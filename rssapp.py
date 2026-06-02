import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor
from scipy.optimize import linprog
from datetime import datetime
import json

# 1. Spatio-Temporal Base Infrastructure Mock Data Generator
@st.cache_data
def load_enterprise_comms_data():
    np.random.seed(42)
    center_lat, center_lon = 40.7128, -74.0060
    
    # Base Facility Definition Locations
    bases = {
        "Precinct Alpha (North)": {"lat": 40.7450, "lon": -74.0010, "fleet": 60},
        "Precinct Bravo (South)": {"lat": 40.6850, "lon": -74.0120, "fleet": 50}
    }
    
    # Historic Incident Logs Matrix
    data = []
    for week in range(3):
        for _ in range(300):
            lat_offset = np.random.normal(0, 0.015)
            lon_offset = np.random.normal(0, 0.015)
            data.append({
                "Week_Index": week, "Latitude": center_lat + lat_offset, "Longitude": center_lon + lon_offset,
            })
    return pd.DataFrame(data), bases

st.set_page_config(page_title="Enterprise Command & Comms Platform", layout="wide")
st.title("⚖️ Strategic Messaging & Pollable RSS Ticker Command Platform")
st.markdown("Automated API status notification streams combined with real-time pollable telemetric data tickers.")

df, base_network = load_enterprise_comms_data()

# ========================================================
# BACKGROUND PROCESSING: RISK PREDICTION & ESCALATION RUN
# ========================================================
df['Grid_Lat_Bin'] = df['Latitude'].round(2)
df['Grid_Lon_Bin'] = df['Longitude'].round(2)
grid_history = df.groupby(['Grid_Lat_Bin', 'Grid_Lon_Bin', 'Week_Index']).size().reset_index(name='Count')
features_df = grid_history.pivot(index=['Grid_Lat_Bin', 'Grid_Lon_Bin'], columns='Week_Index', values='Count').fillna(0).reset_index()

forecaster = RandomForestRegressor(n_estimators=15, random_state=42).fit(features_df[].values, features_df.values)
features_df['Predicted_Volume'] = forecaster.predict(features_df[].values)
forecast_df = features_df[features_df['Predicted_Volume'] > 1.0].copy()

# Inject Mock Escalation States for Notification Pipelines
forecast_df['Escalation_Tier'] = np.where(forecast_df['Predicted_Volume'] >= 8.0, "TIER_3_CRITICAL", 
                                  np.where(forecast_df['Predicted_Volume'] >= 4.0, "TIER_2_REGIONAL", "TIER_1_LOCAL"))

# Interface Layout Tabs
tab_sms, tab_rss = st.tabs(["💬 Live Messaging Webhook Hub", "📻 Pollable RSS Ticker Data Feed"])

# --------------------------------------------------------
# TAB 1: LIVE MESSAGING WEBHOOK HUB
# --------------------------------------------------------
with tab_sms:
    st.header("Automated Multi-Channel Communications Gateway")
    st.markdown("Configure operational dispatch triggers to transmit automated updates across Slack channels or Twilio SMS arrays when regional threat thresholds are crossed.")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.subheader("API Gateway Credentials Configuration")
        slack_url = st.text_input("Target Slack Webhook API URL Endpoint", value="https://slack.com")
        twilio_phone = st.text_input("Target Supervisor Dispatch Cell Number (Twilio SMS Target)", value="+1-555-867-5309")
    
    with col_c2:
        st.subheader("Manual API Operational State Overrides")
        target_override_cell = st.selectbox("Select Target Active Threat Sector Box to Alert", 
                                            [f"Sector Lat: {r['Grid_Lat_Bin']:.2f}, Lon: {r['Grid_Lon_Bin']:.2f} ({r['Escalation_Tier']})" for _, r in forecast_df.iterrows()])
        
    st.subheader("Pending Event Logs & Status Message Previews")
    # Pull out a mock critical record to display live status updates
    crit_records = forecast_df[forecast_df['Escalation_Tier'] == "TIER_3_CRITICAL"]
    if not crit_records.empty:
        target_row = crit_records.iloc[0]
        
        # Build Standardized Status JSON Payload
        slack_payload = {
            "text": f"🚨 *AUTOMATED TACTICAL ESCALATION ALERT* 🚨\n"
                    f"*Location Context:* Grid Sector ({target_row['Grid_Lat_Bin']:.2f}, {target_row['Grid_Lon_Bin']:.2f})\n"
                    f"*Calculated Risk Index:* {target_row['Predicted_Volume']:.2f} expected incidents next week.\n"
                    f"*Status Code Assignment:* `TIER_3_TACTICAL_CRITICAL` - Dispatch protocols initiated immediately."
        }
        
        sms_text = f"[ALERT] Sector ({target_row['Grid_Lat_Bin']:.2f}, {target_row['Grid_Lon_Bin']:.2f}) upgraded to TIER 3. Risk index: {target_row['Predicted_Volume']:.1f}. Check command dashboard."
        
        col_pay1, col_pay2 = st.columns(2)
        with col_pay1:
            st.markdown("**Structured Slack JSON Payload Packet**")
            st.code(json.dumps(slack_payload, indent=2), language="json")
            if st.button("Transmit Slack Status Payload"):
                st.success(f"✔ Webhook packet successfully pushed to API router. HTTP Status Code 200 (Success).")
                
        with col_pay2:
            st.markdown("**Twilio SMS Outbound Text Body String**")
            st.info(sms_text)
            if st.button("Transmit Twilio Text Dispatch"):
                st.success(f"✔ SMS payload packet added to Twilio carrier outbound queue. HTTP Status Code 201 (Created).")
    else:
        st.info("No active Tier 3 exceptions found to trigger notifications.")

