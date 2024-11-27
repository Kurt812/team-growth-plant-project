"""Transforms the plant data to make it ready for loading"""
import pandas as pd
import logging
import os

logging.basicConfig(level=logging.INFO)

INPUT_FILE = os.path.join("../data", "plant_data.csv")
OUTPUT_FILE = os.path.join("../data", "cleaned_plant_data.csv")


def clean_plant_data(plant_df: pd.DataFrame) -> pd.DataFrame:
    """Setting the types for dataframe columns and removing NaN values"""

    plant_df['recording_at'] = pd.to_datetime(
        plant_df['recording_at'], errors='coerce', utc=True).dt.tz_convert(None)
    plant_df['last_watered'] = pd.to_datetime(
        plant_df['last_watered'], errors='coerce', utc=True).dt.tz_convert(None)
    plant_df['soil_moisture'] = pd.to_numeric(
        plant_df['soil_moisture'], errors='coerce')
    plant_df['temperature'] = pd.to_numeric(
        plant_df['temperature'], errors='coerce')
    plant_df['plant_id'] = pd.to_numeric(
        plant_df['plant_id'], errors='coerce')
    plant_df['plant_name'] = plant_df['plant_name'].str.strip(", ")

    plant_df = plant_df[(plant_df['soil_moisture'] >= 0) &
                        (plant_df['soil_moisture'] <= 100)]

    plant_df = plant_df.dropna()
    return plant_df


if __name__ == "__main__":
    try:
        logging.info("Loading raw data from %s", INPUT_FILE)
        raw_df = pd.read_csv(INPUT_FILE)
        cleaned_df = clean_plant_data(raw_df)
        cleaned_df.to_csv(OUTPUT_FILE, index=False)
        logging.info("Data transformation process completed successfully.")

    except FileNotFoundError:
        logging.error("Input file not found: %s", INPUT_FILE)
