import xarray as xr
import pandas as pd
import datetime as dt

# Reef location (Andaman, change if needed)
lat, lon = 11.67, 92.75  

# Today's target date
target_date = dt.date(2025, 9, 3)

# Window length (e.g., 7 days before target date)
window = 7  

# Store results
records = []

for year in range(1982, 2025):  # OISST starts ~1981, skip current year since incomplete
    # Compute window dates for that year
    start = target_date.replace(year=year) - dt.timedelta(days=window)
    end = target_date.replace(year=year) - dt.timedelta(days=1)

    # Build file url for that year
    url = f"https://psl.noaa.gov/thredds/dodsC/Datasets/noaa.oisst.v2.highres/sst.day.mean.{year}.nc"

    try:
        ds = xr.open_dataset(url)
        
        # Slice time window
        sst_time = ds['sst'].sel(time=slice(str(start), str(end)))
        
        # Select nearest grid to reef
        sst_values = sst_time.sel(lat=lat, lon=lon, method="nearest").values.flatten()
        
        # Also get the actual SST on target day (for training label)
        sst_target = ds['sst'].sel(time=str(target_date.replace(year=year)), 
                                   lat=lat, lon=lon, method="nearest").values.item()
        
        # Store record
        record = {"Year": year}
        for i, val in enumerate(sst_values, 1):
            record[f"Day-{window-i+1}"] = float(val)
        record["Target"] = float(sst_target)
        
        records.append(record)
        print(f"Done {year}")
        
    except Exception as e:
        print(f"Skipping {year}: {e}")

# Convert to dataframe
df = pd.DataFrame(records)

# Save to CSV
output_file = "andaman_sst_training.csv"
df.to_csv(output_file, index=False)

print(f"\n✅ Data saved to {output_file}")
