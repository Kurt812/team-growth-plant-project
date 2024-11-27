"""Extracts the data from the RDS into a dataframe"""
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
import pymssql
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

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
S3_KEY_PREFIX = os.getenv("S3_KEY", "plant_data/")


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
    except pymssql.DatabaseError as e:
        logging.error("Database error during data extraction: %s", e)
        raise


def save_to_parquet(dataframe: pd.DataFrame, file_date: str) -> None:
    """Save the DataFrame to a Parquet file."""
    local_file = f"{file_date}.parquet"
    try:
        dataframe.to_parquet(local_file, engine="pyarrow", index=False)
        logging.info("Data successfully saved to Parquet file: %s", local_file)
        return local_file
    except ValueError as e:
        logging.error("Value error during Parquet file saving: %s", e)
        raise


def upload_to_s3(local_file: str, bucket: str, key: str) -> None:
    """Uploads a local file to S3."""
    try:
        s3_client = boto3.client("s3")
        s3_client.upload_file(local_file, bucket, key)
        logging.info(f"""File successfully uploaded to S3 bucket '{
                     bucket}' with key '{key}'.""")
    except FileNotFoundError as e:
        logging.error("File not found for S3 upload: %s", e)
        raise
    except NoCredentialsError as e:
        logging.error("AWS credentials not found: %s", e)
        raise
    except PartialCredentialsError as e:
        logging.error("Incomplete AWS credentials: %s", e)
        raise


if __name__ == "__main__":
    connection = get_db_connection()
    complete_dataframe = load_data_to_dataframe(connection)
    current_date = datetime.now().strftime("%Y-%m-%d")

    local_parquet_file = save_to_parquet(complete_dataframe, current_date)
    s3_key = f"{S3_KEY_PREFIX}{current_date}.parquet"

    if not isinstance(local_parquet_file, str):
        raise ValueError(f"""Expected string for local file, got {
                         type(local_parquet_file)}""")

    upload_to_s3(local_parquet_file, S3_BUCKET, s3_key)

    if os.path.exists(local_parquet_file):
        os.remove(local_parquet_file)
        logging.info("Temporary Parquet file removed: %s",
                     local_parquet_file)
