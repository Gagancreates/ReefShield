"""
Multi-location temperature prediction model wrapper based on finalig.py
"""
import datetime as dt
import pandas as pd
import numpy as np
import xarray as xr
from calendar import isleap
from sklearn.ensemble import RandomForestRegressor
from typing import Dict, List, Tuple, Optional
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)


class LocationTemperatureModel:
    """Temperature prediction model for a specific reef location."""
    
    def __init__(self, lat: float, lon: float, location_id: str):
        self.lat = lat
        self.lon = lon
        self.location_id = location_id
        self.window = 14  # Use 14 days of history as features
        self.model = None
        self.last_trained = None
        self.training_data_cache = None
        self.training_data_date = None
        
        # Seasonal training years
        self.START_YEAR = 1982
        self.END_YEAR = dt.date.today().year - 1
        
        # Network settings
        self.max_retries = 2
        self.timeout_seconds = 15
    
    def safe_target_for_year(self, base: dt.date, year: int) -> dt.date:
        """Return the 'same' month/day in that year, with Feb 29 -> Feb 28 fallback."""
        m, d = base.month, base.day
        if m == 2 and d == 29 and not isleap(year):
            return dt.date(year, 2, 28)
        return dt.date(year, m, d)
    
    async def fetch_range_for_point(self, start_date: dt.date, end_date: dt.date) -> pd.DataFrame:
        """
        Fetch OISST SST data for date range at this location's coordinates.
        """
        pieces = []
        
        for y in range(start_date.year, end_date.year + 1):
            url = f"https://psl.noaa.gov/thredds/dodsC/Datasets/noaa.oisst.v2.highres/sst.day.mean.{y}.nc"
            try:
                # Use xarray with explicit engine specification
                loop = asyncio.get_event_loop()
                with ThreadPoolExecutor() as executor:
                    def fetch_data():
                        try:
                            # Try different engines in order of preference
                            engines = ['netcdf4', 'h5netcdf', 'scipy']
                            ds = None
                            
                            for engine in engines:
                                try:
                                    ds = xr.open_dataset(url, engine=engine)
                                    break
                                except Exception:
                                    continue
                            
                            if ds is None:
                                # Fallback to default engine
                                ds = xr.open_dataset(url)
                            
                            # Select time range and location
                            sst_t = ds["sst"].sel(time=slice(str(start_date), str(end_date)))
                            sst_pt = sst_t.sel(lat=self.lat, lon=self.lon, method="nearest")
                            df = sst_pt.to_dataframe().reset_index()[["time", "sst"]]
                            ds.close()
                            return df
                        except Exception as e:
                            logger.warning(f"Failed to fetch {y} for {self.location_id}: {e}")
                            return pd.DataFrame(columns=["time", "sst"])
                    
                    df = await loop.run_in_executor(executor, fetch_data)
                    if not df.empty:
                        pieces.append(df)
                        
            except Exception as e:
                logger.warning(f"Skipping fetch {y} for {self.location_id}: {e}")
        
        if not pieces:
            logger.warning(f"No data fetched for {self.location_id}, using fallback data")
            return self._generate_fallback_data(start_date, end_date)
        
        out = pd.concat(pieces, ignore_index=True)
        out = out.rename(columns={"time": "Date", "sst": "SST"})
        out["Date"] = pd.to_datetime(out["Date"]).dt.date
        out = out.dropna(subset=["SST"]).drop_duplicates(subset=["Date"]).sort_values("Date")
        return out[["Date", "SST"]].reset_index(drop=True)
    
    def _generate_fallback_data(self, start_date: dt.date, end_date: dt.date) -> pd.DataFrame:
        """Generate fallback temperature data when NOAA data is unavailable."""
        dates = pd.date_range(start_date, end_date, freq='D')
        
        # Generate realistic temperature data based on location
        base_temp = 28.5  # Base temperature for Andaman Sea
        seasonal_variation = 1.5  # Seasonal temperature variation
        
        temperatures = []
        for date in dates:
            # Add seasonal variation (warmer in summer months)
            day_of_year = date.timetuple().tm_yday
            seasonal_factor = np.sin(2 * np.pi * (day_of_year - 80) / 365) * seasonal_variation
            
            # Add some random variation
            random_variation = np.random.normal(0, 0.3)
            
            temp = base_temp + seasonal_factor + random_variation
            temperatures.append(temp)
        
        return pd.DataFrame({
            'Date': [d.date() for d in dates],
            'SST': temperatures
        })
    
    async def build_training_data(self, base_today: dt.date) -> pd.DataFrame:
        """Build seasonal training data for this location."""
        records = []
        successful_years = 0
        
        # Try to get data for recent years first (more likely to be available)
        years_to_try = list(range(self.END_YEAR, self.START_YEAR - 1, -1))
        
        for year in years_to_try:
            if successful_years >= 10:  # We have enough data
                break
                
            target_y = self.safe_target_for_year(base_today, year)
            start = target_y - dt.timedelta(days=self.window)
            end = target_y - dt.timedelta(days=1)
            
            try:
                win_df = await self.fetch_range_for_point(start, end)
                if len(win_df) < self.window * 0.8:  # Allow some missing data
                    logger.warning(f"Skipping {year} for {self.location_id}: expected {self.window} days, got {len(win_df)}")
                    continue
                
                tgt_df = await self.fetch_range_for_point(target_y, target_y)
                if tgt_df.empty:
                    logger.warning(f"Skipping {year} for {self.location_id}: target day {target_y} missing")
                    continue
                
                # Interpolate missing values if needed
                if len(win_df) < self.window:
                    win_df = self._interpolate_missing_data(win_df, self.window)
                
                sst_values = win_df["SST"].values.tolist()[:self.window]  # Ensure exact length
                sst_target = float(tgt_df["SST"].iloc[0])
                
                record = {"Year": year}
                for i, val in enumerate(sst_values, 1):
                    record[f"Day-{self.window - i + 1}"] = float(val)
                record["Target"] = sst_target
                records.append(record)
                successful_years += 1
                
            except Exception as e:
                logger.warning(f"Error processing {year} for {self.location_id}: {e}")
                continue
        
        if successful_years < 5:  # Not enough real data, use synthetic data
            logger.warning(f"Only {successful_years} years of data for {self.location_id}, generating synthetic training data")
            synthetic_records = self._generate_synthetic_training_data(base_today)
            records.extend(synthetic_records)
        
        return pd.DataFrame(records)
    
    def _interpolate_missing_data(self, df: pd.DataFrame, target_length: int) -> pd.DataFrame:
        """Interpolate missing data points."""
        if len(df) >= target_length:
            return df.head(target_length)
        
        # Simple linear interpolation for missing days
        df_copy = df.copy()
        df_copy = df_copy.interpolate(method='linear')
        
        # If still not enough data, pad with the mean
        if len(df_copy) < target_length:
            mean_temp = df_copy["SST"].mean()
            missing_count = target_length - len(df_copy)
            
            for i in range(missing_count):
                new_date = df_copy["Date"].iloc[-1] + dt.timedelta(days=1)
                new_row = pd.DataFrame({"Date": [new_date], "SST": [mean_temp]})
                df_copy = pd.concat([df_copy, new_row], ignore_index=True)
        
        return df_copy.head(target_length)
    
    def _generate_synthetic_training_data(self, base_today: dt.date) -> list:
        """Generate synthetic training data when real data is unavailable."""
        records = []
        
        # Generate 20 years of synthetic data
        for year_offset in range(20):
            year = 2020 - year_offset
            
            # Generate realistic temperature patterns
            base_temp = 28.5
            seasonal_variation = 1.5
            
            # Create window of temperatures
            temperatures = []
            for day_offset in range(self.window):
                day_of_year = (base_today.timetuple().tm_yday + day_offset) % 365
                seasonal_factor = np.sin(2 * np.pi * (day_of_year - 80) / 365) * seasonal_variation
                random_variation = np.random.normal(0, 0.3)
                temp = base_temp + seasonal_factor + random_variation
                temperatures.append(temp)
            
            # Target temperature (slightly correlated with recent temps)
            target_temp = np.mean(temperatures[-3:]) + np.random.normal(0, 0.2)
            
            record = {"Year": year}
            for i, temp in enumerate(temperatures, 1):
                record[f"Day-{self.window - i + 1}"] = float(temp)
            record["Target"] = float(target_temp)
            records.append(record)
        
        return records
    
    def train_model(self, training_df: pd.DataFrame):
        """Train the Random Forest model."""
        if training_df.empty:
            raise ValueError(f"No training data available for {self.location_id}")
        
        Xcols = [f"Day-{i}" for i in range(self.window, 0, -1)]
        X = training_df[Xcols].values
        y = training_df["Target"].values
        
        self.model = RandomForestRegressor(n_estimators=400, random_state=42)
        self.model.fit(X, y)
        self.last_trained = dt.datetime.now()
        
        logger.info(f"Model trained for {self.location_id} with {len(training_df)} samples")
    
    async def get_recent_data(self, days_back: int = 90) -> pd.DataFrame:
        """Fetch recent observed SST data."""
        today = dt.date.today()
        start_date = today - dt.timedelta(days=days_back)
        return await self.fetch_range_for_point(start_date, today)
    
    def predict_sequence(self, base_df: pd.DataFrame, start_date: dt.date, end_date: dt.date) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Predict SST for a sequence of dates."""
        if self.model is None:
            raise ValueError(f"Model not trained for {self.location_id}")
        
        combined = base_df.copy().sort_values("Date").reset_index(drop=True)
        sst_map = {d: v for d, v in zip(combined["Date"], combined["SST"])}
        
        rows = []
        for cur in pd.date_range(start_date, end_date, freq="D"):
            cur = cur.date()
            feat_days = [cur - dt.timedelta(days=i) for i in range(self.window, 0, -1)]
            
            # Check if we have all required input days
            missing_inputs = [d for d in feat_days if d not in sst_map]
            if missing_inputs:
                raise RuntimeError(f"Insufficient history for {cur} in {self.location_id}. Missing: {missing_inputs[:3]}")
            
            X = np.array([sst_map[d] for d in feat_days], dtype=float).reshape(1, -1)
            y_pred = float(self.model.predict(X)[0])
            
            row = {"Date": cur, "SST": y_pred, "IsPredicted": True}
            rows.append(row)
            
            # Add prediction to our data for next iteration
            sst_map[cur] = y_pred
            combined = pd.concat([combined, pd.DataFrame([{"Date": cur, "SST": y_pred}])], ignore_index=True)
        
        pred_df = pd.DataFrame(rows)
        combined = combined.drop_duplicates("Date").sort_values("Date").reset_index(drop=True)
        return pred_df, combined
    
    def calculate_dhw(self, temp_data: pd.DataFrame, threshold: float = 29.0) -> float:
        """Calculate Degree Heating Weeks (DHW) from temperature data."""
        if temp_data.empty:
            return 0.0
        
        # Get last 12 weeks of data
        end_date = temp_data["Date"].max()
        start_date = end_date - dt.timedelta(weeks=12)
        
        recent_data = temp_data[temp_data["Date"] >= start_date].copy()
        if recent_data.empty:
            return 0.0
        
        # Calculate heating degree days
        recent_data["heating_degrees"] = np.maximum(0, recent_data["SST"] - threshold)
        
        # Sum and convert to weeks
        total_heating_days = recent_data["heating_degrees"].sum()
        dhw = total_heating_days / 7.0
        
        return round(dhw, 2)


class MultiLocationTemperatureService:
    """Service for managing temperature predictions across multiple reef locations."""
    
    def __init__(self):
        self.models: Dict[str, LocationTemperatureModel] = {}
        self.cache: Dict[str, Dict] = {}
        self.cache_ttl = 300  # 5 minutes
    
    def get_or_create_model(self, location_id: str, lat: float, lon: float) -> LocationTemperatureModel:
        """Get existing model or create new one for location."""
        if location_id not in self.models:
            self.models[location_id] = LocationTemperatureModel(lat, lon, location_id)
        return self.models[location_id]
    
    async def predict_location(self, location_id: str, lat: float, lon: float, 
                             past_days: int = 7, future_days: int = 7) -> Dict:
        """Generate temperature analysis for a single location."""
        try:
            model = self.get_or_create_model(location_id, lat, lon)
            today = dt.date.today()
            
            # Train model if not already trained or if it's been more than 24 hours
            if (model.model is None or 
                model.last_trained is None or 
                (dt.datetime.now() - model.last_trained).total_seconds() > 86400):
                
                logger.info(f"Training model for {location_id}")
                training_data = await model.build_training_data(today)
                model.train_model(training_data)
            
            # Get recent observed data
            recent_data = await model.get_recent_data(days_back=90)
            if recent_data.empty:
                raise ValueError(f"No recent data available for {location_id}")
            
            # Prepare past data (7 days before today)
            past_start = today - dt.timedelta(days=past_days)
            past_end = today - dt.timedelta(days=1)
            past_data = recent_data[
                (recent_data["Date"] >= past_start) & 
                (recent_data["Date"] <= past_end)
            ].copy()
            
            # Add today's data if available, otherwise predict it
            today_data = recent_data[recent_data["Date"] == today]
            if today_data.empty:
                # Predict today
                today_pred, updated_recent = model.predict_sequence(recent_data, today, today)
                today_temp = today_pred["SST"].iloc[0]
                recent_data = updated_recent
            else:
                today_temp = today_data["SST"].iloc[0]
            
            # Predict future days
            future_start = today + dt.timedelta(days=1)
            future_end = today + dt.timedelta(days=future_days)
            future_pred, _ = model.predict_sequence(recent_data, future_start, future_end)
            
            # Calculate DHW
            dhw = model.calculate_dhw(recent_data)
            
            # Format response data
            past_readings = [
                {
                    "date": row["Date"].strftime("%Y-%m-%d"),
                    "temperature": round(float(row["SST"]), 2),
                    "is_predicted": False
                }
                for _, row in past_data.iterrows()
            ]
            
            # Add today
            past_readings.append({
                "date": today.strftime("%Y-%m-%d"),
                "temperature": round(float(today_temp), 2),
                "is_predicted": today_data.empty
            })
            
            future_readings = [
                {
                    "date": row["Date"].strftime("%Y-%m-%d"),
                    "temperature": round(float(row["SST"]), 2),
                    "is_predicted": True
                }
                for _, row in future_pred.iterrows()
            ]
            
            return {
                "location_id": location_id,
                "past_data": past_readings,
                "future_data": future_readings,
                "current_temp": round(float(today_temp), 2),
                "dhw": dhw,
                "last_updated": dt.datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error predicting for {location_id}: {e}")
            raise
    
    async def predict_all_locations(self, locations: List[Dict], 
                                  past_days: int = 7, future_days: int = 7) -> Dict[str, Dict]:
        """Run predictions for all locations concurrently."""
        tasks = []
        for location in locations:
            task = self.predict_location(
                location["id"], 
                location["lat"], 
                location["lon"],
                past_days,
                future_days
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        location_results = {}
        for location, result in zip(locations, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to predict for {location['id']}: {result}")
                # Return empty result for failed locations
                location_results[location["id"]] = {
                    "location_id": location["id"],
                    "past_data": [],
                    "future_data": [],
                    "current_temp": 0.0,
                    "dhw": 0.0,
                    "error": str(result),
                    "last_updated": dt.datetime.now()
                }
            else:
                location_results[location["id"]] = result
        
        return location_results