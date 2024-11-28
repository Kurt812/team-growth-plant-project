"""
ETL Pipeline: Extract, Transform, and Load Plant Data

This script performs the following steps as part of an ETL pipeline:
1. Extracts plant data from an RDS database using pymssql.
2. Transforms the data into a Pandas DataFrame.
3. Saves the DataFrame as a Parquet file with a timestamped filename.
4. Uploads the Parquet file to an AWS S3 bucket.
"""

# pylint: disable=no-member
import os
import logging
from datetime import datetime
import boto3
import pymssql
import pandas as pd
from dotenv import load_dotenv
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

AWS_CREDENTIALS = {
    "aws_access_key_id": os.getenv("ACCESS_KEY_ID"),
    "aws_secret_access_key": os.getenv("SECRET_ACCESS_KEY"),
    "region_name": os.getenv("AWS_REGION", "eu-west-2"),
}

S3_BUCKET = os.getenv("S3_BUCKET")
S3_KEY_PREFIX = os.getenv("S3_KEY", "plant_data/")


def get_aws_client(service_name: str) -> boto3.client:
    """Creates a Boto3 client using credentials from .env."""
    try:
        client = boto3.client(service_name, **AWS_CREDENTIALS)
        logging.info("AWS client for %s created successfully.", service_name)
        return client
    except NoCredentialsError as e:
        logging.error("AWS credentials not found: %s", e)
        raise
    except PartialCredentialsError as e:
        logging.error("Incomplete AWS credentials: %s", e)
        raise


def get_db_connection() -> pymssql.Connection:
    """Establish a connection to the SQL Server database using pymssql."""
    try:
        connection = pymssql.connect(
            server=DB_CONFIG["host"],
            user=DB_CONFIG["username"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            port=DB_CONFIG["port"]
        )
        logging.info("Database connection established.")
        return connection
    except pymssql.DatabaseError as e:
        logging.error("Failed to connect to the database: %s", e)
        raise


def load_data_to_dataframe(db_connectionn: pymssql.Connection) -> pd.DataFrame:
    """Extracts data from the RDS database into a pandas DataFrame."""

    query = """
    SELECT 
        p.plant_id, p.plant_name, r.soil_moisture, r.temperature, 
        r.last_watered, r.recording_at, 
        b.first_name AS botanist_first_name, b.last_name AS botanist_last_name,
        b.email AS botanist_email, b.phone AS botanist_phone
    FROM gamma.plant p
    JOIN gamma.recording r ON p.plant_id = r.plant_id
    JOIN gamma.botanist b ON p.botanist_id = b.botanist_id
    """

    try:
        dataframe = pd.read_sql(query, db_connectionn)
        logging.info("Data successfully loaded into DataFrame.")
        db_connectionn.close()
        logging.info("Database connection closed.")
        return dataframe
    except pymssql.DatabaseError as e:
        logging.error("Database error during data extraction: %s", e)
        raise


def clear_rds(db_connectionn: pymssql.Connection) -> None:
    query = "DELETE FROM gamma.recordings;"

    try:
        dataframe = pd.read_sql(query, db_connectionn)
        logging.info("Data successfully loaded into DataFrame.")
        db_connectionn.close()
        logging.info("Database connection closed.")
        return dataframe
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


def upload_to_s3(parquet_file: str, bucket: str, s3_key: str) -> None:
    """Uploads a local file to S3."""
    try:
        s3_client = get_aws_client("s3")
        s3_client.upload_file(parquet_file, bucket, s3_key)
        logging.info(
            "File successfully uploaded to S3 bucket '%s' with key '%s'.", bucket, s3_key
        )
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
    db_connection = get_db_connection()
    complete_dataframe = load_data_to_dataframe(db_connection)

    CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
    PARQUET_FILE = save_to_parquet(complete_dataframe, CURRENT_DATE)
    S3_KEY = f"{S3_KEY_PREFIX}{CURRENT_DATE}.parquet"

    if not isinstance(PARQUET_FILE, str):
        raise ValueError(f"""Expected string for local file, got {
                         type(PARQUET_FILE)}""")

    upload_to_s3(PARQUET_FILE, S3_BUCKET, S3_KEY)

    if os.path.exists(PARQUET_FILE):
        os.remove(PARQUET_FILE)
        logging.info("Temporary Parquet file removed: %s",
                     PARQUET_FILE)

    clear_rds(db_connection)
