import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import time
import os
from datetime import datetime

# =====================
# Config (files + reef)
# =====================
CSV_FILE = "sst_sim_14days.csv"                     # 14-day simulation (Date,SST_C,Risk_Level)
CSV_FORECAST = "sst_sim_14days_with_forecast.csv"   # with forecast (Date,SST_C,Source in {"Observed","Forecast"})
reef_lat, reef_lon = 12.0, 92.9  # North Andaman reef

# Color mapping for risk levels
color_map = {
    "Safe": [0, 200, 0],       # green
    "Watch": [255, 255, 0],    # yellow
    "Warning": [255, 140, 0],  # orange
    "Critical": [200, 0, 0]    # red
}

# =====================
# Helpers
# =====================
def _coerce_date(df, col="Date"):
    df = df.copy()
    df[col] = pd.to_datetime(df[col]).dt.date
    return df

def compute_dhw(df_daily, mmm, dhw_window_days=84):
    """
    df_daily: DataFrame with columns ['Date','SST_C'] (Date as datetime.date)
    mmm: Maximum Monthly Mean (°C)
    dhw_window_days: rolling window length in days (default 84)
    Returns: same df with 'HotSpot' (>=1°C only) and 'DHW' (°C-weeks)
    """
    if df_daily.empty:
        return df_daily.assign(HotSpot=[], DHW=[])

    df = df_daily.copy()
    df = df.sort_values("Date")
    hs = df["SST_C"] - float(mmm)
    hs = hs.where(hs >= 1.0, 0.0)   # CRW: only anomalies >= 1°C contribute
    df["HotSpot"] = hs
    # rolling sum over trailing 84 days (min_periods=1 allows short-window demo)
    df["DHW"] = df["HotSpot"].rolling(window=dhw_window_days, min_periods=1).sum() / 7.0
    return df

def flag_dhw_alerts(dhw_value):
    if dhw_value >= 8:
        return "🔴 DHW ≥ 8 (Severe bleaching risk)"
    if dhw_value >= 4:
        return "🟠 DHW ≥ 4 (Bleaching risk)"
    if dhw_value > 0:
        return "🟡 Elevated stress building"
    return "🟢 No accumulated heat stress"

# =====================
# Streamlit UI
# =====================
st.title("Andaman Reef Heatwave Simulation with Forecasting + DHW")
st.write("This demo replays a 14-day marine heatwave scenario for Andaman coral reefs, "
         "predicts the next 7 days, and computes **Degree Heating Weeks (DHW)** using an MMM threshold.")

# ---- Sidebar controls ----
st.sidebar.header("Settings")
mmm = st.sidebar.number_input("MMM (°C)", min_value=20.0, max_value=35.0, value=29.5, step=0.1,
                              help="Maximum Monthly Mean: typical warmest-month average SST for this reef.")
dhw_window = st.sidebar.slider("DHW window (days)", min_value=28, max_value=120, value=84, step=7,
                               help="Standard is 84 days (12 weeks).")
bleach_thresh = st.sidebar.number_input("Bleaching SST threshold (°C)", min_value=25.0, max_value=35.0,
                                        value=30.5, step=0.1,
                                        help="Used only for the simple forecast alert below.")

st.sidebar.markdown("---")
st.sidebar.subheader("Optional: Upload recent history for DHW")
hist_file = st.sidebar.file_uploader("Upload historical SST CSV (Date,SST_C)", type=["csv"])
hist_df = None
if hist_file is not None:
    try:
        hist_df = pd.read_csv(hist_file)
        if not {"Date", "SST_C"}.issubset(hist_df.columns):
            st.sidebar.error("Uploaded file must have columns: Date, SST_C")
            hist_df = None
        else:
            hist_df = _coerce_date(hist_df, "Date")[["Date", "SST_C"]].dropna().sort_values("Date")
            st.sidebar.success(f"History loaded: {len(hist_df)} days")
    except Exception as e:
        st.sidebar.error(f"Error reading file: {e}")
        hist_df = None

# ---- Main data existence checks ----
if not os.path.exists(CSV_FILE):
    st.error(f"CSV file not found: {CSV_FILE}. Please place it in the same folder as the app.")
    st.stop()

df_sim = pd.read_csv(CSV_FILE)
if not {"Date","SST_C","Risk_Level"}.issubset(df_sim.columns):
    st.error(f"{CSV_FILE} must have columns: Date, SST_C, Risk_Level")
    st.stop()

df_sim = _coerce_date(df_sim, "Date")

# =====================
# Simulation
# =====================
st.subheader("🎬 14-Day Simulation (with DHW)")

# Precompute DHW for the simulation window (with optional history concatenated)
if hist_df is not None and not hist_df.empty:
    # Only keep history *before* simulation start to avoid duplicates
    sim_start = df_sim["Date"].min()
    hist_trim = hist_df[hist_df["Date"] < sim_start]
    dhw_input_sim = pd.concat([hist_trim, df_sim[["Date","SST_C"]]], ignore_index=True)
    used_history = True
else:
    dhw_input_sim = df_sim[["Date","SST_C"]].copy()
    used_history = False

dhw_sim = compute_dhw(dhw_input_sim, mmm, dhw_window)
# create a lookup for simulation dates to DHW/HotSpot
dhw_lookup = dhw_sim.set_index("Date")[["HotSpot","DHW"]].to_dict("index")

