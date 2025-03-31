# Streamlit Dashboard for Wheelset Asset Management
import streamlit as st
import pandas as pd
import sqlite3
import datetime

# Connect to database
conn = sqlite3.connect("/mnt/data/wheelsets_demo.db", check_same_thread=False)

# Load wheelset options
wheelsets = pd.read_sql("SELECT Wheelset_ID FROM Wheelset_Master", conn)["Wheelset_ID"].tolist()
st.title("🚆 Freight Wheelset Asset Dashboard")
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/UK_Rail_Logo.svg/2560px-UK_Rail_Logo.svg.png", width=200)

selected_id = st.sidebar.selectbox("🔍 Scan or Select Wheelset ID", wheelsets)

# Fetch asset info
ws_info = pd.read_sql(f"SELECT * FROM Wheelset_Master WHERE Wheelset_ID = '{selected_id}'", conn).iloc[0]
st.header(f"Asset Overview – Wheelset {selected_id}")

# Asset Summary
st.markdown("### ⚙️ Asset Summary")
col1, col2, col3 = st.columns(3)
col1.metric("📦 Wagon No", ws_info.Wagon_No)
col2.metric("📍 Position", ws_info.Current_Position)
col3.metric("🔧 Install Date", ws_info.Install_Date)

col1, col2, col3 = st.columns(3)
col1.metric("📊 Mileage (km)", f"{ws_info.Total_Mileage:,}")
col2.metric("⏳ RUL (km)", f"{ws_info.RUL_km:,}")
col3.metric("🩺 Condition", ws_info.Current_Condition)

# Tabs
tabs = st.tabs(["📋 Overview", "🛠️ Inspection Log", "📊 Monitoring", "🧠 Decision Support"])

# --- Overview Tab ---
with tabs[0]:
    st.subheader("🛤️ Wheelset History Timeline")
    st.write("Coming soon: Wagon exchanges and usage journey")

# --- Inspection Tab ---
with tabs[1]:
    st.subheader("📅 Past Inspections")
    inspections = pd.read_sql(f"SELECT * FROM Inspection_Log WHERE Wheelset_ID = '{selected_id}'", conn)
    st.dataframe(inspections.sort_values("Date", ascending=False))

# --- Monitoring Tab ---
with tabs[2]:
    st.subheader("📡 Condition Monitoring")
    monitoring = pd.read_sql(f"SELECT * FROM Monitoring_Data WHERE Wheelset_ID = '{selected_id}'", conn)
    st.dataframe(monitoring)

# --- Decision Support Tab ---
with tabs[3]:
    st.subheader("🧠 Decision Support")
    condition = ws_info.Current_Condition
    rul = ws_info.RUL_km

    if condition == "Needs Maintenance" or rul < 10000:
        st.error("🚨 This wheelset is flagged for immediate maintenance.")
    elif rul < 20000:
        st.warning("⚠️ Approaching maintenance threshold. Monitor closely.")
    else:
        st.success("✅ No urgent actions needed.")

    st.write("Future feature: Predictive analytics, float planning, lathe queue insights")
