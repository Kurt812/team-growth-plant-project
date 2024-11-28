"""Streamlit Dashboard for Plant Health Monitoring"""
from io import BytesIO
from datetime import datetime
import pandas as pd
import boto3
import altair as alt
import streamlit as st

S3_BUCKET = "c14-team-growth-storage"
FOLDER = "plant_data/"

st.title("🌱 Liverpool Natural History Museum - Plant Health Monitoring")
st.write("Monitor real-time and historical plant health data from the botanical wing.")


def get_file_key(date: str) -> str:
    """Generate the S3 file key based on the given date."""
    return f"{FOLDER}{date}.parquet"


def fetch_data_from_s3(bucket: str, file_key: str) -> pd.DataFrame:
    """Fetch the Parquet file from S3 and return a DataFrame."""
    s3_client = boto3.client("s3")
    try:
        response = s3_client.get_object(Bucket=bucket, Key=file_key)
        dataframe = pd.read_parquet(BytesIO(response["Body"].read()))
        return dataframe
    except s3_client.exceptions.NoSuchKey:
        st.error(f"Data for the selected date ({file_key}) not found in S3.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching data from S3: {e}")
        return pd.DataFrame()


def render_sidebar(dataframe: pd.DataFrame) -> tuple:
    """Render the sidebar with date range and plant selection."""
    st.sidebar.title("Filter Options")

    start_date, end_date = st.sidebar.date_input(
        "Select Date Range",
        [datetime.today(), datetime.today()],
    )
    formatted_start_date = start_date.strftime("%Y-%m-%d")
    formatted_end_date = end_date.strftime("%Y-%m-%d")

    plant_list = dataframe["plant_name"].unique(
    ).tolist() if not dataframe.empty else []
    selected_plant = st.sidebar.selectbox(
        "Select Plant by Name", options=plant_list
    ) if plant_list else None

    return formatted_start_date, formatted_end_date, selected_plant


def render_real_time_dashboard(dataframe: pd.DataFrame):
    """Render the real-time data dashboard."""

    if dataframe.empty or "plant_name" not in dataframe.columns:
        st.warning("No real-time data available.")
        return

    selected_plant = st.sidebar.selectbox(
        "Select Plant by Name", dataframe["plant_name"].unique()
    )
    display_real_time_data(dataframe, selected_plant)


def display_real_time_data(dataframe: pd.DataFrame, selected_plant: str) -> None:
    """Display the latest temperature and moisture readings for the selected plant."""
    if selected_plant:
        dataframe = dataframe[dataframe["plant_name"] == selected_plant]

    if dataframe.empty:
        st.warning(f"No real-time data available for {selected_plant}.")
        return

    dataframe["recording_at"] = pd.to_datetime(
        dataframe["recording_at"], errors="coerce"
    )

    latest_data = dataframe.sort_values(
        "recording_at", ascending=False).iloc[0]

    st.sidebar.metric("Plant Name", latest_data["plant_name"])
    st.sidebar.metric("Current Temperature", f"{latest_data['temperature']}°C")
    st.sidebar.metric("Soil Moisture", f"{latest_data['soil_moisture']}%")
    st.sidebar.metric(
        "Last Watered",
        latest_data["last_watered"].strftime("%Y-%m-%d %H:%M")
        if pd.notnull(latest_data["last_watered"])
        else "N/A",
    )

    st.header(f"{selected_plant}")

    st.subheader("Real-Time Temperature Trend")
    temperature_chart = alt.Chart(dataframe).mark_line().encode(
        x=alt.X("recording_at:T", title="Time"),
        y=alt.Y("temperature:Q", title="Temperature (°C)"),
    ).properties(
        width=700,
        height=400,
    )
    st.altair_chart(temperature_chart, use_container_width=True)

    st.subheader("Real-Time Soil Moisture Trend")
    moisture_chart = alt.Chart(dataframe).mark_line().encode(
        x=alt.X("recording_at:T", title="Time"),
        y=alt.Y("soil_moisture:Q", title="Soil Moisture (%)"),
    ).properties(
        width=700,
        height=400,
    )
    st.altair_chart(moisture_chart, use_container_width=True)


