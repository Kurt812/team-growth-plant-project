"""Pipeline script to extract plant data from an API, transform it, and load it into a database."""

import logging
import os
import pandas as pd
from dotenv import load_dotenv
import extract
import transform
import load
logging.basicConfig(level=logging.INFO)

RAW_DATA_FILE = os.path.join("../data", "plant_data.csv")
CLEANED_DATA_FILE = os.path.join("../data", "cleaned_plant_data.csv")

load_dotenv()


def make_data_directory() -> None:
    """Ensure the ../data directory exists for storing intermediate files."""
    data_dir = os.path.dirname(RAW_DATA_FILE)
    if not os.path.exists(data_dir):
        logging.info("Creating data directory: %s", data_dir)
        os.makedirs(data_dir)


def run_extraction() -> None:
    """Run the extraction process to retrieve raw plant data from the API."""
    logging.info("Starting the extraction process...")
    extract.main()
    logging.info("Extraction completed. Raw data saved to %s", RAW_DATA_FILE)


def run_transformation() -> pd.DataFrame:
    """Run the transformation process to clean the extracted data."""
    logging.info("Starting the transformation process...")
    raw_df = pd.read_csv(RAW_DATA_FILE)
    cleaned_df = transform.clean_plant_data(raw_df)
    cleaned_df.to_csv(CLEANED_DATA_FILE, index=False)
    logging.info(
        "Transformation completed. Cleaned data saved to %s", CLEANED_DATA_FILE)
    return cleaned_df


def run_loading(cleaned_df: pd.DataFrame) -> None:
    """Run the loading process to insert cleaned data into the SQL Server database."""
    logging.info("Starting the loading process...")
    conn = load.get_db_connection()
    load.load_data_to_database(conn, cleaned_df)
    conn.close()
    logging.info(
        "Loading completed. Data successfully loaded into the database.")


def run_pipeline() -> None:
    """Main function to execute the ETL pipeline."""
    try:
        make_data_directory()

        run_extraction()

        cleaned_df = run_transformation()

        run_loading(cleaned_df)

        logging.info("ETL pipeline completed successfully.")

    except Exception as e:
        logging.error("Pipeline execution failed: %s", e)
        raise


if __name__ == "__main__":
    run_pipeline()