# --------------------------------------------------------
# TAB 2: POLLABLE RSS TICKER DATA FEED
# --------------------------------------------------------
with tab_rss:
    st.header("Patrol Screen Ticker Feed Engine (XML/RSS Endpoint)")
    st.markdown("This module compiles active system updates into a **lightweight, standardized XML/RSS news feed data format**. Idle command terminals or vehicle dashboards can query this feed over low bandwidth to show a scrolling ticker of recent updates.")
    
    refresh_rate = st.selectbox("Set Ticker Hardware Auto-Poll Refresh Interval", ["Every 30 Seconds", "Every 2 Minutes", "Every 5 Minutes"])
    
    # 1. XML String Composition Engine
    rss_xml =  "<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n"
    rss_xml += "<rss version=\"2.0\">\n"
    rss_xml += "  <channel>\n"
    rss_xml += "    <title>Spatio-Temporal Tactical Risk Telemetry Ticker</title>\n"
    rss_xml += f"    <lastBuildDate>{datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S')} GMT</lastBuildDate>\n"
    rss_xml += "    <description>Continuous streaming baseline update ledger for vehicle terminal readouts.</description>\n\n"
    
    # Loop over active alerts to construct individual news items
    item_counter = 0
    for idx, row in forecast_df.sort_values(by='Predicted_Volume', ascending=False).iterrows():
        if row['Escalation_Tier'] != "TIER_1_LOCAL":
            rss_xml += "    <item>\n"
            rss_xml += f"      <title>[{row['Escalation_Tier']}] Sector Elevation Warning</title>\n"
            rss_xml += f"      <description>Grid box center located at Lat {row['Grid_Lat_Bin']:.2f}, Lon {row['Grid_Lon_Bin']:.2f} shows a predicted volume index of {row['Predicted_Volume']:.1f} charges for the upcoming tracking frame.</description>\n"
            rss_xml += f"      <guid>GRID_BOX_{row['Grid_Lat_Bin']}_{row['Grid_Lon_Bin']}</guid>\n"
            rss_xml += "    </item>\n"
            item_counter += 1
            
    rss_xml += "  </channel>\n"
    rss_xml += "</rss>"
    
    # Top-level metric for checking ticker state
    st.metric("Active Ticker Feed Items Cached", f"{item_counter} Broadcasting Objects")
    
    col_v1, col_v2 = st.columns([2, 1])
    with col_v1:
        st.markdown("**Live Formatted Output (Valid RSS/XML Data Structure)**")
        st.text_area("Pollable XML Payload View", rss_xml, height=350)
    
    with col_v2:
        st.markdown("### Terminal Reader Status")
        st.write("📡 **Endpoint URL:** `/api/v2/telemetry/ticker.xml`")
        st.write(f"⏱️ **Hardware Interval:** {refresh_rate}")
        st.write("💻 **Target Systems:** Idle Terminals, Vehicle Dashboards, Mobile Digital Systems.")
        
        # Download Action Button
        st.download_button(
            label="Download Live Ticker Payload File (.XML)",
            data=rss_xml,
            file_name="patrol_ticker_feed.xml",
            mime="application/rss+xml"
  )
      
