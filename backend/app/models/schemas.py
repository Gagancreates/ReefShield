"""
Pydantic models and schemas for ReefShield API data validation
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal
from datetime import date, datetime
from enum import Enum


class DataSource(str, Enum):
    """Data source enumeration"""
    HISTORICAL = "Historical"
    PREDICTED = "Predicted"
    OBSERVED = "Observed"
    FORECAST = "Forecast"


class RiskLevel(str, Enum):
    """Risk level enumeration for coral reef health"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class TemperatureReading(BaseModel):
    """Individual temperature reading with metadata"""
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    temperature: float = Field(..., description="Sea surface temperature in Celsius", ge=-5.0, le=50.0)
    source: DataSource = Field(..., description="Source of the data")
    
    @validator('date')
    def validate_date_format(cls, v):
        """Validate date format"""
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')
    
    @validator('temperature')
    def round_temperature(cls, v):
        """Round temperature to 3 decimal places"""
        return round(v, 3)


class LocationCoordinates(BaseModel):
    """Geographic coordinates for reef location"""
    lat: float = Field(..., description="Latitude", ge=-90.0, le=90.0)
    lon: float = Field(..., description="Longitude", ge=-180.0, le=180.0)


class RiskAssessment(BaseModel):
    """Risk assessment for coral reef health"""
    current_risk: RiskLevel = Field(..., description="Current risk level")
    trend: Literal["stable", "increasing", "decreasing"] = Field(..., description="Temperature trend")
    dhw: Optional[float] = Field(None, description="Degree Heating Weeks", ge=0.0)
    anomaly: Optional[float] = Field(None, description="Temperature anomaly in Celsius")
    bleaching_threshold: Optional[float] = Field(29.0, description="Bleaching threshold temperature")
    
    @validator('dhw')
    def round_dhw(cls, v):
        """Round DHW to 1 decimal place"""
        return round(v, 1) if v is not None else None


class ReefLocationData(BaseModel):
    """Complete reef location data including historical and predicted temperatures"""
    location_name: str = Field(..., description="Name of the reef location")
    coordinates: LocationCoordinates = Field(..., description="Geographic coordinates")
    last_updated: str = Field(..., description="Timestamp of last update")
    historical_data: List[TemperatureReading] = Field(..., description="Historical temperature readings")
    predictions: List[TemperatureReading] = Field(..., description="Future temperature predictions")
    risk_assessment: RiskAssessment = Field(..., description="Current risk assessment")
    
    @validator('last_updated')
    def validate_timestamp_format(cls, v):
        """Validate timestamp format"""
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            raise ValueError('Timestamp must be in ISO format')


class CombinedTemperatureData(BaseModel):
    """Combined 14-day temperature data (7 historical + 7 predicted)"""
    location_name: str = Field(..., description="Name of the reef location")
    coordinates: LocationCoordinates = Field(..., description="Geographic coordinates")
    last_updated: str = Field(..., description="Timestamp of last update")
    data: List[TemperatureReading] = Field(..., description="Combined temperature data", min_items=1, max_items=20)
    
    @validator('data')
    def validate_data_order(cls, v):
        """Ensure data is sorted by date"""
        if len(v) <= 1:
            return v
        
        dates = [datetime.strptime(reading.date, '%Y-%m-%d') for reading in v]
        if dates != sorted(dates):
            raise ValueError('Temperature readings must be sorted by date')
        return v


class ModelExecutionStatus(BaseModel):
    """Status of model execution"""
    is_running: bool = Field(..., description="Whether model is currently running")
    last_run: Optional[str] = Field(None, description="Timestamp of last successful run")
    last_error: Optional[str] = Field(None, description="Last error message if any")
    next_scheduled_run: Optional[str] = Field(None, description="Next scheduled run time")


class SystemStatus(BaseModel):
    """Overall system status"""
    api_status: Literal["healthy", "degraded", "down"] = Field(..., description="API status")
    model_status: ModelExecutionStatus = Field(..., description="Model execution status")
    data_files_status: dict = Field(..., description="Status of CSV data files")
    last_data_update: Optional[str] = Field(None, description="Last time data was updated")


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: Literal["healthy", "degraded", "down"] = Field(..., description="Service health status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: str = Field(..., description="Current timestamp")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")
    timestamp: str = Field(..., description="Error timestamp")


class ModelRunRequest(BaseModel):
    """Request to manually trigger model execution"""
    force: bool = Field(False, description="Force run even if recently executed")
    notify: bool = Field(True, description="Send notification on completion")


class ModelRunResponse(BaseModel):
    """Response from model execution request"""
    success: bool = Field(..., description="Whether execution was successful")
    message: str = Field(..., description="Execution message")
    execution_id: Optional[str] = Field(None, description="Unique execution ID")
    estimated_completion: Optional[str] = Field(None, description="Estimated completion time")


class SchedulerJobInfo(BaseModel):
    """Information about a scheduled job"""
    id: str = Field(..., description="Job ID")
    name: str = Field(..., description="Job name")
    next_run_time: Optional[str] = Field(None, description="Next scheduled run time")
    trigger: str = Field(..., description="Trigger description")


class SchedulerStatusResponse(BaseModel):
    """Response for scheduler status"""
    is_running: bool = Field(..., description="Whether scheduler is running")
    jobs: List[SchedulerJobInfo] = Field(..., description="List of scheduled jobs")
    last_job_result: Optional[dict] = Field(None, description="Result of last job execution")
    job_history_count: int = Field(..., description="Number of jobs in history")


class JobHistoryEntry(BaseModel):
    """Single job execution history entry"""
    job_id: str = Field(..., description="Unique job ID")
    execution_id: Optional[str] = Field(None, description="Model execution ID")
    start_time: str = Field(..., description="Job start time")
    end_time: str = Field(..., description="Job end time")
    success: bool = Field(..., description="Whether job was successful")
    message: str = Field(..., description="Job execution message")
    trigger: Literal["scheduled", "manual"] = Field(..., description="How the job was triggered")
    user_id: Optional[str] = Field(None, description="User who triggered manual run")


class JobHistoryResponse(BaseModel):
    """Response for job history endpoint"""
    status: str = Field(..., description="Response status")
    history: List[JobHistoryEntry] = Field(..., description="List of job executions")
    count: int = Field(..., description="Number of entries returned")
    timestamp: str = Field(..., description="Response timestamp")


# Response models for API endpoints
class ReefDataResponse(ReefLocationData):
    """Response model for reef data endpoint"""
    pass


class CombinedDataResponse(CombinedTemperatureData):
    """Response model for combined data endpoint"""
    pass