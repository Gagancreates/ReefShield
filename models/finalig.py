# =================== CONFIG ===================
import datetime as dt
import pandas as pd
import numpy as np
import xarray as xr
from calendar import isleap
from sklearn.ensemble import RandomForestRegressor

lat, lon = 11.67, 92.75     # Andaman reef coords
window = 14          # number of previous days as features
train_csv = "andaman_sst_training.csv"
pred_rows_csv = "andaman_sst_predictions.csv"
filled_series_csv = "andaman_sst_recent_filled.csv"

# Seasonal training years: 1982 -> last full year
START_YEAR = 1982
END_YEAR = dt.date.today().year - 1

# =================== HELPERS ===================
def safe_target_for_year(base: dt.date, year: int) -> dt.date:
    """Return the 'same' month/day in that year, with Feb 29 -> Feb 28 fallback."""
    m, d = base.month, base.day
    if m == 2 and d == 29 and not isleap(year):
        return dt.date(year, 2, 28)
    return dt.date(year, m, d)

def fetch_range_for_point(lat, lon, start_date: dt.date, end_date: dt.date) -> pd.DataFrame:
    """
    Fetch OISST sst for [start_date, end_date] at nearest grid to (lat,lon),
    stitching across year files as needed. Returns DataFrame(Date, SST).
    """

    pieces = []
    for y in range(start_date.year, end_date.year + 1):
        url = f"https://psl.noaa.gov/thredds/dodsC/Datasets/noaa.oisst.v2.highres/sst.day.mean.{y}.nc"
        try:
            ds = xr.open_dataset(url)
            sst_t = ds["sst"].sel(time=slice(str(start_date), str(end_date)))
            sst_pt = sst_t.sel(lat=lat, lon=lon, method="nearest")
            df = sst_pt.to_dataframe().reset_index()[["time", "sst"]]
            pieces.append(df)
        except Exception as e:
            print(f"Skipping fetch {y}: {e}")
    if not pieces:
        return pd.DataFrame(columns=["Date", "SST"])
    out = pd.concat(pieces, ignore_index=True)
    out = out.rename(columns={"time": "Date", "sst": "SST"})
    out["Date"] = pd.to_datetime(out["Date"]).dt.date
    out = out.dropna(subset=["SST"]).drop_duplicates(subset=["Date"]).sort_values("Date")
    return out[["Date", "SST"]].reset_index(drop=True)

def build_training_csv(base_today: dt.date, start_year=START_YEAR, end_year=END_YEAR, window=7, out_path=train_csv):
    """
    Build/update seasonal training CSV for the run date's month/day across all years.
    """
    records = []
    for year in range(start_year, end_year + 1):
        target_y = safe_target_for_year(base_today, year)
        start = target_y - dt.timedelta(days=window)
        end = target_y - dt.timedelta(days=1)

        win_df = fetch_range_for_point(lat, lon, start, end)
        if len(win_df) != window:
            print(f"Skipping {year}: expected {window} days, got {len(win_df)}")
            continue

        tgt_df = fetch_range_for_point(lat, lon, target_y, target_y)
        if tgt_df.empty:
            print(f"Skipping {year}: target day {target_y} missing")
            continue

        sst_values = win_df["SST"].values.tolist()
        sst_target = float(tgt_df["SST"].iloc[0])

        record = {"Year": year}
        # win_df is ascending; first is Day-7, last is Day-1
        for i, val in enumerate(sst_values, 1):
            record[f"Day-{window - i + 1}"] = float(val)
        record["Target"] = sst_target
        records.append(record)
        print(f"Built training row for {year} (target {target_y})")

    df = pd.DataFrame(records)
    df.to_csv(out_path, index=False)
    print(f"✅ Saved seasonal training CSV -> {out_path} (base day = {base_today})")
    return df

def train_model(training_df: pd.DataFrame, window=7):
    Xcols = [f"Day-{i}" for i in range(window, 0, -1)]
    X = training_df[Xcols].values
    y = training_df["Target"].values
    model = RandomForestRegressor(n_estimators=400, random_state=42)
    model.fit(X, y)
    print("✅ Model trained on seasonal dataset.")
    return model

def ensure_enough_history(df: pd.DataFrame, need_until_date: dt.date, window=7):
    """
    Ensure df has at least `window` days ending the day before `need_until_date`.
    If not, extend back by fetching an extra month.
    """
    if df.empty:
        return df
    earliest_needed = (need_until_date - dt.timedelta(days=window))
    if df["Date"].min() <= earliest_needed:
        return df
    extra_start = earliest_needed - dt.timedelta(days=30)
    more = fetch_range_for_point(lat, lon, extra_start, df["Date"].min())
    df2 = pd.concat([more, df], ignore_index=True).drop_duplicates("Date").sort_values("Date")
    return df2

