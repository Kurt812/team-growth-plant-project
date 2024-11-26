"""Script to extract raw data from the API and save to a CSV file."""
import os
import logging
import requests
import pandas as pd

logging.basicConfig(level=logging.INFO)

BASE_URL = "https://data-eng-plants-api.herokuapp.com/plants/"
PLANT_IDS = range(1, 51)
OUTPUT_FILE = os.path.join("../data", "plant_data.csv")


def get_plant_data(plant_id: int) -> dict:
    """Get data for a plant from a specific plant ID from the API endpoint."""
    try:
        logging.info("Retrieving data for plant ID %s", plant_id)
        response = requests.get(f"{BASE_URL}{plant_id}", timeout=10)
        if response.status_code != 200:
            logging.error("Error retrieving data for plant ID %s: %s",
                          plant_id, response.json())
            return None
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error("Error retrieving data for plant ID %s: %s", plant_id, e)
        return None


def extract_botanist_name(name: str) -> tuple:
    """Extract and return the first and last name from the botanist name."""
    name_parts = name.split(" ")
    return name_parts[0], name_parts[1]


def parse_plant_data(raw_data: dict) -> dict:
    """Parse and transform raw plant data into a dictionary."""
    try:
        botanist = raw_data.get("botanist", {})
        botanist_name = botanist.get("name", "")
        botanist_first_name, botanist_last_name = extract_botanist_name(
            botanist_name)
        logging.info("Parsing data for plant ID %s", raw_data.get("plant_id"))

        return {
            "plant_id": raw_data.get("plant_id"),
            "plant_name": raw_data.get("name"),
            "soil_moisture": raw_data.get("soil_moisture"),
            "temperature": raw_data.get("temperature"),
            "last_watered": raw_data.get("last_watered"),
            "recording_at": raw_data.get("recording_taken"),
            "botanist_first_name": botanist_first_name,
            "botanist_last_name": botanist_last_name,
            "botanist_email": botanist.get("email"),
            "botanist_phone": botanist.get("phone")
        }

    except Exception as e:
        logging.error("Error parsing data: %s", e)
        return None


def process_data() -> None:
    """Main function to get, parse, and save plant data from the API to a CSV file."""
    all_data = []

    for plant_id in PLANT_IDS:
        raw_data = get_plant_data(plant_id)
        if raw_data:
            parsed_data = parse_plant_data(raw_data)
            all_data.append(parsed_data)

    if all_data:
        df = pd.DataFrame(all_data)
        df.to_csv(OUTPUT_FILE, index=False)
        logging.info("Data successfully saved as %s.", OUTPUT_FILE)
    else:
        logging.warning("No valid data was extracted.")


if __name__ == "__main__":
    process_data()
