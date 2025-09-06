"""
Data service for handling CSV operations and data processing
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path

from app.models.schemas import (
    TemperatureReading, 
    ReefLocationData, 
    CombinedTemperatureData,
    LocationCoordinates,
    RiskAssessment,
    DataSource,
    RiskLevel
)
from app.utils.csv_reader import CSVProcessor
from config import settings

logger = logging.getLogger(__name__)


class DataService:
    """Service for handling coral reef temperature data operations"""
    
    def __init__(self, models_path: Optional[Path] = None):
        """Initialize DataService with models directory path"""
        self.models_path = models_path or settings.MODELS_DIR
        self.csv_processor = CSVProcessor(self.models_path)
        
        # Cache for storing processed data
        self._cache = {}
        self._cache_timestamp = None
        self._cache_duration = timedelta(minutes=5)  # Cache for 5 minutes
        
        logger.info(f"DataService initialized with models path: {self.models_path}")
    
    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid"""
        if self._cache_timestamp is None:
            return False
        
        return datetime.now() - self._cache_timestamp < self._cache_duration
    
    def _update_cache(self, key: str, data: any) -> None:
        """Update cache with new data"""
        self._cache[key] = data
        self._cache_timestamp = datetime.now()
        logger.debug(f"Cache updated for key: {key}")
    
    def get_last_8_historical(self, use_cache: bool = True) -> List[TemperatureReading]:
        """
        Get last 8 rows from andaman_sst_recent_filled.csv (historical data)
        """
        cache_key = "last_8_historical"
        
        if use_cache and self._is_cache_valid() and cache_key in self._cache:
            logger.debug("Returning cached historical data")
            return self._cache[cache_key]
        
        file_path = settings.historical_csv_path
        logger.info(f"Reading last 8 historical records from: {file_path}")
        
        readings = self.csv_processor.get_last_n_rows(
            file_path=file_path,
            n=8,
            required_columns=['Date', 'SST']
        )
        
        # Ensure all readings are marked as historical
        for reading in readings:
            reading.source = DataSource.HISTORICAL
        
        self._update_cache(cache_key, readings)
        logger.info(f"Retrieved {len(readings)} historical temperature readings")
        
        return readings
    
    def get_all_predictions(self, use_cache: bool = True) -> List[TemperatureReading]:
        """
        Get all rows from andaman_sst_next7_predictions.csv (prediction data)
        """
        cache_key = "all_predictions"
        
        if use_cache and self._is_cache_valid() and cache_key in self._cache:
            logger.debug("Returning cached prediction data")
            return self._cache[cache_key]
        
        file_path = settings.predictions_csv_path
        logger.info(f"Reading prediction data from: {file_path}")
        
        readings = self.csv_processor.get_all_rows(
            file_path=file_path,
            required_columns=['Date', 'SST']
        )
        
        # Ensure all readings are marked as predicted
        for reading in readings:
            reading.source = DataSource.PREDICTED
        
        self._update_cache(cache_key, readings)
        logger.info(f"Retrieved {len(readings)} prediction temperature readings")
        
        return readings
    
    def get_combined_14day_data(self, use_cache: bool = True) -> List[TemperatureReading]:
        """
        Get combined 14-day data from andaman_sst_14day_combined.csv
        """
        cache_key = "combined_14day"
        
        if use_cache and self._is_cache_valid() and cache_key in self._cache:
            logger.debug("Returning cached combined data")
            return self._cache[cache_key]
        
        file_path = settings.combined_14day_csv_path
        logger.info(f"Reading combined 14-day data from: {file_path}")
        
        readings = self.csv_processor.get_combined_14day_data(file_path)
        
        self._update_cache(cache_key, readings)
        logger.info(f"Retrieved {len(readings)} combined temperature readings")
        
        return readings
    
    def calculate_risk_assessment(self, readings: List[TemperatureReading]) -> RiskAssessment:
        """Calculate risk assessment based on temperature readings"""
        if not readings:
            return RiskAssessment(
                current_risk=RiskLevel.LOW,
                trend="stable",
                dhw=0.0,
                anomaly=0.0
            )
        
        # Get risk level, trend, and anomaly from CSV processor
        risk_level_str, trend, anomaly = self.csv_processor.assess_risk_level(
            readings, threshold=29.0
        )
        
        # Convert risk level string to enum
        risk_level = RiskLevel.LOW  # Default
        try:
            risk_level = RiskLevel(risk_level_str)
        except ValueError:
            logger.warning(f"Unknown risk level: {risk_level_str}, defaulting to LOW")
        
        # Calculate DHW (Degree Heating Weeks) - simplified calculation
        dhw = self._calculate_dhw(readings)
        
        return RiskAssessment(
            current_risk=risk_level,
            trend=trend,
            dhw=dhw,
            anomaly=anomaly,
            bleaching_threshold=29.0
        )
    
    def _calculate_dhw(self, readings: List[TemperatureReading], threshold: float = 29.0) -> float:
        """Calculate Degree Heating Weeks (DHW) - simplified version"""
        if not readings:
            return 0.0
        
        # Take the last 12 weeks (84 days) worth of data if available
        recent_readings = readings[-84:] if len(readings) > 84 else readings
        
        # Calculate hotspots (temperatures above threshold)
        hotspots = []
        for reading in recent_readings:
            if reading.temperature > threshold:
                hotspot = reading.temperature - threshold
                if hotspot >= 1.0:  # Only count significant hotspots
                    hotspots.append(hotspot)
        
        # DHW is the sum of weekly hotspots
        dhw = sum(hotspots) / 7.0  # Convert daily to weekly
        return round(dhw, 1)
    
    def combine_data(self, use_cache: bool = True) -> ReefLocationData:
        """Combine historical and prediction data into a complete reef dataset"""
        cache_key = "combined_reef_data"
        
        if use_cache and self._is_cache_valid() and cache_key in self._cache:
            logger.debug("Returning cached combined reef data")
            return self._cache[cache_key]
        
        try:
            # Get historical and prediction data
            historical_data = self.get_last_8_historical(use_cache=use_cache)
            predictions = self.get_all_predictions(use_cache=use_cache)
            
            # Combine for risk assessment (use all available data)
            all_readings = historical_data + predictions
            risk_assessment = self.calculate_risk_assessment(all_readings)
            
            # Create combined reef data
            reef_data = ReefLocationData(
                location_name=settings.REEF_LOCATION["name"],
                coordinates=LocationCoordinates(
                    lat=settings.REEF_LOCATION["coordinates"]["lat"],
                    lon=settings.REEF_LOCATION["coordinates"]["lon"]
                ),
                last_updated=datetime.now().isoformat() + "Z",
                historical_data=historical_data,
                predictions=predictions,
                risk_assessment=risk_assessment
            )
            
            self._update_cache(cache_key, reef_data)
            logger.info(f"Combined reef data created with {len(historical_data)} historical + {len(predictions)} predicted readings")
            
            return reef_data
            
        except Exception as e:
            logger.error(f"Error combining reef data: {e}")
            raise
    
    def get_combined_temperature_data(self, use_cache: bool = True) -> CombinedTemperatureData:
        """Get combined 14-day temperature data in simplified format"""
        cache_key = "combined_temperature_data"
        
        if use_cache and self._is_cache_valid() and cache_key in self._cache:
            logger.debug("Returning cached combined temperature data")
            return self._cache[cache_key]
        
        try:
            # Get combined 14-day data
            readings = self.get_combined_14day_data(use_cache=use_cache)
            
            combined_data = CombinedTemperatureData(
                location_name=settings.REEF_LOCATION["name"],
                coordinates=LocationCoordinates(
                    lat=settings.REEF_LOCATION["coordinates"]["lat"],
                    lon=settings.REEF_LOCATION["coordinates"]["lon"]
                ),
                last_updated=datetime.now().isoformat() + "Z",
                data=readings
            )
            
            self._update_cache(cache_key, combined_data)
            logger.info(f"Combined temperature data created with {len(readings)} readings")
            
            return combined_data
            
        except Exception as e:
            logger.error(f"Error getting combined temperature data: {e}")
            raise
    
    def get_data_file_status(self) -> Dict[str, Dict]:
        """Get status information for all data files"""
        files_to_check = {
            'historical_csv': settings.historical_csv_path,
            'predictions_csv': settings.predictions_csv_path,
            'combined_14day_csv': settings.combined_14day_csv_path,
            'training_csv': settings.training_csv_path,
        }
        
        status = {}
        for file_key, file_path in files_to_check.items():
            status[file_key] = self.csv_processor.get_file_info(file_path)
        
        logger.debug(f"Retrieved status for {len(status)} data files")
        return status
    
    def clear_cache(self) -> None:
        """Clear all cached data"""
        self._cache.clear()
        self._cache_timestamp = None
        logger.info("Data cache cleared")
    
    def get_cache_info(self) -> Dict[str, any]:
        """Get information about current cache state"""
        return {
            'cached_keys': list(self._cache.keys()),
            'cache_timestamp': self._cache_timestamp.isoformat() if self._cache_timestamp else None,
            'cache_valid': self._is_cache_valid(),
            'cache_size': len(self._cache)
        }