def predict_missing_days(model, base_df: pd.DataFrame, start_date: dt.date, end_date: dt.date, window=7):
    """
    Recursively predict daily SST for [start_date, end_date], using last `window` days
    (observed or previously predicted). Returns:
      pred_rows_df: rows with Date, Day-7..Day-1, SST(pred), IsPredicted=True
      combined_df: observed+predicted series, Date,SST sorted unique
    """
    combined = base_df.copy().sort_values("Date").reset_index(drop=True)
    sst_map = {d: v for d, v in zip(combined["Date"], combined["SST"])}

    rows = []
    for cur in pd.date_range(start_date, end_date, freq="D"):
        cur = cur.date()
        feat_days = [cur - dt.timedelta(days=i) for i in range(window, 0, -1)]
        missing_inputs = [d for d in feat_days if d not in sst_map]
        if missing_inputs:
            raise RuntimeError(f"Insufficient history for {cur}. Missing inputs start with {missing_inputs[:3]}")

        X = np.array([sst_map[d] for d in feat_days], dtype=float).reshape(1, -1)
        y_pred = float(model.predict(X)[0])

        row = {"Date": cur, "SST": y_pred, "IsPredicted": True}
        for i, d in enumerate(feat_days, start=1):
            row[f"Day-{window - i + 1}"] = float(sst_map[d])
        rows.append(row)

        sst_map[cur] = y_pred
        combined = pd.concat([combined, pd.DataFrame([{"Date": cur, "SST": y_pred}])], ignore_index=True)

    pred_df = pd.DataFrame(rows)
    feat_cols = [f"Day-{i}" for i in range(window, 0, -1)]
    pred_df = pred_df[["Date"] + feat_cols + ["SST", "IsPredicted"]]
    combined = combined.drop_duplicates("Date").sort_values("Date").reset_index(drop=True)
    return pred_df, combined

# =================== MAIN ===================
# if __name__ == "__main__":
    # =================== MAIN ===================
if __name__ == "__main__":
    # 1) Establish "today" (local date is fine)
    today = dt.date.today()

    FUTURE_DAYS = 7
    future_csv = "andaman_sst_next7_predictions.csv"

    # 2) Build/refresh seasonal training CSV for this calendar day across years
    train_df = build_training_csv(today, START_YEAR, END_YEAR, window, train_csv)

    if train_df.empty:
        raise SystemExit("Training CSV ended up empty. Check network/URLs/coordinates.")

    # 3) Train model
    model = train_model(train_df, window)

    # 4) Fetch recent observed series (last ~90 days to be safe)
    start_fetch = today - dt.timedelta(days=90)
    recent = fetch_range_for_point(lat, lon, start_fetch, today)

    if recent.empty:
        raise SystemExit("No recent OISST data fetched. Check network/URL/coordinates.")

    # 5) Determine gap from last observed to today
    last_obs = recent["Date"].max()
    start_missing = last_obs + dt.timedelta(days=1)

    combined_series = None
    if start_missing <= today:
        # Ensure we have enough history before the first missing day
        recent = ensure_enough_history(recent, start_missing, window)
        if recent.empty:
            raise SystemExit("Insufficient history for predictions.")

        # 6) Predict each missing day up to today
        pred_rows, combined_series = predict_missing_days(
            model, recent, start_missing, today, window
        )

        # Save predicted rows (each has Day-7..Day-1 + predicted SST)
        pred_rows.to_csv(pred_rows_csv, index=False)
        print(f"✅ Wrote predicted rows -> {pred_rows_csv}")

        # Save the full filled series (observed + predicted)
        combined_series.to_csv(filled_series_csv, index=False)
        print(f"✅ Wrote filled series -> {filled_series_csv}")
    else:
        # No gap; optionally predict today anyway
        recent = ensure_enough_history(recent, today, window)
        pred_rows, combined_series = predict_missing_days(
            model, recent, today, today, window
        )
        pred_rows.to_csv(pred_rows_csv, index=False)
        combined_series.to_csv(filled_series_csv, index=False)
        print(f"ℹ️ No missing observed days. Still predicted today.\n"
              f"✅ {pred_rows_csv}\n✅ {filled_series_csv}")

    # ---------------------
    # 7) Predict next FUTURE_DAYS days (today+1 .. today+FUTURE_DAYS)
    # ---------------------
    future_start = today + dt.timedelta(days=1)
    future_end = today + dt.timedelta(days=FUTURE_DAYS)

    # ensure combined_series exists and has enough history for predicting future_start
    combined_series = ensure_enough_history(combined_series, future_start, window)
    if combined_series.empty:
        print("⚠️ Cannot predict future days: insufficient history after ensuring more data.")
    else:
        try:
            future_preds, _ = predict_missing_days(
                model, combined_series, future_start, future_end, window
            )
            future_preds.to_csv(future_csv, index=False)
            print(f"✅ Wrote next-{FUTURE_DAYS}-day predictions -> {future_csv}")
        except Exception as e:
            print(f"❌ Failed to predict next-{FUTURE_DAYS} days: {e}")

    print("\nAll done. 🎯")
