"""Extracts the data from the RDS into a dataframe"""
import logging
import os
from dotenv import load_dotenv
import pandas as pd
import pymssql

logging.basicConfig(level=logging.INFO)
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "username": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": os.getenv("DB_PORT")
}


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


def load_data_to_dataframe(connection: pymssql.Connection, query: str) -> pd.DataFrame:
    """Extracts data from the RDS database into a pandas DataFrame."""
    try:
        df = pd.read_sql(query, connection)
        logging.info("Data successfully loaded into DataFrame.")
        return df
    except Exception as e:
        logging.error("Error loading data to DataFrame: %s", e)
        raise


def create_required_dataframes(connection: pymssql.Connection) -> tuple:
    """Creates the three required dataframes"""
    botanist_query = "SELECT * FROM gamma.botanist"
    plant_query = "SELECT * FROM gamma.plant"
    recording_query = "SELECT * FROM gamma.recording"

    botanists_df = load_data_to_dataframe(connection, botanist_query)
    plants_df = load_data_to_dataframe(connection, plant_query)
    recordings_df = load_data_to_dataframe(connection, recording_query)

    connection.close()
    logging.info("Database connection closed.")

    return botanists_df, plants_df, recordings_df


if __name__ == "__main__":

    try:
        connection = get_db_connection()

        botanists_df, plants_df, recordings_df = create_required_dataframes(
            connection)

        print(botanists_df.head())
        print(plants_df.head())
        print(recordings_df.head())

    except Exception as e:
        logging.error("An error occurred: %s", e)
