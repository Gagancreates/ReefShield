#!/usr/bin/env python3
"""
Daily SST Forecasting System for Andaman Reef
Designed to run as a daily cron job (e.g., 6 AM every day)

Usage: python daily_sst_forecaster.py
Cron example: 0 6 * * * /usr/bin/python3 /path/to/daily_sst_forecaster.py
"""

import datetime as dt
import pandas as pd
import numpy as np
import xarray as xr
import joblib
import os
import logging
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

# =================== CONFIG ===================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "sst_data"
MODEL_DIR = BASE_DIR / "models"
LOG_DIR = BASE_DIR / "logs"

# Create directories
for dir_path in [DATA_DIR, MODEL_DIR, LOG_DIR]:
    dir_path.mkdir(exist_ok=True)

# Reef coordinates
LAT, LON = 11.67, 92.75

# Model parameters
LOOKBACK_DAYS = 14      # Use last 14 days to predict next 7
FORECAST_DAYS = 7       # Always predict next 7 days
RETRAIN_DAYS = 30       # Retrain model every 30 days
MIN_HISTORY_DAYS = 60   # Minimum days needed for reliable prediction

# File paths
FORECAST_DB = DATA_DIR / "sst_forecasts.csv"
OBSERVED_DB = DATA_DIR / "sst_observed.csv" 
MODEL_FILE = MODEL_DIR / "sst_forecaster.joblib"
RETRAIN_FLAG = MODEL_DIR / "last_retrain_date.txt"

# Training data range
START_YEAR = 1982
CURRENT_YEAR = dt.date.today().year

# =================== LOGGING SETUP ===================
def setup_logging():
    """Setup logging for cron job monitoring"""
    log_file = LOG_DIR / f"sst_forecast_{dt.date.today()}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Also print to console
        ]
    )
    return logging.getLogger(__name__)

# =================== DATA FETCHING ===================
def fetch_sst_range(lat, lon, start_date: dt.date, end_date: dt.date) -> pd.DataFrame:
    """
    Fetch OISST data for date range. Robust error handling for cron jobs.
    """
    logger = logging.getLogger(__name__)
    pieces = []
    
    for year in range(start_date.year, end_date.year + 1):
        url = f"https://psl.noaa.gov/thredds/dodsC/Datasets/noaa.oisst.v2.highres/sst.day.mean.{year}.nc"
        
        try:
            logger.info(f"Fetching data for year {year}")
            # Try different engines for robustness
            engines_to_try = ['netcdf4', 'pydap', 'h5netcdf']
            
            ds = None
            for engine in engines_to_try:
                try:
                    ds = xr.open_dataset(url, engine=engine)
                    logger.info(f"Successfully connected using {engine} engine")
                    break
                except Exception as engine_error:
                    logger.debug(f"Engine {engine} failed: {engine_error}")
                    continue
            
            if ds is None:
                raise Exception("All connection engines failed")
            
            sst_data = ds["sst"].sel(time=slice(str(start_date), str(end_date)))
            sst_point = sst_data.sel(lat=lat, lon=lon, method="nearest")
            df = sst_point.to_dataframe().reset_index()[["time", "sst"]]
            pieces.append(df)
            ds.close()  # Clean up
            
        except Exception as e:
            logger.warning(f"Failed to fetch {year}: {e}")
            continue
    
    if not pieces:
        logger.error("No data fetched from any year - check internet connection and dependencies")
        logger.error("Required: pip install netcdf4")
        return pd.DataFrame(columns=["Date", "SST"])
    
    result = pd.concat(pieces, ignore_index=True)
    result = result.rename(columns={"time": "Date", "sst": "SST"})
    result["Date"] = pd.to_datetime(result["Date"]).dt.date
    result = result.dropna(subset=["SST"]).drop_duplicates("Date").sort_values("Date")
    
    logger.info(f"Fetched {len(result)} data points from {result['Date'].min()} to {result['Date'].max()}")
    return result[["Date", "SST"]].reset_index(drop=True)

