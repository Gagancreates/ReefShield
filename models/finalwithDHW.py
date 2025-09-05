import datetime as dt
import calendar
import numpy as np
import pandas as pd
import xarray as xr

# ------------------ CONFIG ------------------
# Reef location (edit if needed)
LAT, LON = 11.67, 92.75

# MMM baseline (quick modern climatology)
BASELINE_START = 1982
BASELINE_END   = max(1982, dt.date.today().year)  # up to current year

# How many days of daily SST to fetch for DHW calc
DAILY_WINDOW_DAYS = 120   # must be >= 84 for DHW

# ------------------ HELPERS ------------------
def fetch_monthly_means(lat, lon, y0, y1):
    """
    FAST: use monthly OISST means (single file) and compute climatology over [y0..y1].
    Returns (climatology_df with Month,SST, MMM_value, MMM_month_int).
    """
    # Monthly means file lives in v2 (not highres)
    url = "https://psl.noaa.gov/thredds/dodsC/Datasets/noaa.oisst.v2/sst.mnmean.nc"
    ds = xr.open_dataset(url)

    # Limit to baseline years
    t = pd.to_datetime(ds["time"].values)
    mask = (t >= pd.Timestamp(y0, 1, 1)) & (t <= pd.Timestamp(y1, 12, 31))
    ds_base = ds.sel(time=mask)

    # Point extract (nearest grid)
    sst_pt = ds_base["sst"].sel(lat=lat, lon=lon, method="nearest")

    # DataFrame with Year/Month and mean per (Year,Month), then monthly climatology
    df = sst_pt.to_dataframe().reset_index()  # columns: time, lat, lon, sst
    df["Year"]  = pd.to_datetime(df["time"]).dt.year
    df["Month"] = pd.to_datetime(df["time"]).dt.month
    # average each calendar month across baseline years
    clim = df.groupby("Month", as_index=False)["sst"].mean().rename(columns={"sst": "SST"})
    clim = clim.sort_values("Month")

    mmm_val = float(clim["SST"].max())
    mmm_month = int(clim.loc[clim["SST"].idxmax(), "Month"])
    return clim, mmm_val, mmm_month

def fetch_daily_series(lat, lon, start_date: dt.date, end_date: dt.date) -> pd.DataFrame:
    """
    Fetch daily OISST (highres) over [start_date..end_date] at the nearest grid point.
    Returns DataFrame(Date, SST) sorted.
    """
    pieces = []
    for year in range(start_date.year, end_date.year + 1):
        url = f"https://psl.noaa.gov/thredds/dodsC/Datasets/noaa.oisst.v2.highres/sst.day.mean.{year}.nc"
        try:
            ds = xr.open_dataset(url)
            sst_t = ds["sst"].sel(time=slice(str(start_date), str(end_date)))
            sst_pt = sst_t.sel(lat=lat, lon=lon, method="nearest")
            df = sst_pt.to_dataframe().reset_index()[["time", "sst"]]
            pieces.append(df)
        except Exception as e:
            print(f"[warn] skip {year}: {e}")
    if not pieces:
        raise RuntimeError("No daily data fetched (check internet/URL/coords).")
    out = pd.concat(pieces, ignore_index=True)
    out = out.rename(columns={"time": "Date", "sst": "SST"})
    out["Date"] = pd.to_datetime(out["Date"]).dt.date
    out = out.dropna(subset=["SST"]).drop_duplicates(subset=["Date"]).sort_values("Date")
    return out[["Date", "SST"]].reset_index(drop=True)

def compute_dhw(daily_df: pd.DataFrame, mmm_value: float) -> pd.DataFrame:
    """
    Compute HotSpot and DHW from daily SST and MMM:
      - HotSpot = SST - MMM; values < 1.0°C are set to 0.0
      - DHW = sum of HotSpot over trailing 84 days / 7  (°C-weeks)
    Returns a copy with columns: Date, SST, HotSpot, DHW
    """
    df = daily_df.copy().sort_values("Date")
    df["HotSpot"] = df["SST"] - mmm_value
    df.loc[df["HotSpot"] < 1.0, "HotSpot"] = 0.0  # CRW rule: ignore <1°C anomalies
    # 84-day rolling window sum, then convert to °C-weeks
    df["DHW"] = df["HotSpot"].rolling(window=84, min_periods=1).sum() / 7.0
    return df

# ------------------ MAIN ------------------
if __name__ == "__main__":
    today = dt.date.today()

    # 1) MMM from monthly climatology (2020..present)
    clim, MMM, MMM_month = fetch_monthly_means(LAT, LON, BASELINE_START, BASELINE_END)
    print(f"MMM (baseline {BASELINE_START}-{BASELINE_END}): {MMM:.3f} °C "
          f"(peak month: {MMM_month} - {calendar.month_name[MMM_month]})")

    # 2) Pull daily SST for DHW calc (last DAILY_WINDOW_DAYS)
    start_daily = today - dt.timedelta(days=DAILY_WINDOW_DAYS)
    daily = fetch_daily_series(LAT, LON, start_daily, today)

    # 3) Compute DHW
    dhw_df = compute_dhw(daily, MMM)

    # 4) Extract today’s values (or last available if today missing)
    last_row = dhw_df.iloc[-1]
    last_date = last_row["Date"]
    hotspot_today = float(last_row["HotSpot"])
    dhw_today = float(last_row["DHW"])
    sst_today = float(last_row["SST"])

    print("\n--- OUTPUT ---")
    print(f"Last available date: {last_date}")
    print(f"SST on last date   : {sst_today:.3f} °C")
    print(f"HotSpot            : {hotspot_today:.3f} °C (>=1°C contributes to DHW)")
    print(f"DHW (84-day, °C-wk): {dhw_today:.3f}")

    # Optional: show the monthly climatology table (pretty)
    # print("\nMonthly climatology (baseline mean SST by month):")
    # print(clim.assign(MonthName=clim["Month"].map(lambda m: calendar.month_name[m]))[["Month","MonthName","SST"]])
