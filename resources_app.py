import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
from scipy.optimize import linprog
import io

# 1. Spatio-Temporal Data Generation Engine
@st.cache_data
def load_comprehensive_platform_data():
    np.random.seed(42)
    categories = ['Property', 'Violent', 'Cyber', 'Statutory/Regulatory']
    base_date = datetime(2026, 4, 6)
    center_lat, center_lon = 40.7128, -74.0060
    
    data = []
    for week in range(8):
        current_week_date = base_date + timedelta(weeks=week)
        incidents_this_week = 450 + (week * 35) 
        
        for _ in range(incidents_this_week):
            cat = np.random.choice(categories)
            hour = np.random.randint(0, 24)
            lat_offset = np.random.normal(0, 0.015)
            lon_offset = np.random.normal(0, 0.015)
                
            data.append({
                "Week_Index": week,
                "Date_String": current_week_date.strftime('%Y-%m-%d'),
                "Category": cat,
                "Hour_of_Day": hour,
                "Latitude": center_lat + lat_offset,
                "Longitude": center_lon + lon_offset,
            })
    return pd.DataFrame(data)

st.set_page_config(page_title="Command Risk Optimization Platform", layout="wide")
st.title("⚖️ Enterprise Statute Analytics & Resource Optimization Engine")
st.markdown("System operations pipeline including ML forecasting, automated alert triggers, linear resource optimization, and data compilation.")

df = load_comprehensive_platform_data()

# ========================================================
# BACKGROUND PROCESSING: FORECASTING ENGINE
# ========================================================
df['Grid_Lat_Bin'] = df['Latitude'].round(2)
df['Grid_Lon_Bin'] = df['Longitude'].round(2)
grid_history = df.groupby(['Grid_Lat_Bin', 'Grid_Lon_Bin', 'Week_Index']).size().reset_index(name='Count')
features_df = grid_history.pivot(index=['Grid_Lat_Bin', 'Grid_Lon_Bin'], columns='Week_Index', values='Count').fillna(0).reset_index()

# Train predictive model
X_train = features_df[[0, 1, 2, 3, 4, 5]].values
y_train = features_df[6].values
forecaster = RandomForestRegressor(n_estimators=50, random_state=42).fit(X_train, y_train)

# Predict next horizon week
X_predict = features_df[[1, 2, 3, 4, 5, 6]].values
features_df['Predicted_Volume'] = forecaster.predict(X_predict)
features_df['Growth_Velocity'] = features_df['Predicted_Volume'] - features_df[7]
forecast_df = features_df[features_df['Predicted_Volume'] > 0.5].copy()

# ========================================================
# INTERFACE NAVIGATION TABS
# ========================================================
tab_alert, tab_opt, tab_report = st.tabs([
    "🚨 Webhook Threat Alerting", 
    "🧮 Resource Allocation Optimizer", 
    "📋 Strategic Performance Reporting"
])

# --------------------------------------------------------
# TAB 1: WEBHOOK THREAT ALERTING MODULE
# --------------------------------------------------------
with tab_alert:
    st.header("Real-Time Incident Webhook Threshold Evaluator")
    st.markdown("This module monitors projected growth velocities. If an area's spike rate crosses a pre-set security limit, the engine logs the anomaly and prepares a payload alert.")
    
    velocity_threshold = st.slider("Select Anomaly Velocity Trigger Limit (Expected Incident Spike)", 1.0, 15.0, 5.0, step=0.5)
    
    # Filter cells crossing the threshold limit
    triggered_alerts = forecast_df[forecast_df['Growth_Velocity'] >= velocity_threshold].copy()
    
    a_kpi1, a_kpi2 = st.columns(2)
    a_kpi1.metric("Monitored Sectors", len(forecast_df))
    a_kpi2.metric("Triggered Active Exceptions", len(triggered_alerts), delta=f"{len(triggered_alerts)} active alerts", delta_color="inverse")
    
    if not triggered_alerts.empty:
        st.subheader("Active Alarm Queue Payloads")
        for idx, row in triggered_alerts.head(3).iterrows():
            mock_payload = {
                "event": "CRITICAL_GROWTH_SPIKE_DETECTED",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "coordinates": {"lat": row['Grid_Lat_Bin'], "lon": row['Grid_Lon_Bin']},
                "metrics": {"historical_baseline": float(row[7]), "forecasted_volume": float(row['Predicted_Volume']), "velocity_deviation": float(row['Growth_Velocity'])}
            }
            with st.expander(f"🔴 EXCEPTION: Sector ({row['Grid_Lat_Bin']:.2f}, {row['Grid_Lon_Bin']:.2f}) Velocity +{row['Growth_Velocity']:.2f}"):
                st.code(mock_payload, language="json")
                if st.button("Manually Dispatch Payload to Endpoint", key=f"btn_{idx}"):
                    st.success("JSON Payload successfully routed to legal endpoint with Status Code 202 (Accepted).")
    else:
        st.success("System normal. No sectors have passed the current velocity threshold limits.")

