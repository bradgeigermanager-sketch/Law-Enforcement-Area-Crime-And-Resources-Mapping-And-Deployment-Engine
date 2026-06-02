import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats

# 1. Mock Data Generator matching our database design
def load_mock_legal_data():
    np.random.seed(42)
    categories = ['Property', 'Violent', 'Cyber', 'Statutory/Regulatory']
    statutes = {
        'Property': ['Larceny-Theft', 'Burglary', 'Motor Vehicle Theft', 'Fraud'],
        'Violent': ['Aggravated Assault', 'Robbery', 'Homicide'],
        'Cyber': ['Identity Theft', 'Phishing Networks', 'Ransomware Deployment'],
        'Statutory/Regulatory': ['Traffic Infractions', 'Tax Evasion', 'Licensing Violations']
    }
    
    data = []
    # Generate 5 years of historical baseline trends
    for year in range(2022, 2027):
        for cat in categories:
            for stat in statutes[cat]:
                # Base counts representing typical global distributions
                if cat == 'Property':
                    base = np.random.randint(8000, 15000)
                elif cat == 'Statutory/Regulatory':
                    base = np.random.randint(12000, 20000)
                elif cat == 'Cyber':
                    base = np.random.randint(3000, 7000) + (year - 2022) * 1500 # Simulating an upward trend
                else: # Violent
                    base = np.random.randint(1500, 4500)
                
                data.append({
                    "Year": year,
                    "Statute": stat,
                    "Category": cat,
                    "Charges Filed": int(base * np.random.uniform(0.9, 1.1))
                })
    return pd.DataFrame(data)

# 2. Main UI Engine App Configuration
st.set_page_config(page_title="Legal Statute Numeracy Engine", layout="wide")
st.title("⚖️ Legal Statute Numeracy & Charge Tracking Engine")
st.markdown("Analyze baseline deviations, comparative counts, and population-adjusted crime tracking metrics.")

df = load_mock_legal_data()

# Sidebar Configuration Controls
st.sidebar.header("Data Filter Matrix")
selected_year = st.sidebar.selectbox("Analysis Target Year", sorted(df['Year'].unique(), reverse=True))
population = st.sidebar.number_input("Jurisdiction Population", min_value=10000, max_value=50000000, value=1000000)

# Filter Dataset based on configurations
year_df = df[df['Year'] == selected_year].copy()
total_charges = year_df['Charges Filed'].sum()

# 3. Statistical Numeracy Engine Calculations
year_df['Rate per 100k'] = (year_df['Charges Filed'] / population) * 100000
year_df['Percentage of Total %'] = (year_df['Charges Filed'] / total_charges) * 100
# Calculate Z-Scores to find anomalous statistical spikes
year_df['Z-Score'] = stats.zscore(year_df['Charges Filed'])

# Top Level KPI Row
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Total Documented Charges", f"{total_charges:,}")
kpi2.metric("Gross Volumetric Average", f"{int(year_df['Charges Filed'].mean()):,} / statute")
kpi3.metric("Highest Incident Category", year_df.groupby('Category')['Charges Filed'].sum().idxmax())

# 4. Interactive Visualizations Block
st.header(f"Statistical Distributions for Calendar Year {selected_year}")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Volumetric Distribution by Main Category")
    cat_df = year_df.groupby('Category')['Charges Filed'].sum().reset_index()
    fig_pie = px.pie(cat_df, values='Charges Filed', names='Category', hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.subheader("Statistical Anomalies (Z-Score Deviation Mapping)")
    # Highlights elements away from the standard historical distribution mean
    fig_z = px.bar(year_df, x='Statute', y='Z-Score', color='Category',
                   title="Statutes standard deviations away from the annual norm",
                   labels={'Z-Score': 'Standard Deviations (Z-Score)'})
    fig_z.add_hline(y=1.96, line_dash="dash", line_color="red", annotation_text="Significantly High (+1.96σ)")
    fig_z.add_hline(y=-1.96, line_dash="dash", line_color="blue", annotation_text="Significantly Low (-1.96σ)")
    st.plotly_chart(fig_z, use_container_width=True)

# 5. Granular Multi-Statute Comparison Matrix
st.header("Comparative Cross-Statute Multi-Axis Explorer")
selected_statutes = st.multiselect("Select Statutes to Contrast Directly", year_df['Statute'].unique(), 
                                     default=year_df['Statute'].unique()[:3])

if selected_statutes:
    compare_df = year_df[year_df['Statute'].isin(selected_statutes)]
    
    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(x=compare_df['Statute'], y=compare_df['Charges Filed'], name='Raw Charges Count', yaxis='y1'))
    fig_comp.add_trace(go.Scatter(x=compare_df['Statute'], y=compare_df['Rate per 100k'], name='Rate per 100k Pop.', yaxis='y2', line=dict(color='orange', width=3)))
    
    fig_comp.update_layout(
        title="Raw Charge Volume vs Normalized Population Rate",
        yaxis=dict(title="Raw Charge Field Count"),
        yaxis2=dict(title="Normalized Rate Per 100k Citizens", overlaying='y', side='right'),
        legend=dict(x=0.01, y=0.99)
    )
    st.plotly_chart(fig_comp, use_container_width=True)

# 6. Structured Data Ledger Export View
st.header("Computed Analytical Output Dataset")
st.dataframe(year_df[['Statute', 'Category', 'Charges Filed', 'Rate per 100k', 'Percentage of Total %', 'Z-Score']].sort_values(by='Charges Filed', ascending=False), use_container_width=True)

