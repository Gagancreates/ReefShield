"""
Configuration settings for ReefShield Backend
"""

import os
from pathlib import Path
from typing import Optional

class Settings:
    """Application settings and configuration"""
    
    # API Configuration
    API_TITLE: str = "ReefShield API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "API for coral reef temperature monitoring and prediction"
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # CORS Configuration
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
    ]
    
    # Paths Configuration
    BASE_DIR: Path = Path(__file__).parent
    MODELS_DIR: Path = BASE_DIR.parent / "models"
    
    # CSV Files Configuration
    HISTORICAL_CSV: str = "andaman_sst_recent_filled.csv"
    PREDICTIONS_CSV: str = "andaman_sst_next7_predictions.csv"
    COMBINED_14DAY_CSV: str = "andaman_sst_14day_combined.csv"
    TRAINING_CSV: str = "andaman_sst_training.csv"
    
    # Model Configuration
    MODEL_SCRIPT: str = "finalig.py"
    HISTORICAL_DAYS_COUNT: int = 8  # Last 8 rows from historical data
    
    # Scheduler Configuration
    MODEL_RUN_HOUR: int = int(os.getenv("MODEL_RUN_HOUR", "6"))  # 6 AM
    MODEL_RUN_MINUTE: int = int(os.getenv("MODEL_RUN_MINUTE", "0"))
    
    # Reef Location Configuration
    REEF_LOCATION: dict = {
        "name": "Andaman Reef",
        "coordinates": {
            "lat": 11.67,
            "lon": 92.75
        }
    }
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Development/Production flags
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    @property
    def historical_csv_path(self) -> Path:
        """Get full path to historical CSV file"""
        return self.MODELS_DIR / self.HISTORICAL_CSV
    
    @property
    def predictions_csv_path(self) -> Path:
        """Get full path to predictions CSV file"""
        return self.MODELS_DIR / self.PREDICTIONS_CSV
    
    @property
    def combined_14day_csv_path(self) -> Path:
        """Get full path to combined 14-day CSV file"""
        return self.MODELS_DIR / self.COMBINED_14DAY_CSV
    
    @property
    def training_csv_path(self) -> Path:
        """Get full path to training CSV file"""
        return self.MODELS_DIR / self.TRAINING_CSV
    
    @property
    def model_script_path(self) -> Path:
        """Get full path to model script"""
        return self.MODELS_DIR / self.MODEL_SCRIPT
    
    def validate_paths(self) -> dict:
        """Validate that required files exist"""
        validation_results = {
            "models_dir_exists": self.MODELS_DIR.exists(),
            "historical_csv_exists": self.historical_csv_path.exists(),
            "predictions_csv_exists": self.predictions_csv_path.exists(),
            "combined_14day_csv_exists": self.combined_14day_csv_path.exists(),
            "model_script_exists": self.model_script_path.exists(),
        }
        return validation_results

# Create global settings instance
settings = Settings()

# Environment file template
ENV_TEMPLATE = """
# ReefShield Backend Environment Configuration

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Model Execution Schedule
MODEL_RUN_HOUR=6
MODEL_RUN_MINUTE=0

# Logging
LOG_LEVEL=INFO

# Environment
DEBUG=True
ENVIRONMENT=development
"""