# --------------------------------------------------------
# TAB 2: RESOURCE ALLOCATION OPTIMIZER
# --------------------------------------------------------
with tab_opt:
    st.header("Linear Optimization Resource Allocator")
    st.markdown("Using a **Simplex Optimization Engine**, this module distributes a fixed total pool of personnel units across high-risk sectors to maximize overall safety coverage.")
    
    total_staff = st.number_input("Total Fleet Units Available for Deployment", min_value=5, max_value=500, value=100)
    max_per_sector = st.slider("Maximum Fleet Density Cap Per Grid Sector", 5, 50, 15)
    
    # Optimization Engine Formulation
    # Maximize risk coverage == Minimize negative predicted volume counts
    c = -forecast_df['Predicted_Volume'].values  # Negative coefficients for maximization
    A_ub = np.ones((1, len(c)))                 # Constraint matrix row: sum(units) <= total_staff
    b_ub = [total_staff]
    
    # Boundary constraints per cell (0 <= units <= max_per_sector)
    bounds = [(0, max_per_sector) for _ in range(len(c))]
    
    # Execute Linear Programming Optimizer
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
    
    if res.success:
        forecast_df['Allocated_Units'] = np.round(res.x).astype(int)
        
        opt_map_df = forecast_df[forecast_df['Allocated_Units'] > 0].copy()
        
        st.subheader("Optimal Fleet Strategy Plan")
        fig_opt = px.scatter_mapbox(
            opt_map_df, lat="Grid_Lat_Bin", lon="Grid_Lon_Bin",
            size="Allocated_Units", color="Allocated_Units",
            color_continuous_scale=px.colors.sequential.Bluyl,
            zoom=11.0, height=500, mapbox_style="carto-positron",
            title="Strategic Personnel Deployment Bins Map"
        )
        st.plotly_chart(fig_opt, use_container_width=True)
    else:
        st.error("Optimization Engine encountered an error solving constraints.")

# --------------------------------------------------------
# TAB 3: STRATEGIC PERFORMANCE REPORTING
# --------------------------------------------------------
with tab_report:
    st.header("Data Compilation Ledger Generator")
    st.markdown("Export operational data summaries, ML forecast trends, and automated deployment parameters.")
    
    # Build text data ledger structure
    report_stream = io.StringIO()
    report_stream.write(f"========================================================\n")
    report_stream.write(f"SYSTEM RISK PERFORMANCE DATA COMPILATION LEDGER\n")
    report_stream.write(f"GENERATION TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report_stream.write(f"========================================================\n\n")
    report_stream.write(f"1. CORE BASELINE EXECUTION PARAMETERS:\n")
    report_stream.write(f"   - Total Documented Historic Dataset Records: {len(df)} counts\n")
    report_stream.write(f"   - Total Active Monitored Grid Sectors: {len(forecast_df)} sectors\n")
    report_stream.write(f"   - Forecast Global Volume for Target Window: {forecast_df['Predicted_Volume'].sum():.2f} events\n\n")
    report_stream.write(f"2. STRATEGIC ALLOCATION PARAMETERS:\n")
    report_stream.write(f"   - Available Personnel Fleet Baseline: {total_staff} units\n")
    if 'Allocated_Units' in forecast_df.columns:
        report_stream.write(f"   - Total Units Effectively Deployed: {forecast_df['Allocated_Units'].sum()} units\n")
        report_stream.write(f"   - Maximum Local Cluster Concentration: {forecast_df['Allocated_Units'].max()} units\n")
    
    st.text_area("Live Data Compiled Ledger Preview", report_stream.getvalue(), height=300)
    
    # Download Action Button
    st.download_button(
        label="Download System Compilation Ledger (.TXT)",
        data=report_stream.getvalue(),
        file_name=f"Risk_System_Data_Compilation_{datetime.now().strftime('%Y%m%d')}.txt",
        mime="text/plain"
    )

