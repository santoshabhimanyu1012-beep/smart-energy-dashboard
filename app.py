import streamlit as st
import pandas as pd
import plotly.express as px

# Page setup
st.set_page_config(page_title="Smart Energy Monitoring Dashboard", layout="wide")
st.markdown("<h1 style='color:#2c3e50;'>⚡ Smart Energy Monitoring Dashboard</h1>", unsafe_allow_html=True)

# Sidebar inputs
with st.sidebar:
    st.header("⚙️ Settings")
    tariff = st.number_input("Tariff (₹ per kWh)", min_value=0.0, value=8.0, step=0.5)
    time_granularity = st.radio("Time view", ["Hourly", "Daily", "Weekly", "Monthly"])
    st.header("📂 Data source")
    data_option = st.radio("Choose data source", ["Upload CSV", "Use sample data"])
    uploaded = None
    if data_option == "Upload CSV":
        uploaded = st.file_uploader("Upload CSV with Timestamp and device columns", type=["csv"])

# Load data
if data_option == "Upload CSV" and uploaded:
    df = pd.read_csv(uploaded)
elif data_option == "Use sample data":
    df = pd.DataFrame({
        "Timestamp": [
            "2025-12-26 08:00","2025-12-26 09:00","2025-12-26 10:00",
            "2025-12-26 11:00","2025-12-26 12:00","2025-12-26 13:00",
            "2025-12-26 14:00","2025-12-26 15:00","2025-12-26 16:00"
        ],
        "Fan (W)": [120,100,130,90,110,95,105,115,98],
        "Light (W)": [60,40,70,50,65,55,45,60,52],
        "Fridge (W)": [200,220,210,230,205,215,225,210,220],
        "TV (W)": [150,160,140,170,155,145,165,150,160]
    })
else:
    st.info("Upload a CSV to proceed or switch to Sample CSV.")
    st.stop()

# Validate and preprocess
if "Timestamp" not in df.columns:
    st.error("CSV must include a 'Timestamp' column.")
    st.stop()

df["Timestamp"] = pd.to_datetime(df["Timestamp"])
device_cols = [c for c in df.columns if c != "Timestamp"]
if not device_cols:
    st.error("CSV must include device columns like 'Fan (W)', 'Fridge (W)', etc.")
    st.stop()

# Layout: raw data preview
with st.container():
    st.subheader("📊 Raw Data Preview")
    st.dataframe(df, use_container_width=True)

# Aggregate by chosen time view
work = df.copy().set_index("Timestamp")
if time_granularity == "Hourly":
    agg = work.resample("H").mean()
elif time_granularity == "Daily":
    agg = work.resample("D").mean()
elif time_granularity == "Weekly":
    agg = work.resample("W").mean()
else:
    agg = work.resample("M").mean()

# Device filtering
selected_devices = st.multiselect("🔍 Select devices to display", device_cols, default=device_cols)

# Charts in columns
col1, col2 = st.columns(2)
with col1:
    st.subheader("📈 Power Usage Trends")
    fig_line = px.line(agg.reset_index(), x="Timestamp", y=selected_devices,
                       labels={"value":"Power (W)","variable":"Device"})
    st.plotly_chart(fig_line, use_container_width=True)

with col2:
    st.subheader("📊 Device Comparison")
    kwh_per_device = (work[selected_devices].sum()) / 1000.0
    fig_bar = px.bar(x=kwh_per_device.index, y=kwh_per_device.values,
                     labels={"x":"Device","y":"Total kWh"})
    st.plotly_chart(fig_bar, use_container_width=True)

# Summary table
st.subheader("💰 Total Consumption and Cost")
costs = kwh_per_device * tariff
summary = pd.DataFrame({"Total kWh": kwh_per_device.round(3),
                        "Estimated Cost (INR)": costs.round(2)})
st.table(summary)

# Pie chart
st.subheader("🍕 Device Contribution")
fig_pie = px.pie(values=kwh_per_device.values, names=kwh_per_device.index)
st.plotly_chart(fig_pie, use_container_width=True)

# Weekly and Monthly summaries
st.subheader("📅 Time-Based Summaries")
tab1, tab2 = st.tabs(["Weekly", "Monthly"])

with tab1:
    weekly = work.resample("W").sum() / 1000.0
    weekly_costs = (weekly * tariff).round(2)
    st.line_chart(weekly[selected_devices])
    st.write("Weekly kWh and Costs")
    st.dataframe(weekly_costs[selected_devices])

with tab2:
    monthly = work.resample("M").sum() / 1000.0
    monthly_costs = (monthly * tariff).round(2)
    st.line_chart(monthly[selected_devices])
    st.write("Monthly kWh and Costs")
    st.dataframe(monthly_costs[selected_devices])

# Export CSV
st.subheader("📥 Export Summary")
csv = summary.to_csv().encode("utf-8")
st.download_button("Download Summary as CSV", csv, "summary.csv", "text/csv")

st.caption("Use the sidebar to upload your CSV, filter devices, and switch views. Your dashboard is now sleek and interactive!")