def update_observed_data():
    """
    Update observed SST database with latest available data
    """
    logger = logging.getLogger(__name__)
    today = dt.date.today()
    
    # Load existing observed data
    if OBSERVED_DB.exists():
        observed_df = pd.read_csv(OBSERVED_DB)
        observed_df['Date'] = pd.to_datetime(observed_df['Date']).dt.date
        last_obs_date = observed_df['Date'].max()
        fetch_start = last_obs_date + dt.timedelta(days=1)
    else:
        # First time - get last 90 days
        fetch_start = today - dt.timedelta(days=90)
        observed_df = pd.DataFrame(columns=['Date', 'SST'])
    
    # Fetch new data (up to yesterday, since today might not be available yet)
    fetch_end = today - dt.timedelta(days=1)
    
    if fetch_start <= fetch_end:
        logger.info(f"Updating observed data from {fetch_start} to {fetch_end}")
        new_data = fetch_sst_range(LAT, LON, fetch_start, fetch_end)
        
        if not new_data.empty:
            # Combine and save
            updated_df = pd.concat([observed_df, new_data], ignore_index=True)
            updated_df = updated_df.drop_duplicates('Date').sort_values('Date')
            
            # Keep only last 365 days to prevent file from growing too large
            cutoff_date = today - dt.timedelta(days=365)
            updated_df = updated_df[updated_df['Date'] >= cutoff_date]
            
            updated_df.to_csv(OBSERVED_DB, index=False)
            logger.info(f"Updated observed database: {len(new_data)} new records")
            return updated_df
        else:
            logger.warning("No new observed data available")
    else:
        logger.info("Observed data is already up to date")
        
    return observed_df

