import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor
from scipy.optimize import linprog
from datetime import datetime, timedelta

# 1. Spatio-Temporal & Infrastructure Data Generator
@st.cache_data
def load_enterprise_infrastructure_data():
    np.random.seed(42)
    center_lat, center_lon = 40.7128, -74.0060
    
    # Generate 4 weeks of historical baseline trends
    data = []
    for week in range(4):
        for _ in range(500):
            lat_offset = np.random.normal(0, 0.015)
            lon_offset = np.random.normal(0, 0.015)
            data.append({
                "Week_Index": week,
                "Latitude": center_lat + lat_offset,
                "Longitude": center_lon + lon_offset,
            })
    df = pd.DataFrame(data)
    
    # Generate Mock Fixed Sensor Apparatus Network
    sensor_types = ['CCTV_Camera', 'ALPR_Scanner', 'Acoustic_IoT']
    sensors = []
    for i in range(45): # 45 physical hardware installations across the landscape
        lat_offset = np.random.uniform(-0.03, 0.03)
        lon_offset = np.random.uniform(-0.03, 0.03)
        sensors.append({
            "Sensor_ID": f"SNS-{1000 + i}",
            "Sensor_Type": np.random.choice(sensor_types),
            "Latitude": center_lat + lat_offset,
            "Longitude": center_lon + lon_offset,
            "Coverage_Radius_Deg": 0.003, # ~330 meter coverage field radius
            "Status": np.random.choice(['Active', 'Active', 'Active', 'Maintenance'])
        })
    return df, pd.DataFrame(sensors)

st.set_page_config(page_title="Infrastructure Command Engine", layout="wide")
st.title("⚖️ Physical Infrastructure & Deployment Optimization Engine")
st.markdown("Map camera and sensor observation networks against machine learning forecasts to isolate systemic blind spots.")

df, sensor_df = load_enterprise_infrastructure_data()

# ========================================================
# BACKGROUND PROCESSING: RISK PREDICTION BINS
# ========================================================
df['Grid_Lat_Bin'] = df['Latitude'].round(2)
df['Grid_Lon_Bin'] = df['Longitude'].round(2)
grid_history = df.groupby(['Grid_Lat_Bin', 'Grid_Lon_Bin', 'Week_Index']).size().reset_index(name='Count')
features_df = grid_history.pivot(index=['Grid_Lat_Bin', 'Grid_Lon_Bin'], columns='Week_Index', values='Count').fillna(0).reset_index()

# Train baseline ML Forecaster
X_train = features_df[].values
y_train = features_df.values
forecaster = RandomForestRegressor(n_estimators=30, random_state=42).fit(X_train, y_train)
features_df['Predicted_Volume'] = forecaster.predict(features_df[].values)
forecast_df = features_df[features_df['Predicted_Volume'] > 0.5].copy()

# Navigation Interfaces
tab_sensor, tab_constraints = st.tabs(["📡 Sensor Network Mapping & Blind Spots", "🚦 Constrained Resource Deployment"])

# --------------------------------------------------------
# TAB 1: SENSOR NETWORK MAPPING & BLIND SPOTS
# --------------------------------------------------------
with tab_sensor:
    st.header("Hardware Sensor Apparatus vs. Forecasted Risk Overlay")
    st.markdown("This matrix cross-references active sensor footprints with next-week volume forecasts to locate **high-risk blind spots** (sectors lacking electronic eyes).")
    
    # Calculate Sensor Proximity for every forecast grid box
    blind_spot_flags = []
    sensor_counts_per_grid = []
    
    for idx, row in forecast_df.iterrows():
        # Find sensors inside a threshold radius of this grid cell center
        distances = np.sqrt((sensor_df['Latitude'] - row['Grid_Lat_Bin'])**2 + (sensor_df['Longitude'] - row['Grid_Lon_Bin'])**2)
        active_sensors = sensor_df[(distances <= 0.015) & (sensor_df['Status'] == 'Active')]
        
        sensor_counts_per_grid.append(len(active_sensors))
        # If expected volume is high (>5) but active sensor count is 0, flag as Critical Blind Spot
        if row['Predicted_Volume'] > 5.0 and len(active_sensors) == 0:
            blind_spot_flags.append("CRITICAL BLIND SPOT")
        else:
            blind_spot_flags.append("Observed Sector")
            
    forecast_df['Active_Sensors_In_Range'] = sensor_counts_per_grid
    forecast_df['Observational_Status'] = blind_spot_flags
    
    critical_blind_spots = forecast_df[forecast_df['Observational_Status'] == "CRITICAL BLIND SPOT"]
    
    s_kpi1, s_kpi2, s_kpi3 = st.columns(3)
    s_kpi1.metric("Total Mapped Sensor Assets", len(sensor_df))
    s_kpi2.metric("Sensors Online & Transmitting", len(sensor_df[sensor_df['Status'] == 'Active']))
    s_kpi3.metric("High-Risk Structural Blind Spots", len(critical_blind_spots), delta=f"{len(critical_blind_spots)} Areas Vulnerable", delta_color="inverse")

    # Render Infrastructure Overlay Map
    st.subheader("Spatio-Infrastructure Overlay System Matrix")
    
    fig_infra = go.Figure()
    # Trace 1: Forecasted Crime Risks
    fig_infra.add_trace(go.Scattermapbox(
        lat=forecast_df['Grid_Lat_Bin'], lon=forecast_df['Grid_Lon_Bin'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=forecast_df['Predicted_Volume'] * 2.5,
            color=forecast_df['Active_Sensors_In_Range'],
            colorscale='YlOrRd', reversearray=True,
            showscale=True,
            colorbar=dict(title="Active Sensors Nearby", x=0.02, y=0.5)
        ),
        text=forecast_df['Observational_Status'] + "<br>Expected: " + forecast_df['Predicted_Volume'].round(1).astype(str),
        name='Forecast Risk Grid'
    ))
    # Trace 2: Physical Sensor Assets Locations
    fig_infra.add_trace(go.Scattermapbox(
        lat=sensor_df['Latitude'], lon=sensor_df['Longitude'],
        mode='markers',
        marker=go.scattermapbox.Marker(size=10, color='cyan', symbol='circle'),
        text=sensor_df['Sensor_ID'] + " (" + sensor_df['Sensor_Type'] + ")",
        name='Sensor Hardware Node'
    ))
    
    fig_infra.update_layout(
        mapbox=dict(style="carto-darkmatter", center=dict(lat=center_lat, lon=center_lon), zoom=11.2),
        margin=dict(l=0, r=0, t=30, b=0), height=600, showlegend=True
    )
    st.plotly_chart(fig_infra, use_container_width=True)

