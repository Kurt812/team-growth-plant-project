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


def get_db_connection():
    """Establish a connection to the SQL Server database using pymssql."""
    try:
        conn = pymssql.connect(
            host=DB_CONFIG["server"],
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
            botanist_key = (row["botanist_first_name"], row["botanist_last_name"],
                            row["botanist_email"], row["botanist_phone"])
            if botanist_key not in botanist_ids:
                cursor.execute(
                    """
                    INSERT INTO botanist (first_name, last_name, email, phone)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        row["botanist_first_name"],
                        row["botanist_last_name"],
                        row["botanist_email"],
                        row["botanist_phone"],
                    ),
                )
                cursor.execute("SELECT @@IDENTITY")
                botanist_ids[botanist_key] = cursor.fetchone()[0]

        conn.commit()
        logging.info("Botanists inserted successfully.")

        logging.info("Inserting plants and recordings into the database...")
        for _, row in transformed_df.iterrows():
            botanist_key = (row["botanist_first_name"], row["botanist_last_name"],
                            row["botanist_email"], row["botanist_phone"])
            botanist_id = botanist_ids[botanist_key]

            cursor.execute(
                """
                INSERT INTO plant (plant_id, botanist_id, plant_name)
                VALUES (%s, %s, %s)
                """,
                (row["plant_id"], botanist_id, row["plant_name"]),
            )

            cursor.execute(
                """
                INSERT INTO recording (plant_id, soil_moisture, temperature, last_watered, recording_at)
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
        logging.info("Plants and recordings inserted successfully.")

    except pymssql.DatabaseError as e:
        logging.error("Error occurred: %s", e)
        conn.rollback()
        raise


if __name__ == "__main__":
    try:
        cleaned_df = pd.read_csv(CLEANED_FILE)
        conn = get_db_connection()
        load_data_to_database(conn, cleaned_df)
        conn.close()

        logging.info("Data loading process completed successfully.")
    except FileNotFoundError:
        logging.error("Cleaned data file not found: %s", CLEANED_FILE)