# =================== FEATURE ENGINEERING ===================
def add_cyclical_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add cyclical time features"""
    df = df.copy()
    df['Date_dt'] = pd.to_datetime(df['Date'])
    
    # Day of year
    df['day_of_year'] = df['Date_dt'].dt.dayofyear
    df['day_sin'] = np.sin(2 * np.pi * df['day_of_year'] / 365.25)
    df['day_cos'] = np.cos(2 * np.pi * df['day_of_year'] / 365.25)
    
    # Month
    df['month'] = df['Date_dt'].dt.month
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    
    return df

def create_training_features(sst_data: pd.DataFrame, lookback=LOOKBACK_DAYS, forecast=FORECAST_DAYS):
    """
    Create training dataset from historical SST data
    """
    logger = logging.getLogger(__name__)
    
    sst_data = sst_data.sort_values('Date').reset_index(drop=True)
    sst_data = add_cyclical_features(sst_data)
    
    samples = []
    
    for i in range(lookback, len(sst_data) - forecast + 1):
        # Input features: last `lookback` days
        input_window = sst_data.iloc[i-lookback:i]
        target_window = sst_data.iloc[i:i+forecast]
        
        # Skip if any missing data
        if input_window['SST'].isna().any() or target_window['SST'].isna().any():
            continue
        
        sample = {'forecast_start_date': target_window['Date'].iloc[0]}
        
        # SST lag features
        for j, sst_val in enumerate(input_window['SST'].values):
            sample[f'sst_lag_{lookback-j}'] = float(sst_val)
        
        # Cyclical time features from forecast start date
        start_row = target_window.iloc[0]
        sample['day_sin'] = float(start_row['day_sin'])
        sample['day_cos'] = float(start_row['day_cos'])
        sample['month_sin'] = float(start_row['month_sin'])
        sample['month_cos'] = float(start_row['month_cos'])
        
        # Target values
        for j, sst_val in enumerate(target_window['SST'].values):
            sample[f'target_day_{j+1}'] = float(sst_val)
        
        samples.append(sample)
    
    result_df = pd.DataFrame(samples)
    logger.info(f"Created {len(result_df)} training samples")
    return result_df

# =================== MODEL TRAINING ===================
def train_forecast_models(training_df: pd.DataFrame):
    """
    Train separate RandomForest models for each forecast day
    """
    logger = logging.getLogger(__name__)
    
    feature_cols = [f'sst_lag_{i}' for i in range(LOOKBACK_DAYS, 0, -1)]
    feature_cols += ['day_sin', 'day_cos', 'month_sin', 'month_cos']
    
    X = training_df[feature_cols].values
    models = {}
    
    for day in range(1, FORECAST_DAYS + 1):
        logger.info(f"Training model for forecast day {day}")
        
        y = training_df[f'target_day_{day}'].values
        
        model = RandomForestRegressor(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1  # Use all CPU cores
        )
        model.fit(X, y)
        
        # Quick validation
        y_pred = model.predict(X)
        rmse = np.sqrt(mean_squared_error(y, y_pred))
        logger.info(f"Day {day} model training RMSE: {rmse:.3f}°C")
        
        models[f'day_{day}'] = model
    
    # Save models and feature columns
    model_data = {
        'models': models,
        'feature_cols': feature_cols,
        'training_date': dt.date.today(),
        'n_samples': len(training_df)
    }
    
    joblib.dump(model_data, MODEL_FILE)
    logger.info(f"Saved models to {MODEL_FILE}")
    
    return models, feature_cols

def should_retrain_model():
    """
    Check if model needs retraining (every RETRAIN_DAYS)
    """
    if not MODEL_FILE.exists() or not RETRAIN_FLAG.exists():
        return True
    
    try:
        with open(RETRAIN_FLAG, 'r') as f:
            last_retrain = dt.datetime.strptime(f.read().strip(), '%Y-%m-%d').date()
        
        days_since_retrain = (dt.date.today() - last_retrain).days
        return days_since_retrain >= RETRAIN_DAYS
    except:
        return True

def load_or_train_models(observed_data: pd.DataFrame):
    """
    Load existing models or retrain if necessary
    """
    logger = logging.getLogger(__name__)
    
    if should_retrain_model():
        logger.info("Retraining models...")
        
        # Get historical training data
        start_date = dt.date(START_YEAR, 1, 1)
        end_date = dt.date.today() - dt.timedelta(days=1)
        
        # Use observed data + fetch more historical data if needed
        if observed_data['Date'].min() > start_date:
            logger.info("Fetching additional historical data for training")
            historical_data = fetch_sst_range(LAT, LON, start_date, observed_data['Date'].min())
            all_data = pd.concat([historical_data, observed_data], ignore_index=True)
            all_data = all_data.drop_duplicates('Date').sort_values('Date')
        else:
            all_data = observed_data
        
        # Create training features
        training_df = create_training_features(all_data)
        
        if len(training_df) < 100:
            raise ValueError("Insufficient training data")
        
        # Train models
        models, feature_cols = train_forecast_models(training_df)
        
        # Update retrain flag
        with open(RETRAIN_FLAG, 'w') as f:
            f.write(dt.date.today().strftime('%Y-%m-%d'))
        
        logger.info("Model retraining completed")
        
    else:
        logger.info("Loading existing models")
        model_data = joblib.load(MODEL_FILE)
        models = model_data['models']
        feature_cols = model_data['feature_cols']
    
    return models, feature_cols

# =================== FORECASTING ===================
def make_daily_forecast(models, feature_cols, observed_data: pd.DataFrame):
    """
    Generate 7-day forecast starting from today
    """
    logger = logging.getLogger(__name__)
    today = dt.date.today()
    
    # Get recent data for features
    observed_data = observed_data.sort_values('Date')
    
    if len(observed_data) < LOOKBACK_DAYS:
        raise ValueError(f"Need at least {LOOKBACK_DAYS} days of observed data")
    
    # Use most recent LOOKBACK_DAYS for prediction
    recent_data = observed_data.tail(LOOKBACK_DAYS).copy()
    recent_data = add_cyclical_features(recent_data)
    
    # Create feature vector
    features = {}
    
    # SST lag features
    for i, sst_val in enumerate(recent_data['SST'].values):
        features[f'sst_lag_{LOOKBACK_DAYS-i}'] = float(sst_val)
    
    # Time features for today
    temp_df = pd.DataFrame({'Date': [today]})
    temp_df = add_cyclical_features(temp_df)
    features['day_sin'] = float(temp_df['day_sin'].iloc[0])
    features['day_cos'] = float(temp_df['day_cos'].iloc[0])
    features['month_sin'] = float(temp_df['month_sin'].iloc[0])
    features['month_cos'] = float(temp_df['month_cos'].iloc[0])
    
    X = np.array([features[col] for col in feature_cols]).reshape(1, -1)
    
    # Generate forecasts
    forecasts = []
    for day in range(1, FORECAST_DAYS + 1):
        forecast_date = today + dt.timedelta(days=day-1)
        predicted_sst = float(models[f'day_{day}'].predict(X)[0])
        
        forecasts.append({
            'Date': forecast_date,
            'SST_Forecast': predicted_sst,
            'Forecast_Day': day,
            'Issue_Date': today,
            'Issue_Time': dt.datetime.now()
        })
    
    logger.info(f"Generated {len(forecasts)} daily forecasts")
    return pd.DataFrame(forecasts)

def update_forecast_database(new_forecasts: pd.DataFrame):
    """
    Update the forecast database with new predictions
    """
    logger = logging.getLogger(__name__)
    
    if FORECAST_DB.exists():
        # Load existing forecasts
        existing_df = pd.read_csv(FORECAST_DB)
        existing_df['Date'] = pd.to_datetime(existing_df['Date']).dt.date
        existing_df['Issue_Date'] = pd.to_datetime(existing_df['Issue_Date']).dt.date
        
        # Remove old forecasts for the same dates (keep most recent)
        today = dt.date.today()
        existing_df = existing_df[~((existing_df['Date'].isin(new_forecasts['Date'])) & 
                                 (existing_df['Issue_Date'] < today))]
        
        # Combine and clean up
        updated_df = pd.concat([existing_df, new_forecasts], ignore_index=True)
        
        # Keep only recent forecasts (last 60 days)
        cutoff_date = today - dt.timedelta(days=60)
        updated_df = updated_df[updated_df['Date'] >= cutoff_date]
        
    else:
        updated_df = new_forecasts
    
    # Save updated database
    updated_df.to_csv(FORECAST_DB, index=False)
    logger.info(f"Updated forecast database: {len(new_forecasts)} new forecasts")

# =================== MAIN EXECUTION ===================
def main():
    """
    Main function for daily cron execution
    """
    logger = setup_logging()
    logger.info("=== DAILY SST FORECAST SYSTEM STARTED ===")
    
    try:
        # 1. Update observed data
        logger.info("Step 1: Updating observed data")
        observed_data = update_observed_data()
        
        if len(observed_data) < MIN_HISTORY_DAYS:
            raise ValueError(f"Insufficient observed data: {len(observed_data)} days (need {MIN_HISTORY_DAYS})")
        
        # 2. Load or retrain models
        logger.info("Step 2: Loading/training forecast models")
        models, feature_cols = load_or_train_models(observed_data)
        
        # 3. Generate today's forecast
        logger.info("Step 3: Generating 7-day forecast")
        forecasts = make_daily_forecast(models, feature_cols, observed_data)
        
        # 4. Update forecast database
        logger.info("Step 4: Updating forecast database")
        update_forecast_database(forecasts)
        
        # 5. Log summary
        logger.info("=== FORECAST SUMMARY ===")
        for _, row in forecasts.iterrows():
            logger.info(f"Day {row['Forecast_Day']}: {row['Date']} -> {row['SST_Forecast']:.2f}°C")
        
        logger.info("=== DAILY FORECAST SYSTEM COMPLETED SUCCESSFULLY ===")
        
        return True
        
    except Exception as e:
        logger.error(f"DAILY FORECAST SYSTEM FAILED: {str(e)}")
        logger.exception("Full error traceback:")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)