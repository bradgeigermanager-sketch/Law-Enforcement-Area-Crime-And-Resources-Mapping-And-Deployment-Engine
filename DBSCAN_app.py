import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
from sklearn.cluster import DBSCAN
from shapely.geometry import Point, Polygon
import math

# 1. Advanced Spatial & Categorical Mock Data Generator
@st.cache_data
def load_complex_spatial_data():
    np.random.seed(42)
    categories = ['Property', 'Violent', 'Cyber', 'Statutory/Regulatory']
    statutes = {
        'Property': ['Larceny-Theft', 'Burglary', 'Motor Vehicle Theft'],
        'Violent': ['Aggravated Assault', 'Robbery', 'Homicide'],
        'Cyber': ['Identity Theft', 'Phishing Networks'],
        'Statutory/Regulatory': ['Traffic Infractions', 'Tax Evasion']
    }
    
    # Define 3 distinct Neighborhood Polygons (WGS84 Coordinates roughly around a city center)
    # Each neighborhood has a defined population baseline
    neighborhood_defs = {
        "Downtown District": {
            "pop": 85000,
            "poly": Polygon([(40.70, -74.02), (40.74, -74.02), (40.74, -73.98), (40.70, -73.98)]),
            "centers": [(40.72, -74.00), (40.715, -74.01)] # Primary hot-spot coordinates
        },
        "North Suburbs": {
            "pop": 120000,
            "poly": Polygon([(40.74, -74.02), (40.78, -74.02), (40.78, -73.98), (40.74, -73.98)]),
            "centers": [(40.76, -73.99)]
        },
        "West Industrial Zone": {
            "pop": 35000,
            "poly": Polygon([(40.70, -74.06), (40.74, -74.06), (40.74, -74.02), (40.70, -74.02)]),
            "centers": [(40.71, -74.045)]
        }
    }
    
    data = []
    # Generate 5,000 unique coordinate-based criminal incidents
    for i in range(5000):
        cat = np.random.choice(categories)
        stat = np.random.choice(statutes[cat])
        
        # Select a random neighborhood to place the crime
        n_name = np.random.choice(list(neighborhood_defs.keys()))
        n_info = neighborhood_defs[n_name]
        
        # Pull a random center point from that neighborhood and add Gaussian noise
        center = n_info["centers"][np.random.choice(len(n_info["centers"]))]
        lat = np.random.normal(center[0], 0.008)
        lon = np.random.normal(center[1], 0.008)
        
        data.append({
            "Incident_ID": 100000 + i,
            "Statute": stat,
            "Category": cat,
            "Latitude": lat,
            "Longitude": lon,
            "Assigned_Neighborhood": n_name # Used later to verify spatial joins
        })
        
    return pd.DataFrame(data), neighborhood_defs

# App Core Initialization
st.set_page_config(page_title="Spatial Numeracy & Clustering Engine", layout="wide")
st.title("⚖️ Spatial Crime Analytics & Hot-Spot Clustering Engine")
st.markdown("Execute automated density clustering (DBSCAN) and calculate polygon-isolated crime metrics per 100k citizens.")

df, neighborhoods = load_complex_spatial_data()

# Render tabs breaking out our operational modules
tab1, tab2 = st.tabs(["🎯 Module A: DBSCAN Spatial Clustering", "🗺️ Module B: Neighborhood Rate Spatial Join"])

