import pandas as pd
from transform import clean_plant_data


COLUMNS = [
    "plant_id", "plant_name", "soil_moisture", "temperature", "last_watered",
    "recording_at", "botanist_first_name", "botanist_last_name",
    "botanist_email", "botanist_phone"
]


def test_clean_plant_data_typing_and_nan_removal():
    """Ensure proper data cleaning and type conversion"""
    data = {
        "plant_id": [1, 2, "invalid"],
        "plant_name": ["Rose", "Tulip", "Lily"],
        "soil_moisture": [50, "invalid", 30],
        "temperature": [20, 25, "invalid"],
        "last_watered": ["2023-11-01", "invalid_date", "2023-11-15"],
        "recording_at": ["2023-11-25", "invalid_date", "2023-11-25"],
        "botanist_first_name": ["Alice", "Bob", None],
        "botanist_last_name": ["Smith", "Johnson", "Brown"],
        "botanist_email": ["alice@example.com", "bob@example.com", None],
        "botanist_phone": ["1234567890", "0987654321", None],
    }
    plant_df = pd.DataFrame(data, columns=COLUMNS)
    cleaned_df = clean_plant_data(plant_df)

    assert not cleaned_df.isnull().values.any()

    assert pd.api.types.is_datetime64_any_dtype(cleaned_df["recording_at"])
    assert pd.api.types.is_datetime64_any_dtype(cleaned_df["last_watered"])
    assert pd.api.types.is_numeric_dtype(cleaned_df["soil_moisture"])
    assert pd.api.types.is_numeric_dtype(cleaned_df["temperature"])
    assert pd.api.types.is_numeric_dtype(cleaned_df["plant_id"])


def test_clean_plant_data_soil_moisture_range():
    """Ensure rows with invalid soil moisture are removed"""
    data = {
        "plant_id": [1, 2, 3],
        "plant_name": ["Rose", "Tulip", "Lily"],
        "soil_moisture": [50, 120, -10],  # 120 and -10 are invalid
        "temperature": [20, 25, 15],
        "last_watered": ["2023-11-01", "2023-11-15", "2023-11-15"],
        "recording_at": ["2023-11-25", "2023-11-25", "2023-11-25"],
        "botanist_first_name": ["Alice", "Bob", "Charlie"],
        "botanist_last_name": ["Smith", "Johnson", "Brown"],
        "botanist_email": ["alice@example.com", "bob@example.com", "charlie@example.com"],
        "botanist_phone": ["1234567890", "0987654321", "1122334455"],
    }
    plant_df = pd.DataFrame(data, columns=COLUMNS)
    cleaned_df = clean_plant_data(plant_df)

    assert len(cleaned_df) == 1
    assert cleaned_df["plant_name"].iloc[0] == "Rose"


def test_clean_plant_data_invalid_dates():
    """Ensures rows with invalid dates are removed"""
    data = {
        "plant_id": [1, 2],
        "plant_name": ["Rose", "Tulip"],
        "soil_moisture": [50, 60],
        "temperature": [20, 25],
        "last_watered": ["2023-11-15", "2023-11-15"],
        "recording_at": ["2023-11-25", "invalid_date"],  # One invalid date
        "botanist_first_name": ["Alice", "Bob"],
        "botanist_last_name": ["Smith", "Johnson"],
        "botanist_email": ["alice@example.com", "bob@example.com"],
        "botanist_phone": ["1234567890", "0987654321"],
    }
    plant_df = pd.DataFrame(data, columns=COLUMNS)
    cleaned_df = clean_plant_data(plant_df)

    assert len(cleaned_df) == 1
    assert cleaned_df["plant_name"].iloc[0] == "Rose"


def test_clean_plant_data_no_dropping():
    """Tests on valid dataframe"""
    data = {
        "plant_id": [1],
        "plant_name": ["Rose"],
        "soil_moisture": [50],
        "temperature": [20],
        "last_watered": ["2023-11-01"],
        "recording_at": ["2023-11-25"],
        "botanist_first_name": ["Alice"],
        "botanist_last_name": ["Smith"],
        "botanist_email": ["alice@example.com"],
        "botanist_phone": ["1234567890"],
    }
    plant_df = pd.DataFrame(data, columns=COLUMNS)
    cleaned_df = clean_plant_data(plant_df)

    assert len(cleaned_df) == 1
    assert cleaned_df.equals(plant_df)


def test_clean_plant_data_empty_df():
    """Tests result on empty dataframe"""
    plant_df = pd.DataFrame(columns=COLUMNS)
    cleaned_df = clean_plant_data(plant_df)

    assert cleaned_df.empty
