import pandas as pd
import pymssql
import logging
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "username": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": os.getenv("DB_PORT")
}

CLEANED_FILE = os.path.join("../data", "cleaned_plant_data.csv")
SCHEMA_NAME = os.getenv("SCHEMA_NAME")


def get_db_connection():
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


def load_data_to_database(conn, transformed_df):
    """Load transformed data into the database."""
    try:
        cursor = conn.cursor()

        logging.info("Inserting botanists into the database...")
        botanist_ids = {}
        for _, row in transformed_df.iterrows():
            cursor.execute(
                f"""
                IF NOT EXISTS (
                    SELECT 1 FROM {SCHEMA_NAME}.botanist
                    WHERE first_name = %s AND last_name = %s AND email = %s AND phone = %s
                )
                BEGIN
                    INSERT INTO {SCHEMA_NAME}.botanist (first_name, last_name, email, phone)
                    VALUES (%s, %s, %s, %s)
                END
                """,
                (
                    row["botanist_first_name"],
                    row["botanist_last_name"],
                    row["botanist_email"],
                    row["botanist_phone"],
                    row["botanist_first_name"],
                    row["botanist_last_name"],
                    row["botanist_email"],
                    row["botanist_phone"],
                ),
            )

        conn.commit()
        logging.info("Botanists inserted successfully.")

        logging.info("Inserting plants into the database...")
        for _, row in transformed_df.iterrows():
            cursor.execute(
                f"""
                IF NOT EXISTS (
                    SELECT 1 FROM {SCHEMA_NAME}.plant
                    WHERE plant_id = %s
                )
                BEGIN
                    INSERT INTO {SCHEMA_NAME}.plant (plant_id, botanist_id, plant_name)
                    VALUES (%s, (SELECT botanist_id FROM {SCHEMA_NAME}.botanist
                                 WHERE first_name = %s AND last_name = %s AND email = %s AND phone = %s), %s)
                END
                """,
                (
                    row["plant_id"],
                    row["plant_id"],
                    row["botanist_first_name"],
                    row["botanist_last_name"],
                    row["botanist_email"],
                    row["botanist_phone"],
                    row["plant_name"],
                ),
            )

        conn.commit()
        logging.info("Plants inserted successfully.")

        logging.info("Inserting recordings into the database...")
        for _, row in transformed_df.iterrows():
            cursor.execute(
                f"""
                INSERT INTO {SCHEMA_NAME}.recording (plant_id, soil_moisture, temperature, last_watered, recording_at)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    row["plant_id"],
                    row["soil_moisture"],
                    row["temperature"],
                    row["last_watered"],
                    row["recording_at"],
                ),
            )

        conn.commit()
        logging.info("Recordings inserted successfully.")

    except pymssql.DatabaseError as e:
        logging.error("Error occurred: %s", e)
        conn.rollback()
        raise


if __name__ == "__main__":
    try:
        logging.info("Loading cleaned data from %s", CLEANED_FILE)
        cleaned_df = pd.read_csv(CLEANED_FILE)
        conn = get_db_connection()

        load_data_to_database(conn, cleaned_df)
        conn.close()
        logging.info("Data loading process completed successfully.")
    except FileNotFoundError:
        logging.error("Cleaned data file not found: %s", CLEANED_FILE)
