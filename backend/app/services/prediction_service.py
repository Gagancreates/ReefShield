"""
Service layer for temperature prediction operations.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from ..models.temperature import MultiLocationTemperatureService
from ..models.schemas import (
    LocationTemperatureAnalysis, 
    MultiLocationTemperatureAnalysis,
    CurrentTemperatureData,
    MultiLocationCurrentData,
    TemperatureReading,
    LocationCoordinates
)
from ..config.locations import REEF_LOCATIONS, BLEACHING_THRESHOLD, get_risk_level

logger = logging.getLogger(__name__)


class PredictionService:
    """Main service for handling temperature predictions and analysis."""
    
    def __init__(self):
        self.temp_service = MultiLocationTemperatureService()
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid."""
        if cache_key not in self._cache:
            return False
        
        cached_time = self._cache[cache_key].get("timestamp")
        if not cached_time:
            return False
        
        return (datetime.now() - cached_time).total_seconds() < self._cache_ttl
    
    def _get_from_cache(self, cache_key: str):
        """Get data from cache if valid."""
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]["data"]
        return None
    
    def _set_cache(self, cache_key: str, data):
        """Store data in cache with timestamp."""
        self._cache[cache_key] = {
            "data": data,
            "timestamp": datetime.now()
        }
    
    async def get_temperature_analysis(self, location_id: Optional[str] = None) -> MultiLocationTemperatureAnalysis:
        """
        Get 14-day temperature analysis for all locations or specific location.
        Returns 7 days past + 7 days future predictions.
        """
        cache_key = f"temp_analysis_{location_id or 'all'}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        try:
            # Determine which locations to process
            if location_id:
                locations = [loc for loc in REEF_LOCATIONS if loc["id"] == location_id]
                if not locations:
                    raise ValueError(f"Location {location_id} not found")
            else:
                locations = REEF_LOCATIONS
            
            # Get predictions for all locations
            predictions = await self.temp_service.predict_all_locations(
                locations, past_days=7, future_days=7
            )
            
            # Convert to response format
            location_analyses = {}
            for loc_id, pred_data in predictions.items():
                location_info = next((loc for loc in REEF_LOCATIONS if loc["id"] == loc_id), None)
                if not location_info:
                    continue
                
                # Convert temperature readings
                past_readings = [
                    TemperatureReading(
                        date=reading["date"],
                        temperature=reading["temperature"],
                        is_predicted=reading["is_predicted"]
                    )
                    for reading in pred_data.get("past_data", [])
                ]
                
                future_readings = [
                    TemperatureReading(
                        date=reading["date"],
                        temperature=reading["temperature"],
                        is_predicted=reading["is_predicted"]
                    )
                    for reading in pred_data.get("future_data", [])
                ]
                
                # Determine risk level
                dhw = pred_data.get("dhw", 0.0)
                risk_level = get_risk_level(dhw)
                
                location_analyses[loc_id] = LocationTemperatureAnalysis(
                    location_id=loc_id,
                    location_name=location_info["name"],
                    past_data=past_readings,
                    future_data=future_readings,
                    bleaching_threshold=BLEACHING_THRESHOLD,
                    current_dhw=dhw,
                    risk_level=risk_level,
                    last_updated=pred_data.get("last_updated", datetime.now())
                )
            
            result = MultiLocationTemperatureAnalysis(
                locations=location_analyses,
                metadata={
                    "total_locations": len(location_analyses),
                    "prediction_window_days": 14,
                    "past_days": 7,
                    "future_days": 7,
                    "bleaching_threshold": BLEACHING_THRESHOLD
                }
            )
            
            self._set_cache(cache_key, result)
            return result
            
        except Exception as e:
            logger.error(f"Error getting temperature analysis: {e}")
            raise
    
    async def get_current_temperature_data(self, location_id: Optional[str] = None) -> MultiLocationCurrentData:
        """Get current temperature and DHW data for locations."""
        cache_key = f"current_temp_{location_id or 'all'}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        try:
            # Get analysis data (which includes current temperature)
            analysis = await self.get_temperature_analysis(location_id)
            
            current_data = {}
            for loc_id, loc_analysis in analysis.locations.items():
                location_info = next((loc for loc in REEF_LOCATIONS if loc["id"] == loc_id), None)
                if not location_info:
                    continue
                
                # Get current temperature (last item in past_data)
                current_temp = 0.0
                if loc_analysis.past_data:
                    current_temp = loc_analysis.past_data[-1].temperature
                
                current_data[loc_id] = CurrentTemperatureData(
                    location_id=loc_id,
                    current_temp=current_temp,
                    dhw=loc_analysis.current_dhw,
                    risk_level=loc_analysis.risk_level,
                    coordinates=LocationCoordinates(
                        lat=location_info["lat"],
                        lon=location_info["lon"]
                    ),
                    last_updated=loc_analysis.last_updated
                )
            
            result = MultiLocationCurrentData(locations=current_data)
            self._set_cache(cache_key, result)
            return result
            
        except Exception as e:
            logger.error(f"Error getting current temperature data: {e}")
            raise
    
    async def retrain_models(self, location_id: Optional[str] = None) -> Dict[str, any]:
        """Retrain models for all locations or specific location."""
        try:
            # Clear relevant cache entries
            if location_id:
                cache_keys_to_clear = [k for k in self._cache.keys() if location_id in k]
                locations_to_retrain = [loc for loc in REEF_LOCATIONS if loc["id"] == location_id]
                if not locations_to_retrain:
                    raise ValueError(f"Location {location_id} not found")
            else:
                cache_keys_to_clear = list(self._cache.keys())
                locations_to_retrain = REEF_LOCATIONS
            
            # Clear cache
            for key in cache_keys_to_clear:
                self._cache.pop(key, None)
            
            # Clear model cache to force retraining
            if location_id:
                self.temp_service.models.pop(location_id, None)
            else:
                self.temp_service.models.clear()
            
            # Trigger retraining by running predictions
            await self.temp_service.predict_all_locations(locations_to_retrain)
            
            return {
                "status": "success",
                "message": f"Models retrained successfully",
                "locations_processed": len(locations_to_retrain),
                "location_id": location_id if location_id else None
            }
            
        except Exception as e:
            logger.error(f"Error retraining models: {e}")
            return {
                "status": "error",
                "message": f"Failed to retrain models: {str(e)}",
                "locations_processed": 0,
                "location_id": location_id if location_id else None
            }
    
    def get_locations(self) -> List[Dict]:
        """Get list of all monitored reef locations."""
        return [
            {
                "id": loc["id"],
                "name": loc["name"],
                "coordinates": {
                    "lat": loc["lat"],
                    "lon": loc["lon"]
                },
                "description": loc["description"]
            }
            for loc in REEF_LOCATIONS
        ]