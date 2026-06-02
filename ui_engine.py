import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import json

# 1. Spatio-Temporal Data Generation Engine
@st.cache_data
def load_db_simulation_baseline():
    np.random.seed(42)
    center_lat, center_lon = 40.7128, -74.0060
    
    # Generate mock records to simulate an incoming live stream
    stream_data = []
    for i in range(100):
        stream_data.append({
            "Transaction_ID": 500000 + i,
            "Timestamp": (datetime.utcnow() - timedelta(seconds=(100-i)*10)).isoformat() + "Z",
            "Latitude": center_lat + np.random.normal(0, 0.01),
            "Longitude": center_lon + np.random.normal(0, 0.01),
            "Charge_Type": np.random.choice(["Property", "Violent", "Cyber"]),
            "Payload_Size_KB": float(np.random.uniform(1.2, 4.5))
        })
    return pd.DataFrame(stream_data)

st.set_page_config(page_title="Database Resilience Platform", layout="wide")
st.title("🗄️ Database Fault Auto-Recovery & Write-Buffer Escalation Engine")
st.markdown("Automate decoupled transactional buffering during master instance connection loss and execute transactional re-spooling loops.")

stream_df = load_db_simulation_baseline()

# ========================================================
# USER CONTROLS: MASTER DATABASE HEALTH STATE SIMULATOR
# ========================================================
st.sidebar.header("Database Node Controls")
db_connection_state = st.sidebar.radio(
    "Set Primary Database Node Connectivity State",
    ["CONNECTED (Healthy/Nominal)", "TIMEOUT_FAILURE (Instance Crashing)", "RESTORED (Awaiting Log Re-Spool)"]
)

# --------------------------------------------------------
# CORE RESILIENCE LOGIC ENGINE
# --------------------------------------------------------
if db_connection_state == "CONNECTED (Healthy/Nominal)":
    state_code = "STABLE_SYNC"
    buffer_action = "Streaming directly to Main Cloud PostgreSQL Engine"
    buffer_count = 0
    ui_status_color = "success"
    diagnostic_msg = "✔ Master Database link active. Processing transactional payloads natively with zero replication lag."

elif db_connection_state == "TIMEOUT_FAILURE (Instance Crashing)":
    state_code = "BUFFERING_LOCAL"
    buffer_action = "⚠️ CRASH DETECTED: Decoupling stream to local encrypted SQLite write-buffer"
    buffer_count = len(stream_df) # All inbound transactions spill into the buffer
    ui_status_color = "error"
    diagnostic_msg = "🔴 DATABASE WRITE FAILURE: Automated failover initialized. Direct writes blocked; spooling to local edge disk caches."

else: # RESTORED (Awaiting Log Re-Spool)
    state_code = "SPOOLING_RECOVERY"
    buffer_action = "🔄 AUTO-RECOVERY ACTIVE: Spooling local buffers back into Primary Database..."
    buffer_count = int(len(stream_df) * 0.35) # Simulating a processing stream clearing out the cache
    ui_status_color = "warning"
    diagnostic_msg = "⚡ PRIMARY DB RECONNECTED: Validating connection integrity. Parsing sequential log structures and clearing write-buffer."

# Interface Tabs
tab_status, tab_payloads = st.tabs(["⚡ Live Cluster Health Metrics", "📦 Cache Transaction Payloads"])

# --------------------------------------------------------
# TAB 1: LIVE CLUSTER HEALTH METRICS
# --------------------------------------------------------
with tab_status:
    st.header("Database Instance Status Dashboard")
    st.button(diagnostic_msg, type="primary" if ui_status_color == "success" else ("secondary" if ui_status_color == "warning" else "danger"), disabled=True)
    
    # Render Status Cards
    db_k1, db_k2, db_k3 = st.columns(3)
    db_k1.metric("Database Cluster State Mode", state_code)
    db_k2.metric("Write-Buffer Target Pipeline", buffer_action.split(":")[0])
    db_k3.metric("Spillover Cached Record Count", f"{buffer_count} transactions", 
                 delta=f"+{buffer_count} delayed" if state_code == "BUFFERING_LOCAL" else (f"-{len(stream_df) - buffer_count} processed" if state_code == "SPOOLING_RECOVERY" else "0 delayed"),
                 delta_color="inverse" if buffer_count > 0 else "normal")
    
    # Graphing Buffer Volumes over Time
    st.subheader("Dynamic Operational Buffer Spillover Footprint")
    time_bins = []
    cached_volumes = []
    current_accumulator = 0
    
    for idx, row in stream_df.iterrows():
        time_bins.append(row["Timestamp"])
        if state_code == "BUFFERING_LOCAL":
            current_accumulator += row["Payload_Size_KB"]
        elif state_code == "SPOOLING_RECOVERY" and idx > 35:
            current_accumulator = max(0.0, current_accumulator - row["Payload_Size_KB"])
        else:
            current_accumulator = 0.0
        cached_volumes.append(current_accumulator)
        
    chart_df = pd.DataFrame({"Timestamp": time_bins, "Accumulated_Buffer_Size_KB": cached_volumes})
    fig_buffer = px.area(chart_df, x="Timestamp", y="Accumulated_Buffer_Size_KB",
                         title="Active Local Disk Cache Size Footprint (KB)",
                         color_discrete_sequence=["#FF9900" if state_code == "SPOOLING_RECOVERY" else ("#FF3333" if state_code == "BUFFERING_LOCAL" else "#00FFCC")])
    st.plotly_chart(fig_buffer, use_container_width=True)

# --------------------------------------------------------
# TAB 2: CACHE TRANSACTION PAYLOADS
# --------------------------------------------------------
with tab_payloads:
    st.header("Decoupled Buffer Transaction Logs")
    st.markdown("This payload ledger tracks transactional structural definitions when the database drops offline. It captures transactions locally, preventing system crashes or lost records.")
    
    if buffer_count > 0:
        sample_batch = stream_df.head(2).to_dict(orient="records")
        buffer_metadata_packet = {
            "buffer_engine_state": state_code,
            "local_storage_target": "SQLITE_EDGE_CACHE_BLOCK_A",
            "total_buffered_size_bytes": int(sum(stream_df['Payload_Size_KB']) * 1024) if state_code == "BUFFERING_LOCAL" else int(buffer_count * 2048),
            "master_recovery_endpoint": "postgresql://master-cluster-01.internal:5432/legal_ledger",
            "buffered_records_preview": sample_batch
        }
        st.markdown(f"**Active Write-Buffer Payload Cache Manifest (`JSON`)**")
        st.code(json.dumps(buffer_metadata_packet, indent=2), language="json")
    else:
        st.success("Buffer is clear. All system transactions are routing natively to the cloud database cluster.")

