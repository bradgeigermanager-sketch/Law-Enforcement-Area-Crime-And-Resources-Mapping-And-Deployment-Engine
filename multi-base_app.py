import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor
from scipy.optimize import linprog
from datetime import datetime
import math

# 1. Multi-Base & Infrastructure Matrix Data Generator
@st.cache_data
def load_enterprise_multibase_data():
    np.random.seed(42)
    center_lat, center_lon = 40.7128, -74.0060
    
    # Define 3 Distributed Fleet Precinct Bases (Origin Matrix Nodes)
    bases = {
        "Precinct Alpha (North)": {"lat": 40.7450, "lon": -74.0010, "fleet": 60},
        "Precinct Bravo (South)": {"lat": 40.6850, "lon": -74.0120, "fleet": 50},
        "Precinct Charlie (West)": {"lat": 40.7100, "lon": -74.0550, "fleet": 40}
    }
    
    # Historical Crime Volume Logs
    data = []
    for week in range(3):
        for _ in range(450):
            lat_offset = np.random.normal(0, 0.015)
            lon_offset = np.random.normal(0, 0.015)
            data.append({
                "Week_Index": week,
                "Latitude": center_lat + lat_offset,
                "Longitude": center_lon + lon_offset,
            })
    df = pd.DataFrame(data)
    
    # Spatial Electronic Sensor Networks Network Array
    sensor_types = ['CCTV_Camera', 'ALPR_Scanner', 'Acoustic_IoT']
    sensors = []
    for i in range(60):
        lat_offset = np.random.uniform(-0.035, 0.035)
        lon_offset = np.random.uniform(-0.035, 0.035)
        sensors.append({
            "Sensor_ID": f"SNS-{3000 + i}",
            "Sensor_Type": np.random.choice(sensor_types),
            "Latitude": center_lat + lat_offset,
            "Longitude": center_lon + lon_offset,
            "State": "Active"
        })
        
    return df, pd.DataFrame(sensors), bases

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000 # Earth radius in meters
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2) * math.sin(dl/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# Main UI Panel Setup
st.set_page_config(page_title="Multi-Base Tactical Platform", layout="wide")
st.title("⚖️ Multi-Base Logistics & Auto-Escalation Threat Engine")
st.markdown("Automate linear allocation cross-routing across multiple deployment bases while executing cascading logic triggers.")

df, sensor_df, base_network = load_enterprise_multibase_data()

# ========================================================
# RECURSIVE FORECAST MATRIX ENGINE RUNNER
# ========================================================
df['Grid_Lat_Bin'] = df['Latitude'].round(2)
df['Grid_Lon_Bin'] = df['Longitude'].round(2)
grid_history = df.groupby(['Grid_Lat_Bin', 'Grid_Lon_Bin', 'Week_Index']).size().reset_index(name='Count')
features_df = grid_history.pivot(index=['Grid_Lat_Bin', 'Grid_Lon_Bin'], columns='Week_Index', values='Count').fillna(0).reset_index()

forecaster = RandomForestRegressor(n_estimators=20, random_state=42).fit(features_df[].values, features_df.values)
features_df['Predicted_Volume'] = forecaster.predict(features_df[].values)
forecast_df = features_df[features_df['Predicted_Volume'] > 0.5].copy()

# Interface Workspace Splits
tab_escalation, tab_multibase = st.tabs(["⚡ Cascading Auto-Escalation Engine", "🏢 Multi-Base Fleet Cost Allocation"])

# --------------------------------------------------------
# TAB 1: CASCADING AUTO-ESCALATION ENGINE
# --------------------------------------------------------
with tab_escalation:
    st.header("Real-Time Incident State Escalation Matrices")
    st.markdown("Single failures are handled locally. This rule engine looks for **compound failures** (where high predicted crime overlaps with multiple hardware drops in the same grid) to automatically upgrade sectors to higher response tiers.")
    
    sim_packet_loss = st.slider("Simulate Live Network Breakdown Ratio (%)", 10, 90, 40, step=5)
    
    # Process Stochastic Sensor Vitality Drops
    np.random.seed(datetime.now().second)
    sensor_df['Live_Status'] = sensor_df['State'].apply(
        lambda x: 'OFFLINE' if np.random.uniform(0, 100) < sim_packet_loss else 'ONLINE'
    )
    
    # Rule Evaluation Matrix
    escalated_tiers = []
    reasons = []
    color_codes = []
    
    for idx, row in forecast_df.iterrows():
        # Check active sensor nodes within range
        dist = np.sqrt((sensor_df['Latitude'] - row['Grid_Lat_Bin'])**2 + (sensor_df['Longitude'] - row['Grid_Lon_Bin'])**2)
        total_sensors = len(sensor_df[dist <= 0.015])
        offline_sensors = len(sensor_df[(dist <= 0.015) & (sensor_df['Live_Status'] == 'OFFLINE')])
        
        # Rule Matrix Evaluator
        if row['Predicted_Volume'] >= 7.0 and offline_sensors >= 2:
            escalated_tiers.append("TIER_3_CRITICAL")
            reasons.append(f"High Vol ({row['Predicted_Volume']:.1f}) + Compound Hardware Loss (-{offline_sensors} Nodes)")
            color_codes.append("#FF0033")
        elif row['Predicted_Volume'] >= 4.0 or offline_sensors >= 1:
            escalated_tiers.append("TIER_2_REGIONAL")
            reasons.append("Moderate Vol Growth or Local Hardware Loss")
            color_codes.append("#FFA500")
        else:
            escalated_tiers.append("TIER_1_LOCAL")
            reasons.append("Standard Baseline Activity Profile")
            color_codes.append("#00FFCC")
            
    forecast_df['Escalation_Tier'] = escalated_tiers
    forecast_df['Trigger_Reason'] = reasons
    forecast_df['Marker_Color'] = color_codes
    
    # Render Diagnostics Indicators
    t3_count = len(forecast_df[forecast_df['Escalation_Tier'] == "TIER_3_CRITICAL"])
    t2_count = len(forecast_df[forecast_df['Escalation_Tier'] == "TIER_2_REGIONAL"])
    
    e_kpi1, e_kpi2, e_kpi3 = st.columns(3)
    e_kpi1.metric("Standard Local State (Tier 1)", len(forecast_df) - t2_count - t3_count)
    e_kpi2.metric("Regional Active Warnings (Tier 2)", t2_count, delta=f"{t2_count} Areas Active")
    e_kpi3.metric("Tactical Escalations (Tier 3 Critical)", t3_count, delta=f"{t3_count} Severe Exceptions", delta_color="inverse")
    
    # Draw Threat Matrix Map Layout
    st.subheader("Automated Escalation Threat Space Map")
    fig_esc_map = go.Figure()
    
    fig_esc_map.add_trace(go.Scattermapbox(
        lat=forecast_df['Grid_Lat_Bin'], lon=forecast_df['Grid_Lon_Bin'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=forecast_df['Predicted_Volume'] * 2.5,
            color=forecast_df['Marker_Color']
        ),
        text=forecast_df['Escalation_Tier'] + "<br>Reason: " + forecast_df['Trigger_Reason'],
        name='Grid Threat Spectrum'
    ))
    
    fig_esc_map.update_layout(
        mapbox=dict(style="carto-darkmatter", center=dict(lat=40.7128, lon=-74.0060), zoom=11.0),
        margin=dict(l=0, r=0, t=30, b=0), height=550
    )
    st.plotly_chart(fig_esc_map, use_container_width=True)

# --------------------------------------------------------
# TAB 2: MULTI-BASE FLEET COST ALLOCATION
# --------------------------------------------------------
with tab_multibase:
    st.header("Multi-Origin Simplex Cost Optimization Model")
    st.markdown("With multiple precincts available, the platform calculates drive times from **every base** to **every grid cell** to find the most efficient routing configuration.")
    
    speed_kmh = st.slider("Operational Surface Velocity Speed (KM/H)", 20, 70, 40)
    max_mins_cutoff = st.number_input("Maximum Response Cutoff Threshold (Minutes)", min_value=5, max_value=45, value=15)
    
    # 1. Compute Transit Matrix Dimensions
    # Rows = Base-to-Grid combinations; Columns = Individual sector targets
    base_names = list(base_network.keys())
    n_bases = len(base_names)
    n_grids = len(forecast_df)
    n_vars = n_bases * n_grids # Multi-variable array configuration
    
    # Build cost parameters list based on calculated travel times
    cost_coefficients = []
    grid_index_map = forecast_df.reset_index(drop=True)
    
    # Build a lookup table tracking response times across all combinations
    transit_matrix_lookup = []
    
    for b_idx, b_name in enumerate(base_names):
        b_lat = base_network[b_name]["lat"]
        b_lon = base_network[b_name]["lon"]
        
        for g_idx, row in grid_index_map.iterrows():
            meters = calculate_haversine_distance(b_lat, b_lon, row['Grid_Lat_Bin'], row['Grid_Lon_Bin'])
            mins = ((meters / 1000) / speed_kmh) * 60 * 1.3
            
            transit_matrix_lookup.append({
                "Base": b_name, "Lat": row['Grid_Lat_Bin'], "Lon": row['Grid_Lon_Bin'],
                "Mins": mins, "Risk": row['Predicted_Volume'], "Escalation": row['Escalation_Tier']
            })
            
            # Optimization Goal: Maximize risk coverage while keeping drive times low
            # Cost weight = (1 / Risk Level) * Travel Minutes
            weight = (1.0 / (row['Predicted_Volume'] + 0.1)) * mins
            cost_coefficients.append(weight)
            
    matrix_df = pd.DataFrame(transit_matrix_lookup)
    
    # 2. Linear Optimization Constraint Setup
    A_ub = []
    b_ub = []
    
    # Constraint A: Do not exceed each precinct's maximum vehicle capacity
    for b_idx, b_name in enumerate(base_names):
        base_constraint_row = np.zeros(n_vars)
        # Set values to 1 for variables belonging to this specific base
        base_constraint_row[b_idx*n_grids : (b_idx+1)*n_grids] = 1
        A_ub.append(base_constraint_row)
        b_ub.append(base_network[b_name]["fleet"])
        
    # Boundary Constraints Engine (0 <= units <= max_cap)
    var_bounds = []
    idx_counter = 0
    for b_name in base_names:
        for g_idx, row in grid_index_map.iterrows():
            current_transit = matrix_df.iloc[idx_counter]["Mins"]

  
