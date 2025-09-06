"""
Pydantic models for API request/response schemas.
"""
from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class LocationCoordinates(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    lon: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")


class ReefLocation(BaseModel):
    id: str = Field(..., description="Unique location identifier")
    name: str = Field(..., description="Human-readable location name")
    coordinates: LocationCoordinates
    description: str = Field(..., description="Location description")


class TemperatureReading(BaseModel):
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    temperature: float = Field(..., description="Sea surface temperature in Celsius")
    is_predicted: bool = Field(..., description="Whether this is a predicted value")


class LocationTemperatureAnalysis(BaseModel):
    location_id: str = Field(..., description="Location identifier")
    location_name: str = Field(..., description="Location name")
    past_data: List[TemperatureReading] = Field(..., description="Historical temperature data")
    future_data: List[TemperatureReading] = Field(..., description="Predicted temperature data")
    bleaching_threshold: float = Field(..., description="Coral bleaching threshold temperature")
    current_dhw: float = Field(..., description="Current Degree Heating Weeks value")
    risk_level: str = Field(..., description="Current bleaching risk level")
    last_updated: datetime = Field(..., description="When this analysis was generated")


class MultiLocationTemperatureAnalysis(BaseModel):
    locations: Dict[str, LocationTemperatureAnalysis] = Field(..., description="Temperature analysis per location")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    generated_at: datetime = Field(default_factory=datetime.now, description="When this analysis was generated")


class CurrentTemperatureData(BaseModel):
    location_id: str = Field(..., description="Location identifier")
    current_temp: float = Field(..., description="Current temperature in Celsius")
    dhw: float = Field(..., description="Current Degree Heating Weeks")
    risk_level: str = Field(..., description="Current risk level")
    coordinates: LocationCoordinates
    last_updated: datetime = Field(..., description="When this data was last updated")


class MultiLocationCurrentData(BaseModel):
    locations: Dict[str, CurrentTemperatureData] = Field(..., description="Current data per location")
    generated_at: datetime = Field(default_factory=datetime.now, description="When this data was generated")


class ApiResponse(BaseModel):
    status: str = Field(..., description="Response status")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(None, description="Response data")


class RetrainResponse(BaseModel):
    status: str = Field(..., description="Retraining status")
    message: str = Field(..., description="Status message")
    locations_processed: Optional[int] = Field(None, description="Number of locations processed")
    location_id: Optional[str] = Field(None, description="Specific location ID if single location retrain")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")