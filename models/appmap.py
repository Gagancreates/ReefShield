import streamlit as st
import pandas as pd
import pydeck as pdk
import time
import os

# =====================
# Config
# =====================
CSV_FILE = "sst_sim_14days.csv"                  # 14-day simulation
CSV_FORECAST = "sst_sim_14days_with_forecast.csv"  # with forecast
reef_lat, reef_lon = 12.0, 92.9  # North Andaman reef

# Color mapping for risk levels
color_map = {
    "Safe": [0, 200, 0],       # green
    "Watch": [255, 255, 0],    # yellow
    "Warning": [255, 140, 0],  # orange
    "Critical": [200, 0, 0]    # red
}

# =====================
# Streamlit App
# =====================
st.title("🌍 Andaman Reef Heatwave Simulation with Forecasting")
st.write("This demo replays a 14-day marine heatwave scenario for Andaman coral reefs, then predicts the next 7 days.")

# Check if simulation CSV exists
if not os.path.exists(CSV_FILE):
    st.error(f"CSV file not found: {CSV_FILE}. Please place it in the same folder as app.py")
else:
    df = pd.read_csv(CSV_FILE)

    if st.button("▶ Start Simulation"):
        chart = st.line_chart()
        status = st.empty()
        map_area = st.empty()

        # ===== Auto simulation =====
        for i in range(len(df)):
            row = df.iloc[i]
            risk = row["Risk_Level"]
            sst = row["SST_C"]

            # ===== Map update =====
            layer = pdk.Layer(
                "ScatterplotLayer",
                data=[{"lat": reef_lat, "lon": reef_lon, "risk": risk}],
                get_position=["lon", "lat"],
                get_color=color_map[risk] + [200],
                get_radius=40000,
            )
            view_state = pdk.ViewState(latitude=reef_lat, longitude=reef_lon, zoom=6)

            map_area.pydeck_chart(pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                tooltip={"text": f"Andaman Reef\nRisk: {risk}\nSST: {sst:.2f} °C"}
            ))

            # ===== Status update =====
            if risk == "Safe":
                status.success(f"Day {row['Date']}: 🌿 Reef Safe (SST {sst:.2f} °C)")
            elif risk == "Watch":
                status.warning(f"Day {row['Date']}: ⚠️ Stress Watch (SST {sst:.2f} °C)")
            elif risk == "Warning":
                status.error(f"Day {row['Date']}: 🚨 Bleaching Warning (SST {sst:.2f} °C)")
            else:
                status.error(f"Day {row['Date']}: 🔴 CRITICAL Bleaching Alert (SST {sst:.2f} °C)")

            # ===== Chart update =====
            chart.add_rows(pd.DataFrame({"SST (°C)": [sst]}, index=[row["Date"]]))

            time.sleep(2)  # <-- speed: 2 seconds per simulated day

        # ===== Forecast Section =====
        if not os.path.exists(CSV_FORECAST):
            st.warning("⚠️ Forecast data not found. Please generate 'sst_sim_14days_with_forecast.csv'")
        else:
            st.subheader("📈 Observed vs Forecast SST")

            df_forecast = pd.read_csv(CSV_FORECAST)

            # Split observed vs forecast
            observed = df_forecast[df_forecast["Source"] == "Observed"]
            forecast = df_forecast[df_forecast["Source"] == "Forecast"]

            # Show line chart
            st.line_chart({
                "Observed SST": observed.set_index("Date")["SST_C"],
                "Forecast SST": forecast.set_index("Date")["SST_C"]
            })

            # Show early warning if forecast exceeds bleaching threshold
            bleaching_threshold = 30.5
            if forecast["SST_C"].max() > bleaching_threshold:
                st.error("🚨 Early Warning: Forecast predicts bleaching risk within 7 days!")
            else:
                st.success("✅ Forecast: Reef remains safe in the coming week.")
