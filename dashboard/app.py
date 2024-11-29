"""Streamlit Dashboard for Plant Health Monitoring"""
import os
from io import BytesIO
from datetime import datetime
import pandas as pd
import boto3
import altair as alt
import streamlit as st
import pymssql
from dotenv import load_dotenv

load_dotenv(override=True)

S3_BUCKET = "c14-team-growth-storage"
FOLDER = "plant_data/"
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "username": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": os.getenv("DB_PORT"),
}

st.title("🌱 Liverpool Natural History Museum - Plant Health Monitoring")
st.write("Monitor real-time and historical plant health data from the botanical wing.")


def get_rds_connection():
    """Establish a connection to the RDS database."""
    try:
        conn = pymssql.connect(
            server=DB_CONFIG["host"],
            user=DB_CONFIG["username"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            port=DB_CONFIG["port"],
        )
        return conn
    except pymssql.OperationalError as e:
        st.error(f"Failed to connect to RDS: {e}")
        return None


def fetch_real_time_data_from_rds(selected_plant: str) -> pd.DataFrame:
    """Fetch the latest real-time data for a specific plant."""
    conn = get_rds_connection()
    if not conn:
        return pd.DataFrame()

    query = f"""
        SELECT 
            p.plant_name,
            r.soil_moisture,
            r.temperature,
            r.last_watered,
            r.recording_at
        FROM 
            gamma.recording r
        JOIN 
            gamma.plant p
        ON 
            r.plant_id = p.plant_id
        WHERE 
            p.plant_name = '{selected_plant}'
        ORDER BY 
            r.recording_at DESC
        OFFSET 0 ROWS FETCH NEXT 10 ROWS ONLY;
    """

    dataframe = pd.read_sql(query, conn)
    conn.close()
    return dataframe


def get_plant_names() -> list:
    """Fetch a list of plant names from the database."""
    conn = get_rds_connection()
    if not conn:
        return []

    query = "SELECT DISTINCT plant_name FROM gamma.plant;"

    dataframe = pd.read_sql(query, conn)
    conn.close()
    return dataframe["plant_name"].tolist()


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


def render_real_time_dashboard():
    """Render the real-time data dashboard."""
    plant_list = get_plant_names()
    selected_plant = st.sidebar.selectbox("Select Plant by Name", plant_list)

    if not selected_plant:
        st.warning("Please select a plant to view real-time data.")
        return

    dataframe = fetch_real_time_data_from_rds(selected_plant)

    if dataframe.empty:
        st.warning(f"No real-time data available for {selected_plant}.")
        return

    display_real_time_data(dataframe, selected_plant)


def display_real_time_data(dataframe: pd.DataFrame, selected_plant: str) -> None:
    """Display the latest temperature and moisture readings for the selected plant."""
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

    plant_list = dataframe["plant_name"].unique()
    selected_plant = st.sidebar.selectbox("Select Plant by Name", plant_list)
    start_date = st.sidebar.date_input("Start Date", datetime.today()).strftime(
        "%Y-%m-%d"
    )
    end_date = st.sidebar.date_input(
        "End Date", datetime.today()).strftime("%Y-%m-%d")

    if start_date > end_date:
        st.warning("Start date cannot be after end date.")
        return

    display_historical_data(dataframe, selected_plant, pd.to_datetime(
        start_date), pd.to_datetime(end_date))


def display_historical_data(dataframe: pd.DataFrame, selected_plant: str,
                            start_date: datetime, end_date: datetime) -> None:
    """Display historical data for the selected plant within a date range."""
    if selected_plant:
        dataframe = dataframe[dataframe["plant_name"] == selected_plant]

    dataframe["recording_at"] = pd.to_datetime(
        dataframe["recording_at"], errors="coerce"
    )
    dataframe = dataframe[
        (dataframe["recording_at"] >= start_date) & (
            dataframe["recording_at"] <= end_date)
    ]

    st.header(f"{selected_plant}")

    st.subheader(f"Temperature Over Time for {selected_plant}")
    temperature_chart = alt.Chart(dataframe).mark_line().encode(
        x=alt.X("recording_at:T", title="Date/ Time",
                axis=alt.Axis(
                    format="%d-%m/ %I:%M %p",
                    tickCount=10,
                )
                ),
        y=alt.Y("temperature:Q", title="Temperature (°C)"),
    )
    st.altair_chart(temperature_chart, use_container_width=True)

    st.subheader(f"Soil Moisture Over Time for {selected_plant}")
    moisture_chart = alt.Chart(dataframe).mark_line().encode(
        x=alt.X("recording_at:T", title="Date/ Time",
                axis=alt.Axis(
                    format="%d-%m/ %I:%M %p",
                    tickCount=10,
                )
                ),
        y=alt.Y("soil_moisture:Q", title="Soil Moisture (%)"),
    )
    st.altair_chart(moisture_chart, use_container_width=True)


def run_streamlit():
    """Main function to run the Streamlit app."""
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select Dashboard", ["Real-Time", "Historical"])

    if page == "Real-Time":
        render_real_time_dashboard()
    elif page == "Historical":
        current_date = datetime.today().strftime("%Y-%m-%d")
        file_key = get_file_key(current_date)
        dataframe = fetch_data_from_s3(S3_BUCKET, file_key)
        render_historical_dashboard(dataframe)


if __name__ == "__main__":
    run_streamlit()
