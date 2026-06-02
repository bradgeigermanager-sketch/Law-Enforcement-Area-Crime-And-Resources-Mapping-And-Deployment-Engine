import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta

# 1. Advanced Spatio-Temporal Mock Data Generator
@st.cache_data
def load_spatio_temporal_forecast_data():
    np.random.seed(42)
    categories = ['Property', 'Violent', 'Cyber', 'Statutory/Regulatory']
    
    # Generate 8 weeks of historical incident points with an accelerating trend
    base_date = datetime(2026, 4, 6) # Starting point in recent timeline
    center_lat, center_lon = 40.7128, -74.0060
    
    data = []
    for week in range(8):
        current_week_date = base_date + timedelta(weeks=week)
        # Add volume acceleration to mimic shifting trends
        incidents_this_week = 400 + (week * 45) 
        
        for _ in range(incidents_this_week):
            cat = np.random.choice(categories)
            # Simulate a diurnal pattern: Violent crime shifts late; Statutory shifts early
            if cat == 'Violent':
                hour = int(np.random.beta(5, 2) * 24) # Skewed toward night hours
                lat_offset = np.random.normal(0.005, 0.012)
                lon_offset = np.random.normal(-0.005, 0.012)
            elif cat == 'Statutory/Regulatory':
                hour = int(np.random.beta(2, 5) * 24) # Skewed toward daytime business hours
                lat_offset = np.random.normal(-0.008, 0.01)
                lon_offset = np.random.normal(0.008, 0.01)
            else:
                hour = np.random.randint(0, 24)
                lat_offset = np.random.normal(0, 0.015)
                lon_offset = np.random.normal(0, 0.015)
                
            data.append({
                "Week_Index": week,
                "Date_String": current_week_date.strftime('%Y-%m-%d'),
                "Category": cat,
                "Hour_of_Day": hour,
                "Time_Slice": "Night Shift (18-06)" if hour >= 18 or hour < 6 else "Day Shift (06-18)",
                "Latitude": center_lat + lat_offset,
                "Longitude": center_lon + lon_offset,
                "Historical_Count_Weight": 1 # Target variable baseline tracker
            })
            
    return pd.DataFrame(data)

# App Architecture Setup
st.set_page_config(page_title="Spatio-Temporal Predictive Engine", layout="wide")
st.title("⚖️ Spatio-Temporal Tracking & Hotspot Forecasting Engine")
st.markdown("Track dynamic diurnal shifts through animated coordinate systems and calculate spatial risk projections for next-week incident volumes.")

df = load_spatio_temporal_forecast_data()

# Layout Splitter
tab1, tab2 = st.tabs(["⏳ Module C: Time-Series Diurnal Animation", "🔮 Module D: Predictive Spatial Forecasting"])

# ==========================================
# MODULE C: TIME-SERIES DIURNAL ANIMATION
# ==========================================
with tab1:
    st.header("Diurnal Velocity Analysis (Day vs. Night Density Shift)")
    st.markdown("Physical crime footprints are rarely static. This animation tracks how density matrices evolve hour-by-hour across distinct time slices.")
    
    selected_anim_cat = st.selectbox("Filter Animation Matrix by Category", ["All Matrix Categories"] + list(df['Category'].unique()))
    anim_df = df if selected_anim_cat == "All Matrix Categories" else df[df['Category'] == selected_anim_cat]
    
    # Sort dataset by time vectors to guarantee chronological frame rendering in Plotly
    anim_df = anim_df.sort_values(by='Hour_of_Day')
    
    # Render Mapbox Animation Engine
    fig_anim = px.scatter_mapbox(
        anim_df, lat="Latitude", lon="Longitude", 
        color="Time_Slice", hover_data=["Category", "Hour_of_Day"],
        animation_frame="Hour_of_Day", # Generates the interactive timeline playback controls
        color_discrete_map={"Day Shift (06-18)": "#FFA500", "Night Shift (18-06)": "#4B0082"},
        zoom=11.5, height=650, mapbox_style="carto-positron",
        title=f"Chronological Hourly Offense Fluidity: {selected_anim_cat}"
    )
    
    fig_anim.update_traces(marker=dict(size=8, opacity=0.6))
    # Optimize layout engine parameters for continuous playback frames
    fig_anim.update_layout(transition={'duration': 250})
    st.plotly_chart(fig_anim, use_container_width=True)

