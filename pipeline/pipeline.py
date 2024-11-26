"""Pipeline script to extract plant data from an API, transform it, and load it into a database."""
import logging
import pandas as pd
from dotenv import load_dotenv
import extract
import transform
import load

logging.basicConfig(level=logging.INFO)

load_dotenv()


def run_extraction() -> pd.DataFrame:
    """Run the extraction process to retrieve raw plant data from the API."""
    logging.info("Starting the extraction process...")
    all_data = []

    for plant_id in extract.PLANT_IDS:
        raw_data = extract.get_plant_data(plant_id)
        if raw_data:
            parsed_data = extract.parse_plant_data(raw_data)
            if parsed_data:
                all_data.append(parsed_data)

    if not all_data:
        logging.warning("No data was extracted from the API.")
        raise ValueError("Extraction process resulted in an empty dataset.")

    raw_df = pd.DataFrame(all_data)
    logging.info(
        "Extraction completed. Retrieved data for %d plants.", len(raw_df))
    return raw_df


def run_transformation(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Run the transformation process to clean the extracted data."""
    logging.info("Starting the transformation process...")
    cleaned_df = transform.clean_plant_data(raw_df)
    logging.info(
        "Transformation completed. Cleaned data contains %d rows.", len(cleaned_df))
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
        raw_df = run_extraction()
        cleaned_df = run_transformation(raw_df)
        run_loading(cleaned_df)
        logging.info("ETL pipeline completed successfully.")

    except Exception as e:
        logging.error("Pipeline execution failed: %s", e)
        raise


if __name__ == "__main__":
    run_pipeline()
