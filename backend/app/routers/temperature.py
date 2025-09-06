"""
Temperature API endpoints for reef monitoring system.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
import logging

from ..services.prediction_service import PredictionService
from ..models.schemas import (
    MultiLocationTemperatureAnalysis,
    LocationTemperatureAnalysis,
    MultiLocationCurrentData,
    CurrentTemperatureData,
    RetrainResponse,
    ApiResponse,
    ErrorResponse
)
from ..config.locations import REEF_LOCATIONS

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/temperature", tags=["temperature"])
prediction_service = PredictionService()


@router.get("/analysis", response_model=MultiLocationTemperatureAnalysis)
async def get_temperature_analysis():
    """
    Get 14-day temperature analysis for all reef locations.
    Returns 7 days past + 7 days future predictions.
    """
    try:
        result = await prediction_service.get_temperature_analysis()
        return result
    except Exception as e:
        logger.error(f"Error in get_temperature_analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis/{location_id}", response_model=LocationTemperatureAnalysis)
async def get_location_temperature_analysis(location_id: str):
    """
    Get 14-day temperature analysis for specific reef location.
    Returns 7 days past + 7 days future predictions.
    """
    try:
        # Validate location exists
        if not any(loc["id"] == location_id for loc in REEF_LOCATIONS):
            raise HTTPException(status_code=404, detail=f"Location {location_id} not found")
        
        result = await prediction_service.get_temperature_analysis(location_id)
        
        if location_id not in result.locations:
            raise HTTPException(status_code=404, detail=f"No data available for location {location_id}")
        
        return result.locations[location_id]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_location_temperature_analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/current", response_model=MultiLocationCurrentData)
async def get_current_temperature_data():
    """
    Get current temperature and DHW analysis for all reef locations.
    """
    try:
        result = await prediction_service.get_current_temperature_data()
        return result
    except Exception as e:
        logger.error(f"Error in get_current_temperature_data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/current/{location_id}", response_model=CurrentTemperatureData)
async def get_location_current_temperature(location_id: str):
    """
    Get current temperature and DHW analysis for specific reef location.
    """
    try:
        # Validate location exists
        if not any(loc["id"] == location_id for loc in REEF_LOCATIONS):
            raise HTTPException(status_code=404, detail=f"Location {location_id} not found")
        
        result = await prediction_service.get_current_temperature_data(location_id)
        
        if location_id not in result.locations:
            raise HTTPException(status_code=404, detail=f"No data available for location {location_id}")
        
        return result.locations[location_id]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_location_current_temperature: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/locations")
async def get_locations():
    """
    Get list of all monitored reef locations.
    """
    try:
        locations = prediction_service.get_locations()
        return {"locations": locations}
    except Exception as e:
        logger.error(f"Error in get_locations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/retrain", response_model=RetrainResponse)
async def retrain_all_models(background_tasks: BackgroundTasks):
    """
    Trigger model retraining for all locations (admin endpoint).
    Runs in background to avoid timeout.
    """
    try:
        # Run retraining in background
        background_tasks.add_task(prediction_service.retrain_models)
        
        return RetrainResponse(
            status="accepted",
            message="Model retraining started for all locations",
            locations_processed=len(REEF_LOCATIONS)
        )
    except Exception as e:
        logger.error(f"Error in retrain_all_models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/retrain/{location_id}", response_model=RetrainResponse)
async def retrain_location_model(location_id: str, background_tasks: BackgroundTasks):
    """
    Trigger model retraining for specific location (admin endpoint).
    Runs in background to avoid timeout.
    """
    try:
        # Validate location exists
        if not any(loc["id"] == location_id for loc in REEF_LOCATIONS):
            raise HTTPException(status_code=404, detail=f"Location {location_id} not found")
        
        # Run retraining in background
        background_tasks.add_task(prediction_service.retrain_models, location_id)
        
        return RetrainResponse(
            status="accepted",
            message=f"Model retraining started for location {location_id}",
            locations_processed=1,
            location_id=location_id
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in retrain_location_model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "temperature-prediction",
        "locations_configured": len(REEF_LOCATIONS),
        "timestamp": prediction_service.temp_service.models.keys() if prediction_service.temp_service.models else []
    }