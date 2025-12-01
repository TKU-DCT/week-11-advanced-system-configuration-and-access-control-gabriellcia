import streamlit as st
import sqlite3
import pandas as pd
import os

DB_NAME = "log.db"

st.set_page_config(page_title="Advanced Dashboard", layout="wide")

# ---------------------------
# Session State Initialization
# ---------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "cpu_threshold" not in st.session_state:
    st.session_state.cpu_threshold = 80
if "memory_threshold" not in st.session_state:
    st.session_state.memory_threshold = 80
if "disk_threshold" not in st.session_state:
    st.session_state.disk_threshold = 80


# ---------------------------
# Login Page
# ---------------------------
def login_page():
    st.title("🔐 Login to Access Dashboard")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.success("Login successful! Redirecting to dashboard...")
            st.rerun()  # <─ PENTING: st.rerun, BUKAN experimental_rerun
        else:
            st.error("Invalid username or password.")


# ---------------------------
# Dashboard Page
# ---------------------------
def dashboard_page():
    st.title("🌐 Secure Data Center Dashboard")

    if not os.path.exists(DB_NAME):
        st.warning("Database not found. Please ensure 'log.db' exists.")
        return

    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM system_log", conn)
    conn.close()

    if df.empty:
        st.info("No data in system_log table yet.")
        return

    # Tampilkan data terakhir
    st.subheader("📊 Latest Logs")
    st.dataframe(df.tail(10), use_container_width=True)

    # Line chart
    st.subheader("📈 Resource Usage Over Time")
    try:
        chart_df = df.set_index("timestamp")[["cpu", "memory", "disk"]]
        st.line_chart(chart_df)
    except Exception as e:
        st.warning(f"Could not plot chart: {e}")

    # Alert based on thresholds
    st.subheader("🚨 Alert Status (Based on Current Thresholds)")
    latest = df.iloc[-1]

    cpu_msg = f"CPU: {latest['cpu']}% (threshold {st.session_state.cpu_threshold}%)"
    mem_msg = f"Memory: {latest['memory']}% (threshold {st.session_state.memory_threshold}%)"
    disk_msg = f"Disk: {latest['disk']}% (threshold {st.session_state.disk_threshold}%)"

    if latest["cpu"] > st.session_state.cpu_threshold:
        st.error(cpu_msg)
    else:
        st.success(cpu_msg)

    if latest["memory"] > st.session_state.memory_threshold:
        st.error(mem_msg)
    else:
        st.success(mem_msg)

    if latest["disk"] > st.session_state.disk_threshold:
        st.error(disk_msg)
    else:
        st.success(disk_msg)


# ---------------------------
# Configuration Page
# ---------------------------
def configuration_page():
    st.title("⚙️ Configuration Panel")

    st.write("Adjust alert thresholds for system resources:")

    cpu = st.slider("CPU Alert Threshold (%)", 0, 100,
                    st.session_state.cpu_threshold)
    mem = st.slider("Memory Alert Threshold (%)", 0, 100,
                    st.session_state.memory_threshold)
    disk = st.slider("Disk Alert Threshold (%)", 0, 100,
                     st.session_state.disk_threshold)

    if st.button("💾 Save Settings"):
        st.session_state.cpu_threshold = cpu
        st.session_state.memory_threshold = mem
        st.session_state.disk_threshold = disk
        st.success("Configuration saved!")


# ---------------------------
# Logout
# ---------------------------
def logout():
    st.session_state.logged_in = False
    st.success("You have been logged out.")
    st.rerun()  # <─ PENTING: st.rerun, BUKAN experimental_rerun


# ---------------------------
# Main App Logic
# ---------------------------
if not st.session_state.logged_in:
    login_page()
else:
    st.sidebar.title("📂 Navigation")
    page = st.sidebar.radio("Select Page",
                            ["Dashboard", "Configuration", "Logout"])

    if page == "Dashboard":
        dashboard_page()
    elif page == "Configuration":
        configuration_page()
    elif page == "Logout":
        logout()
git status