info_note = "Using uploaded history for DHW ✅" if used_history else "No history uploaded — DHW uses a short window (demo) ⚠️"
st.caption(info_note)

# Start simulation UI
chart = st.line_chart()
status = st.empty()
map_area = st.empty()

if st.button("▶ Start Simulation"):
    for i in range(len(df_sim)):
        row = df_sim.iloc[i]
        date_i = row["Date"]
        risk = row["Risk_Level"]
        sst = float(row["SST_C"])
        # pull DHW/HotSpot for this date (if available)
        hs_i = dhw_lookup.get(date_i, {}).get("HotSpot", np.nan)
        dhw_i = dhw_lookup.get(date_i, {}).get("DHW", np.nan)

        # ----- Map update -----
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=[{"lat": reef_lat, "lon": reef_lon, "risk": risk}],
            get_position=["lon", "lat"],
            get_color=color_map.get(risk, [128, 128, 128]) + [200],
            get_radius=40000,
        )
        view_state = pdk.ViewState(latitude=reef_lat, longitude=reef_lon, zoom=6)
        tip = f"Andaman Reef\nDate: {date_i}\nRisk: {risk}\nSST: {sst:.2f} °C\nDHW: {dhw_i:.2f} °C-weeks"
        map_area.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": tip}))

        # ----- Status update -----
        if risk == "Safe":
            status.success(f"Day {date_i}: 🌿 Reef Safe — SST {sst:.2f} °C | DHW {dhw_i:.2f}")
        elif risk == "Watch":
            status.warning(f"Day {date_i}: ⚠️ Stress Watch — SST {sst:.2f} °C | DHW {dhw_i:.2f}")
        elif risk == "Warning":
            status.error(f"Day {date_i}: 🚨 Bleaching Warning — SST {sst:.2f} °C | DHW {dhw_i:.2f}")
        else:
            status.error(f"Day {date_i}: 🔴 CRITICAL — SST {sst:.2f} °C | DHW {dhw_i:.2f}")

        # ----- Chart update (SST) -----
        chart.add_rows(pd.DataFrame({"SST (°C)": [sst]}, index=[str(date_i)]))

        time.sleep(2)  # 2s per simulated day

# =====================
# Forecast + DHW
# =====================
st.subheader("📈 Observed vs Forecast SST + DHW outlook")

if not os.path.exists(CSV_FORECAST):
    st.warning("⚠️ Forecast data not found. Please generate 'sst_sim_14days_with_forecast.csv'")
else:
    df_forecast = pd.read_csv(CSV_FORECAST)
    if not {"Date","SST_C","Source"}.issubset(df_forecast.columns):
        st.error(f"{CSV_FORECAST} must have columns: Date, SST_C, Source")
        st.stop()

    df_forecast = _coerce_date(df_forecast, "Date").sort_values("Date")
    observed = df_forecast[df_forecast["Source"] == "Observed"][["Date","SST_C"]]
    forecast = df_forecast[df_forecast["Source"] == "Forecast"][["Date","SST_C"]]

    # Plot observed vs forecast SST
    st.line_chart({
        "Observed SST": observed.set_index("Date")["SST_C"],
        "Forecast SST": forecast.set_index("Date")["SST_C"],
    })

    # Simple early warning based on SST threshold
    if not forecast.empty and forecast["SST_C"].max() > bleach_thresh:
        st.error("🚨 Early Warning: Forecast predicts bleaching risk within 7 days (SST exceeds threshold)!")
    else:
        st.success("✅ Forecast: SST remains below bleaching threshold.")

    # ====== DHW over observed+forecast (with optional history) ======
    if hist_df is not None and not hist_df.empty:
        last_obs_date = observed["Date"].max() if not observed.empty else None
        # Only keep history before the first date in observed to avoid duplicates
        first_obs_date = observed["Date"].min() if not observed.empty else None
        hist_trim2 = hist_df.copy()
        if first_obs_date is not None:
            hist_trim2 = hist_trim2[hist_trim2["Date"] < first_obs_date]
        dhw_input_all = pd.concat([hist_trim2, observed, forecast], ignore_index=True)
        used_history_fore = True
    else:
        dhw_input_all = pd.concat([observed, forecast], ignore_index=True)
        used_history_fore = False

    dhw_all = compute_dhw(dhw_input_all, mmm, dhw_window)
    dhw_all_plot = dhw_all.set_index("Date")["DHW"]

    st.line_chart({"DHW (°C-weeks)": dhw_all_plot})

    # Metrics
    current_row = dhw_all.iloc[len(observed)-1] if len(observed) > 0 else dhw_all.iloc[0]
    cur_dhw = float(current_row["DHW"])
    max_future_dhw = float(dhw_all.iloc[-1]["DHW"])
    st.write(f"**Current DHW**: {cur_dhw:.2f} °C-weeks  |  **Max DHW over forecast**: {max_future_dhw:.2f} °C-weeks")
    st.info(flag_dhw_alerts(max_future_dhw))

    if not used_history_fore:
        st.caption("⚠️ No historical SST uploaded — DHW is computed on a short window (demo). "
                   "Upload ~84+ days of history for standard DHW.")

# Done