# ==========================================
# MODULE A: DBSCAN SPATIAL CLUSTERING
# ==========================================
with tab1:
    st.header("Density-Based Cluster Discovery Pipeline")
    st.markdown("DBSCAN groups points closely packed together while identifying sparse points as background outlier noise. This allows the system to find crime clusters without needing preset neighborhood boundaries.")
    
    # Interactive Engine Parameters
    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)
    with col_ctrl1:
        selected_cat = st.selectbox("Select Target Analytics Category", ["All Crimes"] + list(df['Category'].unique()))
    with col_ctrl2:
        # Distance calculation helper: 0.001 degrees is roughly 111 meters
        cluster_radius_meters = st.slider("Maximum Scanning Radius (Epsilon Distance in Meters)", 50, 1000, 300, step=50)
        eps_degrees = (cluster_radius_meters / 1000) / 111.32
    with col_ctrl3:
        min_samples = st.number_input("Minimum Incident Density Threshold (Min Points per Cluster)", min_value=2, max_value=200, value=25)
        
    # Filter working frame based on user constraints
    working_df = df.copy() if selected_cat == "All Crimes" else df[df['Category'] == selected_cat].copy()
    
    if len(working_df) > 1:
        # Extract physical coordinate matrices for the Scikit-Learn pipeline
        coords = working_df[['Latitude', 'Longitude']].values
        
        # Execute DBSCAN Engine
        db = DBSCAN(eps=eps_degrees, min_samples=min_samples, metric='euclidean').fit(coords)
        working_df['Cluster_ID'] = db.labels_
        
        # Calculate system statistics
        total_clusters = len(set(db.labels_)) - (1 if -1 in db.labels_ else 0)
        noise_points = np.sum(db.labels_ == -1)
        
        # UI Metrics Display Panel
        c_kpi1, c_kpi2, c_kpi3 = st.columns(3)
        c_kpi1.metric("Identified High-Density Clusters", total_clusters)
        c_kpi2.metric("Clustered High-Frequency Points", f"{len(working_df) - noise_points:,}")
        c_kpi3.metric("Scattered Outlier Events (Noise)", f"{noise_points:,}")
        
        # Map Display Preparation
        # Format names for the map legend: Label -1 as "Background Noise", others as "Cluster X"
        working_df['Map_Display_Label'] = working_df['Cluster_ID'].apply(
            lambda x: 'Background Non-Cluster Activity' if x == -1 else f'High-Density Cluster Group {x}'
        )
        
        # Render Interactive Mapbox Visual
        fig_cluster_map = px.scatter_mapbox(
            working_df, lat="Latitude", lon="Longitude", 
            color="Map_Display_Label", hover_name="Statute",
            color_discrete_sequence=px.colors.qualitative.Alphabet,
            zoom=11.5, height=650, mapbox_style="carto-positron",
            title="DBSCAN Automated Spatial Hot-Spot Allocations"
        )
        fig_cluster_map.update_traces(marker=dict(size=6, opacity=0.7))
        st.plotly_chart(fig_cluster_map, use_container_width=True)
    else:
        st.error("The filtered dataset contains insufficient data vectors to initialize clustering.")

# ==========================================
# MODULE B: NEIGHBORHOOD RATE SPATIAL JOIN
# ==========================================
with tab2:
    st.header("Localized Geographic Boundary Spatial Join & Normalization")
    st.markdown("Raw charge numbers can distort reality if a busy commercial district is compared directly to a quiet residential suburb without adjusting for population. This module maps each incident coordinate to its corresponding neighborhood boundary to calculate population-adjusted rates.")
    
    # Database Engine Simulation: Compute Point-in-Polygon spatial joins
    spatial_join_records = []
    
    for idx, row in df.iterrows():
        p = Point(row['Latitude'], row['Longitude'])
        assigned_to_polygon = "Unmapped Territory / Outside Bounds"
        
        # Check intersections against defined boundaries
        for n_name, n_info in neighborhoods.items():
            if n_info["poly"].contains(p):
                assigned_to_polygon = n_name
                break
        
        spatial_join_records.append(assigned_to_polygon)
        
    df['Calculated_Polygon'] = spatial_join_records
    
    # Aggregate volumetric data per polygon boundary
    poly_summary = df[df['Calculated_Polygon'] != "Unmapped Territory / Outside Bounds"].groupby('Calculated_Polygon').size().reset_index(name='Raw Incident Count')
    
    # Inject baseline populations and compute rates normalized per 100k citizens
    poly_summary['Population Baseline'] = poly_summary['Calculated_Polygon'].map(lambda x: neighborhoods[x]['pop'])
    poly_summary['Rate per 100k Population'] = (poly_summary['Raw Incident Count'] / poly_summary['Population Baseline']) * 100000
    poly_summary = poly_summary.sort_values(by='Rate per 100k Population', ascending=False)
    
    # Render Two-Axis Analytical Summary Screen
    col_graph1, col_graph2 = st.columns(2)
    
    with col_graph1:
        st.subheader("Raw Volumetric Counts by Boundary")
        fig_raw_bar = px.bar(poly_summary, x='Calculated_Polygon', y='Raw Incident Count', 
                             color='Calculated_Polygon', text_auto=True,
                             title="Absolute Total of Filed Charges")
        st.plotly_chart(fig_raw_bar, use_container_width=True)
        
    with col_graph2:
        st.subheader("Normalized Risk Profile (Rate per 100k)")
        fig_rate_bar = px.bar(poly_summary, x='Calculated_Polygon', y='Rate per 100k Population', 
                              color='Calculated_Polygon', text_auto='.2f',
                              color_discrete_sequence=px.colors.qualitative.Set2,
                              title="Violations Scaled Proportionally to Population Density")
        st.plotly_chart(fig_rate_bar, use_container_width=True)
        
    # Print clean ledger data matrix
    st.subheader("Geospatial Join Ledger View")
    st.dataframe(poly_summary.style.format({
        'Raw Incident Count': '{:,}',
        'Population Baseline': '{:,}',
        'Rate per 100k Population': '{:,.2f}'
    }), use_container_width=True)
  
