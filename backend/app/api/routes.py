"""
API routes for ReefShield Backend
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging
from datetime import datetime

from app.services.data_service import DataService
from app.services.model_service import ModelService
from app.services.scheduler_service import SchedulerService
from app.utils.error_handling import get_error_handler
from app.utils.logging_config import get_logging_manager
from app.models.schemas import (
    ReefDataResponse,
    CombinedDataResponse,
    SystemStatus,
    HealthCheckResponse,
    ModelRunRequest,
    ModelRunResponse,
    ErrorResponse
)
from config import settings

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api/v1", tags=["ReefShield API"])

# Service instances
data_service = DataService()
model_service = ModelService()
scheduler_service = None  # Will be injected from main app


def get_data_service() -> DataService:
    """Dependency injection for DataService"""
    return data_service


def get_model_service() -> ModelService:
    """Dependency injection for ModelService"""
    return model_service


def get_scheduler_service() -> SchedulerService:
    """Dependency injection for SchedulerService"""
    from main import get_scheduler_service as get_sched
    return get_sched()


@router.get("/health", response_model=HealthCheckResponse)
async def enhanced_health_check():
    """Enhanced health check with dependency verification"""
    try:
        # Check data service health
        file_status = data_service.get_data_file_status()
        files_healthy = all(
            status.get('exists', False) 
            for status in file_status.values()
        )
        
        # Check model service health
        model_health = await model_service.health_check()
        model_healthy = model_health.get('status') == 'healthy'
        
        # Determine overall health
        overall_status = "healthy"
        if not files_healthy or not model_healthy:
            overall_status = "degraded"
        
        return HealthCheckResponse(
            status=overall_status,
            service="ReefShield Backend",
            version=settings.API_VERSION,
            timestamp=datetime.now().isoformat() + "Z"
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )


@router.get("/reef-data", response_model=ReefDataResponse)
async def get_reef_data(data_svc: DataService = Depends(get_data_service)):
    """
    Get complete reef data including historical temperatures, predictions, and risk assessment
    
    Returns:
    - Last 8 historical temperature readings
    - Next 7 predicted temperature readings  
    - Risk assessment with DHW and trend analysis
    - Location coordinates and metadata
    """
    try:
        logger.info("Fetching complete reef data")
        reef_data = data_svc.combine_data(use_cache=True)
        
        logger.info(
            f"Retrieved reef data: {len(reef_data.historical_data)} historical + "
            f"{len(reef_data.predictions)} predictions, risk: {reef_data.risk_assessment.current_risk}"
        )
        
        return reef_data
        
    except Exception as e:
        logger.error(f"Error fetching reef data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve reef data: {str(e)}"
        )


@router.get("/combined-data", response_model=CombinedDataResponse)  
async def get_combined_data(data_svc: DataService = Depends(get_data_service)):
    """
    Get 14-day combined temperature data (7 historical + 7 predicted)
    
    Returns data from the andaman_sst_14day_combined.csv file with:
    - Date, temperature, and source (Historical/Predicted) for each reading
    - Location metadata and coordinates
    - Last update timestamp
    """
    try:
        logger.info("Fetching 14-day combined temperature data")
        combined_data = data_svc.get_combined_temperature_data(use_cache=True)
        
        logger.info(f"Retrieved combined data: {len(combined_data.data)} readings")
        
        return combined_data
        
    except Exception as e:
        logger.error(f"Error fetching combined data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve combined data: {str(e)}"
        )


@router.get("/status", response_model=SystemStatus)
async def get_system_status(
    data_svc: DataService = Depends(get_data_service),
    model_svc: ModelService = Depends(get_model_service)
):
    """
    Get comprehensive system status including model execution and data file status
    """
    try:
        logger.info("Fetching system status")
        
        # Get model execution status
        model_status = model_svc.get_execution_status()
        
        # Get data files status
        data_files_status = data_svc.get_data_file_status()
        
        # Determine API status based on health checks
        files_healthy = all(
            status.get('exists', False) 
            for status in data_files_status.values()
        )
        
        api_status = "healthy" if files_healthy else "degraded"
        
        # Get last data update time
        last_data_update = None
        try:
            combined_file_info = data_files_status.get('combined_14day_csv', {})
            last_data_update = combined_file_info.get('last_modified')
        except Exception:
            pass
        
        system_status = SystemStatus(
            api_status=api_status,
            model_status=model_status,
            data_files_status=data_files_status,
            last_data_update=last_data_update
        )
        
        logger.info(f"System status: API={api_status}, Model running={model_status.is_running}")
        
        return system_status
        
    except Exception as e:
        logger.error(f"Error fetching system status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve system status: {str(e)}"
        )


@router.post("/run-model", response_model=ModelRunResponse)
async def trigger_model_run(
    request: ModelRunRequest,
    background_tasks: BackgroundTasks,
    model_svc: ModelService = Depends(get_model_service)
):
    """
    Manually trigger model execution
    
    Parameters:
    - force: Force execution even if model was recently run
    - notify: Send notification on completion (placeholder for future implementation)
    """
    try:
        logger.info(f"Model execution requested: force={request.force}, notify={request.notify}")
        
        # Execute model asynchronously
        success, message, execution_id = await model_svc.run_model(force=request.force)
        
        if success:
            logger.info(f"Model execution started successfully: {execution_id}")
            
            # Clear data service cache to force fresh data on next request
            data_service.clear_cache()
            
            return ModelRunResponse(
                success=True,
                message=message,
                execution_id=execution_id,
                estimated_completion=None  # Could be calculated based on historical runs
            )
        else:
            logger.warning(f"Model execution failed: {message}")
            return ModelRunResponse(
                success=False,
                message=message,
                execution_id=execution_id,
                estimated_completion=None
            )
            
    except Exception as e:
        logger.error(f"Error triggering model run: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger model execution: {str(e)}"
        )


@router.get("/cache-info")
async def get_cache_info(data_svc: DataService = Depends(get_data_service)):
    """Get information about data service cache (for debugging)"""
    try:
        cache_info = data_svc.get_cache_info()
        return {
            "cache_info": cache_info,
            "timestamp": datetime.now().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Error getting cache info: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get cache info: {str(e)}"
        )


@router.post("/clear-cache")
async def clear_cache(data_svc: DataService = Depends(get_data_service)):
    """Clear data service cache (for debugging/maintenance)"""
    try:
        data_svc.clear_cache()
        logger.info("Data service cache cleared manually")
        return {
            "message": "Cache cleared successfully",
            "timestamp": datetime.now().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear cache: {str(e)}"
        )


# Error handlers will be added to the main app, not the router


# =================== SCHEDULER ENDPOINTS ===================

@router.get("/scheduler/status")
async def get_scheduler_status(scheduler_svc: SchedulerService = Depends(get_scheduler_service)):
    """Get current scheduler status and job information"""
    try:
        status = scheduler_svc.get_scheduler_status()
        logger.debug("Retrieved scheduler status")
        
        return {
            "status": "success",
            "scheduler": status,
            "timestamp": datetime.now().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get scheduler status: {str(e)}"
        )


@router.get("/scheduler/history")
async def get_job_history(
    limit: int = 10,
    scheduler_svc: SchedulerService = Depends(get_scheduler_service)
):
    """Get recent job execution history"""
    try:
        if limit < 1 or limit > 50:
            raise HTTPException(
                status_code=400,
                detail="Limit must be between 1 and 50"
            )
        
        history = scheduler_svc.get_job_history(limit=limit)
        logger.debug(f"Retrieved {len(history)} job history entries")
        
        return {
            "status": "success",
            "history": history,
            "count": len(history),
            "timestamp": datetime.now().isoformat() + "Z"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get job history: {str(e)}"
        )


@router.post("/scheduler/trigger")
async def trigger_immediate_run(
    user_id: str = None,
    scheduler_svc: SchedulerService = Depends(get_scheduler_service)
):
    """Trigger an immediate model run outside of the schedule"""
    try:
        logger.info(f"Manual model run triggered by user: {user_id}")
        
        job_result = await scheduler_svc.trigger_immediate_run(user_id=user_id)
        
        return {
            "status": "success",
            "message": "Model execution triggered",
            "job_result": job_result,
            "timestamp": datetime.now().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Error triggering immediate run: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger model run: {str(e)}"
        )


@router.post("/scheduler/reschedule")
async def reschedule_daily_run(
    hour: int,
    minute: int = 0,
    scheduler_svc: SchedulerService = Depends(get_scheduler_service)
):
    """Reschedule the daily model run to a new time"""
    try:
        if not (0 <= hour <= 23) or not (0 <= minute <= 59):
            raise HTTPException(
                status_code=400,
                detail="Invalid time: hour must be 0-23, minute must be 0-59"
            )
        
        success = await scheduler_svc.reschedule_daily_run(hour, minute)
        
        if success:
            return {
                "status": "success",
                "message": f"Daily run rescheduled to {hour:02d}:{minute:02d} UTC",
                "new_schedule": f"{hour:02d}:{minute:02d}",
                "timestamp": datetime.now().isoformat() + "Z"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to reschedule daily run"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rescheduling daily run: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reschedule: {str(e)}"
        )


@router.post("/scheduler/pause")
async def pause_scheduler(scheduler_svc: SchedulerService = Depends(get_scheduler_service)):
    """Pause the scheduler (stop accepting new jobs)"""
    try:
        success = await scheduler_svc.pause_scheduler()
        
        if success:
            return {
                "status": "success",
                "message": "Scheduler paused successfully",
                "timestamp": datetime.now().isoformat() + "Z"
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Scheduler is not running or already paused"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error pausing scheduler: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to pause scheduler: {str(e)}"
        )


@router.post("/scheduler/resume")
async def resume_scheduler(scheduler_svc: SchedulerService = Depends(get_scheduler_service)):
    """Resume the paused scheduler"""
    try:
        success = await scheduler_svc.resume_scheduler()
        
        if success:
            return {
                "status": "success",
                "message": "Scheduler resumed successfully",
                "timestamp": datetime.now().isoformat() + "Z"
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Scheduler is not running or not paused"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resuming scheduler: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to resume scheduler: {str(e)}"
        )


# =================== ERROR HANDLING ENDPOINTS ===================

@router.get("/errors/stats")
async def get_error_statistics():
    """Get error statistics and recent error information"""
    try:
        error_handler = get_error_handler()
        stats = error_handler.get_error_stats()
        
        return {
            "status": "success",
            "error_statistics": stats,
            "timestamp": datetime.now().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Error getting error statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get error statistics: {str(e)}"
        )


# =================== LOGGING ENDPOINTS ===================

@router.get("/logs/stats")
async def get_logging_statistics():
    """Get logging system statistics and configuration"""
    try:
        logging_manager = get_logging_manager()
        stats = logging_manager.get_log_stats()
        
        return {
            "status": "success",
            "logging_statistics": stats,
            "timestamp": datetime.now().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Error getting logging statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get logging statistics: {str(e)}"
        )