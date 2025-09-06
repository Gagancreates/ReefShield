"""
CSV processing utilities for ReefShield backend
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Union
from datetime import datetime, date, timedelta
import logging
from app.models.schemas import TemperatureReading, DataSource

logger = logging.getLogger(__name__)


class CSVProcessor:
    """Utility class for processing CSV files"""
    
    def __init__(self, models_dir: Path):
        """Initialize with models directory path"""
        self.models_dir = Path(models_dir)
    
    def read_csv_safely(self, file_path: Path) -> Optional[pd.DataFrame]:
        """Safely read CSV file with error handling"""
        try:
            if not file_path.exists():
                logger.error(f"CSV file not found: {file_path}")
                return None
            
            df = pd.read_csv(file_path)
            logger.debug(f"Successfully read CSV: {file_path} ({len(df)} rows)")
            return df
            
        except Exception as e:
            logger.error(f"Error reading CSV {file_path}: {e}")
            return None
    
    def validate_csv_format(self, df: pd.DataFrame, required_columns: List[str]) -> bool:
        """Validate that CSV has required columns"""
        if df is None or df.empty:
            return False
        
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            return False
        
        return True
    
    def clean_temperature_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate temperature data"""
        if df is None or df.empty:
            return pd.DataFrame()
        
        # Make a copy to avoid modifying original
        df_clean = df.copy()
        
        # Convert Date column to datetime if needed
        if 'Date' in df_clean.columns:
            df_clean['Date'] = pd.to_datetime(df_clean['Date']).dt.date
        
        # Clean SST values
        if 'SST' in df_clean.columns:
            # Remove invalid values
            df_clean = df_clean.dropna(subset=['SST'])
            # Filter reasonable temperature range (-5 to 50 Celsius)
            df_clean = df_clean[(df_clean['SST'] >= -5.0) & (df_clean['SST'] <= 50.0)]
            # Round to 3 decimal places
            df_clean['SST'] = df_clean['SST'].round(3)
        
        # Remove duplicates based on Date
        if 'Date' in df_clean.columns:
            df_clean = df_clean.drop_duplicates(subset=['Date']).sort_values('Date')
        
        return df_clean.reset_index(drop=True)
    
    def get_last_n_rows(self, file_path: Path, n: int = 7, 
                       required_columns: List[str] = None) -> List[TemperatureReading]:
        """Get last N rows from CSV file as TemperatureReading objects"""
        if required_columns is None:
            required_columns = ['Date', 'SST']
        
        df = self.read_csv_safely(file_path)
        if not self.validate_csv_format(df, required_columns):
            return []
        
        df_clean = self.clean_temperature_data(df)
        if df_clean.empty:
            logger.warning(f"No valid data found in {file_path}")
            return []
        
        # Get last n rows
        last_n = df_clean.tail(n)
        
        readings = []
        for _, row in last_n.iterrows():
            try:
                # Determine data source
                source = DataSource.HISTORICAL
                if 'Source' in row and pd.notna(row['Source']):
                    source_str = str(row['Source']).strip()
                    if source_str.lower() in ['predicted', 'forecast']:
                        source = DataSource.PREDICTED
                    elif source_str.lower() in ['historical', 'observed']:
                        source = DataSource.HISTORICAL
                
                reading = TemperatureReading(
                    date=str(row['Date']),
                    temperature=float(row['SST']),
                    source=source
                )
                readings.append(reading)
                
            except Exception as e:
                logger.warning(f"Error processing row: {row}, error: {e}")
                continue
        
        logger.info(f"Extracted {len(readings)} readings from {file_path}")
        return readings
    
    def get_all_rows(self, file_path: Path, 
                    required_columns: List[str] = None) -> List[TemperatureReading]:
        """Get all rows from CSV file as TemperatureReading objects"""
        if required_columns is None:
            required_columns = ['Date', 'SST']
        
        df = self.read_csv_safely(file_path)
        if not self.validate_csv_format(df, required_columns):
            return []
        
        df_clean = self.clean_temperature_data(df)
        if df_clean.empty:
            logger.warning(f"No valid data found in {file_path}")
            return []
        
        readings = []
        for _, row in df_clean.iterrows():
            try:
                # Determine data source
                source = DataSource.PREDICTED  # Default for prediction files
                if 'Source' in row and pd.notna(row['Source']):
                    source_str = str(row['Source']).strip()
                    if source_str.lower() in ['predicted', 'forecast']:
                        source = DataSource.PREDICTED
                    elif source_str.lower() in ['historical', 'observed']:
                        source = DataSource.HISTORICAL
                
                reading = TemperatureReading(
                    date=str(row['Date']),
                    temperature=float(row['SST']),
                    source=source
                )
                readings.append(reading)
                
            except Exception as e:
                logger.warning(f"Error processing row: {row}, error: {e}")
                continue
        
        logger.info(f"Extracted {len(readings)} readings from {file_path}")
        return readings
    
    def get_combined_14day_data(self, combined_csv_path: Path) -> List[TemperatureReading]:
        """Get combined 14-day data from the combined CSV file"""
        required_columns = ['Date', 'SST', 'Source']
        
        df = self.read_csv_safely(combined_csv_path)
        if not self.validate_csv_format(df, required_columns):
            return []
        
        df_clean = self.clean_temperature_data(df)
        if df_clean.empty:
            logger.warning(f"No valid data found in {combined_csv_path}")
            return []
        
        readings = []
        for _, row in df_clean.iterrows():
            try:
                # Map source string to enum
                source_str = str(row['Source']).strip()
                if source_str.lower() in ['predicted', 'forecast']:
                    source = DataSource.PREDICTED
                elif source_str.lower() in ['historical', 'observed']:
                    source = DataSource.HISTORICAL
                else:
                    source = DataSource.HISTORICAL  # Default fallback
                
                reading = TemperatureReading(
                    date=str(row['Date']),
                    temperature=float(row['SST']),
                    source=source
                )
                readings.append(reading)
                
            except Exception as e:
                logger.warning(f"Error processing row: {row}, error: {e}")
                continue
        
        logger.info(f"Extracted {len(readings)} combined readings from {combined_csv_path}")
        return readings
    
    def calculate_statistics(self, readings: List[TemperatureReading]) -> Dict[str, float]:
        """Calculate basic statistics from temperature readings"""
        if not readings:
            return {}
        
        temperatures = [r.temperature for r in readings]
        
        stats = {
            'min_temp': min(temperatures),
            'max_temp': max(temperatures),
            'avg_temp': sum(temperatures) / len(temperatures),
            'temp_range': max(temperatures) - min(temperatures),
            'count': len(readings)
        }
        
        # Round statistics to 3 decimal places
        return {k: round(v, 3) if isinstance(v, float) else v for k, v in stats.items()}
    
    def assess_risk_level(self, readings: List[TemperatureReading], 
                         threshold: float = 29.0) -> Tuple[str, str, float]:
        """
        Assess risk level based on temperature readings
        Returns: (risk_level, trend, anomaly)
        """
        if not readings:
            return "low", "stable", 0.0
        
        temperatures = [r.temperature for r in readings]
        current_temp = temperatures[-1] if temperatures else threshold
        
        # Calculate anomaly from threshold
        anomaly = current_temp - threshold
        
        # Determine risk level
        if anomaly >= 2.0:
            risk_level = "critical"
        elif anomaly >= 1.0:
            risk_level = "high"
        elif anomaly >= 0.5:
            risk_level = "moderate"
        else:
            risk_level = "low"
        
        # Determine trend (using last 3 readings if available)
        trend = "stable"
        if len(temperatures) >= 3:
            recent_temps = temperatures[-3:]
            temp_diff = recent_temps[-1] - recent_temps[0]
            
            if temp_diff > 0.5:
                trend = "increasing"
            elif temp_diff < -0.5:
                trend = "decreasing"
        
        return risk_level, trend, round(anomaly, 3)
    
    def get_file_info(self, file_path: Path) -> Dict[str, Union[str, int, bool]]:
        """Get information about a CSV file"""
        info = {
            'exists': file_path.exists(),
            'path': str(file_path),
            'size_bytes': 0,
            'row_count': 0,
            'last_modified': None
        }
        
        if file_path.exists():
            try:
                info['size_bytes'] = file_path.stat().st_size
                info['last_modified'] = datetime.fromtimestamp(
                    file_path.stat().st_mtime
                ).isoformat()
                
                df = self.read_csv_safely(file_path)
                if df is not None:
                    info['row_count'] = len(df)
            
            except Exception as e:
                logger.error(f"Error getting file info for {file_path}: {e}")
        
        return info