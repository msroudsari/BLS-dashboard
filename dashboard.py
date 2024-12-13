import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

file_path = 'bls_data.csv'
data = pd.read_csv(file_path)

# Mapping series_id to series names
series_mapping = {
    "LNS11000000": "Civilian Labor Force (Seasonally Adjusted)",
    "LNS12000000": "Civilian Employment (Seasonally Adjusted)",
    "LNS13000000": "Civilian Unemployment (Seasonally Adjusted)",
    "LNS14000000": "Unemployment Rate (Seasonally Adjusted)",
    "CES0000000001": "Total Nonfarm Employment (Seasonally Adjusted)",
    "CES0500000002": "Total Private Avg Weekly Hours (All Employees)",
    "CES0500000007": "Total Private Avg Weekly Hours (Prod. and Nonsup. Employees)",
    "CES0500000003": "Total Private Avg Hourly Earnings (All Employees)",
    "CES0500000008": "Total Private Avg Hourly Earnings (Prod. and Nonsup. Employees)"
}

# Streamlit dashboard starts here
st.set_page_config(page_title="BLS Data Dashboard", layout="wide")
st.title("📊 Bureau of Labor Statistics (BLS) Data Dashboard")

# Sidebar
st.sidebar.title("Filter Options")
series_name = st.sidebar.selectbox("Select a Series", list(series_mapping.values()))
series_id = list(series_mapping.keys())[list(series_mapping.values()).index(series_name)]

# Year range selection
min_year = int(data['year'].min())
max_year = int(data['year'].max())
start_year, end_year = st.sidebar.slider(
    "Select Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
    step=1
)

# Filter data
series_data = data[(data['series_id'] == series_id) & (data['year'] >= start_year) & (data['year'] <= end_year)]

# Summary
st.sidebar.markdown("---")
st.sidebar.subheader("Summary Statistics")
st.sidebar.metric("Minimum Value", f"{series_data['value'].min():,.2f}")
st.sidebar.metric("Maximum Value", f"{series_data['value'].max():,.2f}")
st.sidebar.metric("Mean Value", f"{series_data['value'].mean():,.2f}")
st.sidebar.metric("Median Value", f"{series_data['value'].median():,.2f}")
st.sidebar.metric("Standard Deviation", f"{series_data['value'].std():,.2f}")
st.sidebar.metric("Total Sum", f"{series_data['value'].sum():,.2f}")

# Sum of data by year
yearly_data = series_data.groupby('year')['value'].sum().reset_index()

# Plots
bar_fig = px.bar(
    yearly_data,
    x='year',
    y='value',
    title=f"📊 Total Value by Year for {series_name} ({start_year} to {end_year})",
    labels={'value': 'Total Value', 'year': 'Year'},
    color_discrete_sequence=['#636EFA']
)
bar_fig.update_layout(
    xaxis=dict(
        tickmode='array',
        tickvals=yearly_data['year'],  # Set tick values to exact years
    )
)

line_fig = px.line(
    yearly_data,
    x='year',
    y='value',
    title=f"📈 Yearly Trend for {series_name} ({start_year} to {end_year})",
    labels={'value': 'Total Value', 'year': 'Year'},
    line_shape='linear',
    markers=True
)

box_fig = px.box(
    series_data,
    x='year',
    y='value',
    title=f"📦 Value Distribution by Year for {series_name} ({start_year} to {end_year})",
    labels={'value': 'Value', 'year': 'Year'},
    color_discrete_sequence=['#00CC96']
)

hist_fig = px.histogram(
    series_data,
    x='value',
    nbins=20,
    title=f"📊 Value Distribution for {series_name} ({start_year} to {end_year})",
    labels={'value': 'Value'},
    color_discrete_sequence=['#007fff']
)

# Columns layout
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(bar_fig, use_container_width=True)
    st.plotly_chart(box_fig, use_container_width=True)

with col2:
    st.plotly_chart(line_fig, use_container_width=True)
    st.plotly_chart(hist_fig, use_container_width=True)

# Time-series plot
if 'period_name' in series_data.columns:
    series_data = series_data.copy()
    series_data['month'] = series_data['period_name'].str[:3]
    time_series_data = series_data.groupby(['month', 'year'])['value'].mean().reset_index()
    time_series_fig = px.line(
        time_series_data,
        x='month',
        y='value',
        color='year',
        title=f"🕒 Time-Series Plot for {series_name} ({start_year} to {end_year})",
        labels={'value': 'Value', 'month': 'Month'}
    )
    st.plotly_chart(time_series_fig, use_container_width=True)