def render_historical_dashboard(dataframe: pd.DataFrame):
    """Render the historical data dashboard."""
    st.title("Historical Plant Data")

    selected_plant = st.sidebar.selectbox(
        "Select Plant by Name", dataframe["plant_name"].unique()
    )
    start_date = st.sidebar.date_input(
        "Start Date", datetime.today()).strftime("%Y-%m-%d")
    end_date = st.sidebar.date_input(
        "End Date", datetime.today()).strftime("%Y-%m-%d")

    if start_date > end_date:
        st.warning("Start date cannot be after end date.")
        return

    display_historical_data(dataframe, selected_plant, pd.to_datetime(
        start_date), pd.to_datetime(end_date))


def display_historical_data(dataframe: pd.DataFrame, selected_plant: str, start_date: datetime, end_date: datetime) -> None:
    """Display historical data for the selected plant within a date range."""
    if dataframe.empty:
        st.warning("No historical data available.")
        return

    if selected_plant:
        dataframe = dataframe[dataframe["plant_name"] == selected_plant]

    dataframe["recording_at"] = pd.to_datetime(
        dataframe["recording_at"], errors="coerce"
    )
    dataframe = dataframe.dropna(subset=["recording_at"])
    dataframe = dataframe[
        (dataframe["recording_at"] >= start_date) & (
            dataframe["recording_at"] <= end_date)
    ]

    if dataframe.empty:
        st.warning(f"No data available for {
                   selected_plant} in the selected date range.")
        return

    dataframe.reset_index(drop=True, inplace=True)

    st.subheader(f"Soil Moisture Over Time for {selected_plant}")
    if "recording_at" in dataframe.columns and "soil_moisture" in dataframe.columns:
        moisture_chart = alt.Chart(dataframe).mark_line().encode(
            x=alt.X(
                "recording_at:T",
                title="Time",
                axis=alt.Axis(titleFontSize=14, labelFontSize=12),
                timeUnit="hours"
            ),
            y=alt.Y(
                "soil_moisture:Q",
                title="Soil Moisture (%)",
                axis=alt.Axis(titleFontSize=14, labelFontSize=12),
            ),
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14
        ).properties(
            width=700,
            height=400,
        )
        st.altair_chart(moisture_chart, use_container_width=True)
    else:
        st.warning("Data for soil moisture is missing or improperly formatted.")

    st.subheader(f"Temperature Over Time for {selected_plant}")
    if "recording_at" in dataframe.columns and "temperature" in dataframe.columns:
        temperature_chart = alt.Chart(dataframe).mark_line().encode(
            x=alt.X(
                "recording_at:T",
                title="Time",
                axis=alt.Axis(titleFontSize=14, labelFontSize=12),
                timeUnit="hours"
            ),
            y=alt.Y(
                "temperature:Q",
                title="Temperature (°C)",
                axis=alt.Axis(titleFontSize=14, labelFontSize=12),
            ),
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14
        ).properties(
            width=700,
            height=400,
        )
        st.altair_chart(temperature_chart, use_container_width=True)
    else:
        st.warning("Data for temperature is missing or improperly formatted.")


def run_streamlit():
    """Main function to run the Streamlit app."""
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select Dashboard", ["Real-Time", "Historical"])

    current_date = datetime.today().strftime("%Y-%m-%d")
    file_key = get_file_key(current_date)
    dataframe = fetch_data_from_s3(S3_BUCKET, file_key)

    if page == "Real-Time":
        render_real_time_dashboard(dataframe)
    elif page == "Historical":
        render_historical_dashboard(dataframe)


if __name__ == "__main__":
    run_streamlit()