# ==========================================
# MODULE D: PREDICTIVE SPATIAL FORECASTING
# ==========================================
with tab2:
    st.header("Machine Learning Spatial Density Projections (Next-Week Forecast)")
    st.markdown("This engine segments the geographic coordinate plane into a structured spatial grid, analyzes multi-week historic incident velocities, and executes a **Random Forest Regression Pipeline** to predict localized grid densities for the upcoming week.")
    
    # 1. Geographic Grid Mesh Engine Allocation
    # Round off coordinates to construct uniform spatial prediction bins (~1.1km grid spacing)
    df['Grid_Lat_Bin'] = df['Latitude'].round(2)
    df['Grid_Lon_Bin'] = df['Longitude'].round(2)
    
    # Build out history matrices aggregated by location and time index
    grid_history = df.groupby(['Grid_Lat_Bin', 'Grid_Lon_Bin', 'Week_Index']).size().reset_index(name='Weekly_Incident_Count')
    
    # 2. Feature Engineering Pipeline
    # Pivot rows to track historical volume trajectories per grid box
    features_df = grid_history.pivot(index=['Grid_Lat_Bin', 'Grid_Lon_Bin'], columns='Week_Index', values='Weekly_Incident_Count').fillna(0).reset_index()
    
    # Build lag matrices: Use weeks 0-6 to predict week 7 volume
    X_train = features_df[[0, 1, 2, 3, 4, 5]].values
    y_train = features_df[6].values
    
    # Model Training
    forecaster = RandomForestRegressor(n_estimators=100, random_state=42)
    forecaster.fit(X_train, y_train)
    
    # 3. Next-Week Prediction Engine Pipeline
    # Shift time lag arrays forward: Use weeks 1-7 to estimate upcoming target week 8
    X_predict_next_week = features_df[[1, 2, 3, 4, 5, 6]].values
    features_df['Predicted_Next_Week_Volume'] = forecaster.predict(X_predict_next_week)
    
    # Calculate Variance Deviations to locate high-acceleration sectors
    features_df['Velocity_Acceleration_Risk'] = features_df['Predicted_Next_Week_Volume'] - features_df[6]
    
    # Filter out empty cells to keep the UI view clean
    plot_forecast_df = features_df[features_df['Predicted_Next_Week_Volume'] > 0.1].copy()
    
    # KPI Calculations
    total_predicted_load = plot_forecast_df['Predicted_Next_Week_Volume'].sum()
    highest_risk_cell = plot_forecast_df.loc[plot_forecast_df['Predicted_Next_Week_Volume'].idxmax()]
    
    f_kpi1, f_kpi2, f_kpi3 = st.columns(3)
    f_kpi1.metric("Predicted System-Wide Volume (Next Week)", f"{int(total_predicted_load):,} Charges")
    f_kpi2.metric("Peak Sector Coordinates", f"{highest_risk_cell['Grid_Lat_Bin']:.2f}N, {highest_risk_cell['Grid_Lon_Bin']:.2f}W")
    f_kpi3.metric("Max Expected Incidents in Single Cell", f"{highest_risk_cell['Predicted_Next_Week_Volume']:.1f} events")
    
    # Render Predictive Visualization Graph
    col_map, col_ledger = st.columns([3, 2])
    
    with col_map:
        fig_forecast = px.scatter_mapbox(
            plot_forecast_df, lat="Grid_Lat_Bin", lon="Grid_Lon_Bin",
            size="Predicted_Next_Week_Volume", color="Velocity_Acceleration_Risk",
            color_continuous_scale=px.colors.sequential.OrRd,
            zoom=11.2, height=550, mapbox_style="carto-positron",
            title="Spatio-Temporal Predictive Risks Matrix (Color scale represents volume shift velocity)",
            labels={'Velocity_Acceleration_Risk': 'Expected Growth Intensity'}
        )
        st.plotly_chart(fig_forecast, use_container_width=True)
        
    with col_ledger:
        st.subheader("High-Risk Structural Projections")
        ledger_view = plot_forecast_df[['Grid_Lat_Bin', 'Grid_Lon_Bin', 6, 'Predicted_Next_Week_Volume', 'Velocity_Acceleration_Risk']].copy()
        ledger_view.columns = ['Lat Bin', 'Lon Bin', 'Current Week Vol', 'Forecasted Vol', 'Growth Velocity']
        st.dataframe(ledger_view.sort_values(by='Forecasted Vol', ascending=False).head(10).style.format({
            'Current Week Vol': '{:.0f}',
            'Forecasted Vol': '{:.1f}',
            'Growth Velocity': '{:+.1f}'
        }), use_container_width=True)
      