# --------------------------------------------------------
# TAB 2: CONSTRAINED RESOURCE DEPLOYMENT
# --------------------------------------------------------
with tab_constraints:
    st.header("Operational Deployment Optimization Engine")
    st.markdown("Real-world dispatch requires handling tactical boundary constraints. This module optimizes fleet resource allocation while respecting localized priority conditions.")
    
    # Real-World Operational Parameters Panel
    col_con1, col_con2, col_con3 = st.columns(3)
    with col_con1:
        total_fleet = st.number_input("Total Unit Pool Budget", min_value=10, max_value=500, value=120)
    with col_con2:
        min_per_blind_spot = st.slider("Min Fleet Units Required inside Blind Spots (Safety Minimum)", 0, 5, 2)
    with col_con3:
        commute_cap = st.slider("Logistical Upper Cap (Max Units per Single Sector)", 5, 30, 12)
        
    # --- Advanced Linear Programming Setup ---
    # Objective function: Minimize negative risk coefficients
    c = -forecast_df['Predicted_Volume'].values
    n_sectors = len(c)
    
    # Constraint 1: Global fleet limit constraint (sum(x) <= total_fleet)
    A_ub = [np.ones(n_sectors)]
    b_ub = [total_fleet]
    
    # Boundary Setup (0 <= x <= commute_cap)
    bounds = []
    for idx, row in forecast_df.iterrows():
        # Inject constraint: If it is a critical blind spot, force it to receive at least the minimum required safety units
        lower_bound = min_per_blind_spot if row['Observational_Status'] == "CRITICAL BLIND SPOT" else 0
        bounds.append((lower_bound, commute_cap))
        
    # Solve linear matrix system using HiGHS simplex optimizer
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
    
    if res.success:
        forecast_df['Optimized_Deployment'] = np.round(res.x).astype(int)
        
        # Display Comparative Distribution Matrix
        st.subheader("Constrained Response Plan Strategy Breakdown")
        col_res1, col_res2 = st.columns([2, 1])
        
        with col_res1:
            fig_dep = px.bar(
                forecast_df[forecast_df['Optimized_Deployment'] > 0].sort_values(by='Optimized_Deployment', ascending=False),
                x='Grid_Lat_Bin', y='Optimized_Deployment', color='Observational_Status',
                title="Units Assigned per Sector Grid Box Cross-Referenced with Sensor State",
                labels={'Optimized_Deployment': 'Units Stationed', 'Grid_Lat_Bin': 'Sector Lat Center'}
            )
            st.plotly_chart(fig_dep, use_container_width=True)
            
        with col_res2:
            st.markdown("### Deployment Execution Checks")
            st.write(f"✔️ **Budget Limit:** {forecast_df['Optimized_Deployment'].sum()} / {total_fleet} Units Deployed")
            st.write(f"✔️ **Max Capacity Boundary:** Within user-defined limit of {commute_cap} units maximum per grid sector.")
            
            blind_spot_coverage = forecast_df[forecast_df['Observational_Status'] == "CRITICAL BLIND SPOT"]['Optimized_Deployment'].sum()
            st.write(f"🚨 **Blind Spot Unit Allocation:** {blind_spot_coverage} units sent directly to unmonitored sectors.")
            
            st.dataframe(forecast_df[['Grid_Lat_Bin', 'Grid_Lon_Bin', 'Predicted_Volume', 'Observational_Status', 'Optimized_Deployment']]
                         .sort_values(by='Optimized_Deployment', ascending=False).head(8), use_container_width=True)
    else:
        st.error("Optimization failed. Constraints are mutually exclusive. Reduce the Blind Spot Safety Minimum or increase Total Fleet Units.")
  
