# =================== CONFIG ===================
import datetime as dt
import pandas as pd
import numpy as np
import xarray as xr
from calendar import isleap
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

# --- location + knobs ---
lat, lon = 11.67, 92.75     # Andaman reef coords
window = 7                  # number of previous days as features

# --- outputs ---
train_csv = "andaman_sst_training.csv"
pred_rows_csv = "andaman_sst_predictions.csv"
filled_series_csv = "andaman_sst_recent_filled.csv"

# Seasonal training years: 1982 -> last full year
START_YEAR = 1982
END_YEAR = dt.date.today().year - 1

# ---- Backtest switch: set to a past date to evaluate accuracy (or set to None) ----
# Examples: dt.date(2025, 6, 12) or dt.date(2024, 6, 12)
TEST_DATE = dt.date(2025, 6, 12)   # set None to run “today” mode

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
if __name__ == "__main__":
    if TEST_DATE is not None:
        # ===== BACKTEST MODE: predict a past date and compare with NOAA =====
        test_date = TEST_DATE
        print(f"\n🔎 Backtesting for {test_date} ...")

        # 1) Build seasonal training for that calendar day across years
        train_df = build_training_csv(test_date, START_YEAR, END_YEAR, window, train_csv)
        if train_df.empty:
            raise SystemExit("Training dataset empty. Check network/URLs/coordinates.")

        # 2) Train model
        model = train_model(train_df, window)

        # 3) Fetch observed series around the test date (90 days context)
        start_fetch = test_date - dt.timedelta(days=90)
        observed = fetch_range_for_point(lat, lon, start_fetch, test_date)
        if test_date not in observed["Date"].values:
            raise SystemExit(f"No observed SST available for {test_date} (check dataset or coords)")

        # Keep actual for scoring, but REMOVE test_date to simulate 'unknown'
        y_true = float(observed.loc[observed["Date"] == test_date, "SST"].values[0])
        observed_wo_test = observed[observed["Date"] != test_date].copy()

        # 4) Ensure at least 7 days before the test_date
        observed_wo_test = ensure_enough_history(observed_wo_test, test_date, window)
        if observed_wo_test.empty:
            raise SystemExit("Insufficient history for backtest.")

        # 5) Predict ONLY the test_date (start=end=test_date)
        pred_rows, _ = predict_missing_days(
            model, observed_wo_test, start_date=test_date, end_date=test_date, window=window
        )
        y_pred = float(pred_rows.loc[pred_rows["Date"] == test_date, "SST"].values[0])

        # 6) Metrics (handle older sklearn without squared=False)
        mae = mean_absolute_error([y_true], [y_pred])
        try:
            rmse = mean_squared_error([y_true], [y_pred], squared=False)
        except TypeError:
            rmse = mean_squared_error([y_true], [y_pred]) ** 0.5

        # 7) Print + Save a small CSV with the comparison
        print(f"\n🎯 {test_date}  Predicted={y_pred:.3f} °C | Actual={y_true:.3f} °C")
        print(f"   MAE = {mae:.3f} °C, RMSE = {rmse:.3f} °C")
        pd.DataFrame([{
            "Date": test_date,
            "Predicted_SST": y_pred,
            "Actual_SST": y_true,
            "MAE_degC": mae,
            "RMSE_degC": rmse
        }]).to_csv("andaman_sst_backtest_result.csv", index=False)
        print("   Saved -> andaman_sst_backtest_result.csv")

    else:
        # ===== LIVE “TODAY” MODE: fill NOAA lag up to today =====
        today = dt.date.today()

        # Build/refresh seasonal training CSV for this day across years
        train_df = build_training_csv(today, START_YEAR, END_YEAR, window, train_csv)
        if train_df.empty:
            raise SystemExit("Training CSV ended up empty. Check network/URLs/coordinates.")

        # Train model
        model = train_model(train_df, window)

        # Fetch recent observed series (last ~90 days)
        start_fetch = today - dt.timedelta(days=90)
        recent = fetch_range_for_point(lat, lon, start_fetch, today)
        if recent.empty:
            raise SystemExit("No recent OISST data fetched. Check network/URL/coordinates.")

        # Determine gap from last observed to today
        last_obs = recent["Date"].max()
        start_missing = last_obs + dt.timedelta(days=1)

        if start_missing <= today:
            recent = ensure_enough_history(recent, start_missing, window)
            if recent.empty:
                raise SystemExit("Insufficient history for predictions.")

            pred_rows, combined_series = predict_missing_days(
                model, recent, start_missing, today, window
            )

            pred_rows.to_csv(pred_rows_csv, index=False)
            combined_series.to_csv(filled_series_csv, index=False)
            print(f"✅ Wrote predicted rows -> {pred_rows_csv}")
            print(f"✅ Wrote filled series -> {filled_series_csv}")
        else:
            recent = ensure_enough_history(recent, today, window)
            pred_rows, combined_series = predict_missing_days(
                model, recent, today, today, window
            )
            pred_rows.to_csv(pred_rows_csv, index=False)
            combined_series.to_csv(filled_series_csv, index=False)
            print(f"ℹ️ No missing observed days. Still predicted today.\n"
                  f"✅ {pred_rows_csv}\n✅ {filled_series_csv}")

        print("\nAll done. 🎯")
