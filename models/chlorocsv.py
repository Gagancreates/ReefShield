# find_nearest_valid_pixels.py
# pip install xarray netcdf4 numpy pandas

import xarray as xr
import numpy as np
import pandas as pd
import os
from math import radians, sin, cos, sqrt, atan2

MODIS_PATH = r"D:\INFERENTIA\AQUA_MODIS.20250731.L3m.DAY.CHL.chlor_a.9km.nc"
OUT_DIR = "andaman_chl_output"
os.makedirs(OUT_DIR, exist_ok=True)

# Reef boxes (same as before)
reef_boxes = {
    "Havelock_Island": dict(lat_min=11.90, lat_max=12.05, lon_min=92.90, lon_max=93.05),
    "MG_Marine_NP": dict(lat_min=11.50, lat_max=11.65, lon_min=92.55, lon_max=92.70),
    "Jolly_Buoy": dict(lat_min=11.47, lat_max=11.52, lon_min=92.58, lon_max=92.64),
    "Neil_Island": dict(lat_min=11.77, lat_max=11.88, lon_min=92.99, lon_max=93.10),
}

# Search parameters
MAX_DISTANCE_KM = 50      # max radius to search for a valid pixel
N_NEAREST = 3             # return up to this many nearest valid pixels
MIN_VALID_VALUE = 0       # optionally require chlor_a > MIN_VALID_VALUE

# Haversine distance (km) between two lat/lon points
def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in km
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi/2.0)**2 + cos(phi1)*cos(phi2)*sin(dlambda/2.0)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

# Load data
ds = xr.open_dataset(MODIS_PATH)
var = "chlor_a"
if var not in ds:
    raise ValueError(f"{var} not in dataset. Available: {list(ds.data_vars)}")

# normalize lon coords to -180..180
def norm_lon_arr(lon_arr):
    return ((lon_arr + 180) % 360) - 180

if "lon" in ds.coords:
    ds = ds.assign_coords(lon=norm_lon_arr(ds.lon))
elif "longitude" in ds.coords:
    ds = ds.assign_coords(longitude=norm_lon_arr(ds.longitude))
    ds = ds.rename({"longitude": "lon"})
else:
    raise ValueError("No lon/longitude coordinate found in dataset")

chl = ds[var]

# Build 2D arrays of lat/lon for all grid cells
# Ensure coords are 1D
lats = chl['lat'].values
lons = chl['lon'].values
lon2d, lat2d = np.meshgrid(lons, lats)  # shapes (nlat, nlon)

# Flatten arrays for quick searching
lat_flat = lat2d.ravel()
lon_flat = lon2d.ravel()
chl_flat = chl.values.ravel()

# Precompute mask of valid entries
valid_mask = np.isfinite(chl_flat) & (chl_flat > MIN_VALID_VALUE)

results = []

for reef_name, bbox in reef_boxes.items():
    # reef center
    center_lat = 0.5 * (bbox["lat_min"] + bbox["lat_max"])
    center_lon = 0.5 * (bbox["lon_min"] + bbox["lon_max"])
    center_lon = ((center_lon + 180) % 360) - 180  # normalize

    # quick bounding box in degrees to limit candidates (approx)
    # convert MAX_DISTANCE_KM to degrees roughly: 1 deg lat ~ 111 km
    deg_lat_buffer = MAX_DISTANCE_KM / 111.0
    # lon buffer depends on latitude
    deg_lon_buffer = MAX_DISTANCE_KM / (111.0 * max(1e-6, np.cos(np.deg2rad(center_lat))))

    lat_min_search = center_lat - deg_lat_buffer
    lat_max_search = center_lat + deg_lat_buffer
    lon_min_search = center_lon - deg_lon_buffer
    lon_max_search = center_lon + deg_lon_buffer

    # select candidates inside this rough box
    in_box = (lat_flat >= lat_min_search) & (lat_flat <= lat_max_search) & \
             (lon_flat >= lon_min_search) & (lon_flat <= lon_max_search) & valid_mask

    if not np.any(in_box):
        # no candidates even in rough box
        print(f"[WARN] No valid candidates within approx {MAX_DISTANCE_KM} km of {reef_name}")
        results.append({
            "reef": reef_name,
            "center_lat": center_lat,
            "center_lon": center_lon,
            "found": False,
            "notes": f"No valid pixels within approx {MAX_DISTANCE_KM} km"
        })
        continue

    cand_idx = np.where(in_box)[0]
    cand_lats = lat_flat[cand_idx]
    cand_lons = lon_flat[cand_idx]
    cand_vals = chl_flat[cand_idx]

    # compute haversine distances
    dists = np.array([haversine_km(center_lat, center_lon, float(la), float(lo)) for la, lo in zip(cand_lats, cand_lons)])

    # filter by MAX_DISTANCE_KM
    within = dists <= MAX_DISTANCE_KM
    if not np.any(within):
        print(f"[WARN] Candidates exist but none within {MAX_DISTANCE_KM} km for {reef_name}")
        results.append({
            "reef": reef_name,
            "center_lat": center_lat,
            "center_lon": center_lon,
            "found": False,
            "notes": f"No valid pixels within {MAX_DISTANCE_KM} km; nearest at {float(np.min(dists)):.1f} km"
        })
        continue

    # sort by distance and pick up to N_NEAREST
    valid_indices = cand_idx[within]
    valid_dists = dists[within]
    valid_vals = cand_vals[within]

    order = np.argsort(valid_dists)
    picked = order[:N_NEAREST]

    for rank, idx_local in enumerate(picked, start=1):
        idx_global = valid_indices[idx_local]
        rlat = float(lat_flat[idx_global])
        rlon = float(lon_flat[idx_global])
        rval = float(chl_flat[idx_global])
        rdist = float(valid_dists[idx_local])

        results.append({
            "reef": reef_name,
            "center_lat": center_lat,
            "center_lon": center_lon,
            "found": True,
            "rank": rank,
            "pixel_lat": rlat,
            "pixel_lon": rlon,
            "chlor_a": rval,
            "distance_km": rdist
        })

    print(f"[OK] {reef_name}: found {min(N_NEAREST, np.sum(within))} valid pixels (nearest {valid_dists[order[0]]:.2f} km)")

# Save results to CSV (multiple rows per reef if N_NEAREST)
out_df = pd.DataFrame(results)
out_csv = os.path.join(OUT_DIR, "nearest_valid_pixels.csv")
out_df.to_csv(out_csv, index=False)
print("Saved nearest valid pixels to:", out_csv)
print(out_df)
