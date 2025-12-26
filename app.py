import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Smart Energy Monitoring Dashboard", layout="wide")
st.title("⚡ Smart Energy Monitoring Dashboard")

# Sidebar inputs
st.sidebar.header("Settings")
tariff = st.sidebar.number_input("Tariff (₹ per kWh)", min_value=0.0, value=8.0, step=0.5)
time_granularity = st.sidebar.radio("Time view", ["Hourly", "Daily", "Weekly", "Monthly"])

# Data input options
st.sidebar.header("Data source")
data_option = st.sidebar.radio("Choose data source", ["Sample CSV", "Upload CSV"])

if data_option == "Upload CSV":
    uploaded = st.sidebar.file_uploader("Upload CSV with Timestamp and device columns", type=["csv"])
if uploaded is not None:
    df = pd.read_csv(uploaded)
else:
    st.info("Upload a CSV to proceed or switch to Sample CSV.")
st.stop()
else:
# Sample dataset
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

# Validate and preprocess
if "Timestamp" not in df.columns:
st.error("CSV must include a 'Timestamp' column.")
st.stop()

df["Timestamp"] = pd.to_datetime(df["Timestamp"])
device_cols = [c for c in df.columns if c != "Timestamp"]
if not device_cols:
st.error("CSV must include device columns like 'Fan (W)', 'Fridge (W)', etc.")
st.stop()

# Show raw data
st.subheader("Raw readings")
st.dataframe(df, use_container_width=True)

# Aggregate by chosen time view
work = df.copy()
work = work.set_index("Timestamp")
if time_granularity == "Hourly":
agg = work.resample("H").mean()
elif time_granularity == "Daily":
agg = work.resample("D").mean()
elif time_granularity == "Weekly":
agg = work.resample("W").mean()
else:
agg = work.resample("M").mean()

# Charts: trends
st.subheader(f"{time_granularity} power usage trends (W)")
fig_line = px.line(agg.reset_index(), x="Timestamp", y=device_cols,
labels={"value":"Power (W)","variable":"Device"})
st.plotly_chart(fig_line, use_container_width=True)

# Daily/period totals (kWh) approximation:
# Convert W average per period to Wh by multiplying by hours in period, then to kWh
# For simplicity, we sum watts readings and divide by 1000 assuming 1-hour intervals for uploaded data.
# If your real data has variable intervals, adjust this logic accordingly.
period_hours = 1
kwh_per_device = (work[device_cols].sum() * period_hours) / 1000.0
st.subheader("Total consumption per device (kWh) and estimated cost")
costs = kwh_per_device * tariff
summary = pd.DataFrame({"Total kWh": kwh_per_device.round(3),
"Estimated Cost (INR)": costs.round(2)})
st.table(summary)

# Contribution pie
st.subheader("Device contribution to total usage")
fig_pie = px.pie(values=kwh_per_device.values, names=kwh_per_device.index)
st.plotly_chart(fig_pie, use_container_width=True)

# Compare devices bar
st.subheader("Consumption comparison (kWh)")
fig_bar = px.bar(x=kwh_per_device.index, y=kwh_per_device.values,
labels={"x":"Device","y":"Total kWh"})
st.plotly_chart(fig_bar, use_container_width=True)

st.caption("Tip: Use the sidebar to upload your CSV and switch views (Hourly/Daily/Weekly/Monthly).")