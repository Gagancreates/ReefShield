import xarray as xr
import pandas as pd
import datetime as dt

lat, lon = 11.67, 92.75  

end_date = dt.date.today() - dt.timedelta(days=1)
start_date = end_date - dt.timedelta(days=7)

url = (
    "https://psl.noaa.gov/thredds/dodsC/Datasets/noaa.oisst.v2.highres/sst.day.mean."
    f"{start_date.year}.nc"
)

ds = xr.open_dataset(url)

sst_time = ds['sst'].sel(time=slice(str(start_date), str(end_date)))

sst = sst_time.sel(lat=lat, lon=lon, method="nearest")

df = sst.to_dataframe().reset_index()

print(df)
