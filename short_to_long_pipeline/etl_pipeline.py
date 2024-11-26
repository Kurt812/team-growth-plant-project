"""Extracts the data from the RDS into a dataframe"""
import logging
import os
from dotenv import load_dotenv
import pandas as pd
import pymssql
import boto3

logging.basicConfig(level=logging.INFO)
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "username": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": os.getenv("DB_PORT")
}

S3_BUCKET = os.getenv("S3_BUCKET")
S3_KEY = os.getenv("S3_KEY", "plant_data/complete_data.parquet")

LOCAL_PARQUET_FILE = "complete_data.parquet"


def get_db_connection() -> pymssql.Connection:
    """Establish a connection to the SQL Server database using pymssql."""
    try:
        conn = pymssql.connect(
            server=DB_CONFIG["host"],
            user=DB_CONFIG["username"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            port=DB_CONFIG["port"]
        )
        logging.info("Database connection established.")
        return conn
    except pymssql.DatabaseError as e:
        logging.error("Failed to connect to the database: %s", e)
        raise


def load_data_to_dataframe(connection: pymssql.Connection) -> pd.DataFrame:
    """Extracts data from the RDS database into a pandas DataFrame."""

    query = """SELECT p.plant_id, p.plant_name, r.soil_moisture, r.temperature, 
        r.last_watered, r.recording_at, 
        b.first_name AS botanist_first_name, b.last_name AS botanist_last_name,
        b.email AS botanist_email, b.phone AS botanist_phone
    FROM gamma.plant p
    JOIN gamma.recording r ON p.plant_id = r.plant_id
    JOIN gamma.botanist b ON p.botanist_id = b.botanist_id"""

    try:
        complete_df = pd.read_sql(query, connection)
        logging.info("Data successfully loaded into DataFrame.")
        connection.close()
        logging.info("Database connection closed.")
        return complete_df
    except Exception as e:
        logging.error("Error loading data to DataFrame: %s", e)
        raise


def save_to_parquet(dataframe: pd.DataFrame, local_file: str) -> None:
    """Save the DataFrame to a Parquet file."""
    try:
        dataframe.to_parquet(local_file, engine="pyarrow", index=False)
        logging.info("Data successfully saved to Parquet file: %s", local_file)
    except Exception as e:
        logging.error("Error saving DataFrame to Parquet file: %s", e)
        raise


def upload_to_s3(local_file: str, bucket: str, key: str) -> None:
    """Uploads a local file to S3."""
    try:
        s3_client = boto3.client("s3")
        s3_client.upload_file(local_file, bucket, key)
        logging.info(f"""File successfully uploaded to S3 bucket '{
                     bucket}' with key '{key}'.""")
    except Exception as e:
        logging.error("Error uploading file to S3: %s", e)
        raise


if __name__ == "__main__":

    try:
        connection = get_db_connection()
        complete_dataframe = load_data_to_dataframe(connection)

        save_to_parquet(complete_dataframe, LOCAL_PARQUET_FILE)

        upload_to_s3(LOCAL_PARQUET_FILE, S3_BUCKET, S3_KEY)

        if os.path.exists(LOCAL_PARQUET_FILE):
            os.remove(LOCAL_PARQUET_FILE)
            logging.info("Temporary Parquet file removed: %s",
                         LOCAL_PARQUET_FILE)

    except Exception as e:
        logging.error("An error occurred: %s", e)
