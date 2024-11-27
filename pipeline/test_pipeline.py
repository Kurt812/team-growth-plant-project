"""Tests for extracting raw data from API, transforming and loading into database."""
import unittest
from unittest.mock import MagicMock, patch
import requests
import pandas as pd
from extract import get_plant_data, parse_plant_data, extract_botanist_name
from transform import clean_plant_data
from load import get_db_connection, insert_botanists, insert_plants, insert_recordings, load_data_to_database


COLUMNS = [
    "plant_id", "plant_name", "soil_moisture", "temperature", "last_watered",
    "recording_at", "botanist_first_name", "botanist_last_name",
    "botanist_email", "botanist_phone"
]


class TestExtractScript(unittest.TestCase):
    """Tests for the extract portion of the pipeline."""

    @patch("extract.requests.get")
    def test_get_plant_data_success(self, mock_get):
        """Test get_plant_data successful."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "plant_id": 1, "name": "Test Plant"}

        result = get_plant_data(1)
        self.assertEqual(result["plant_id"], 1)
        self.assertEqual(result["name"], "Test Plant")

    @patch("extract.requests.get")
    def test_get_plant_data_unsuccessful(self, mock_get):
        """Test get_plant_data with an unsuccessful API response."""
        mock_get.return_value.status_code = 404
        mock_get.side_effect = requests.RequestException("API not found")

        result = get_plant_data(999)
        self.assertIsNone(result)

    @patch("extract.requests.get")
    def test_get_plant_data_sensor_error(self, mock_get):
        """Test get_plant_data when the API shows a sensor error."""
        mock_get.return_value.status_code = 404
        mock_get.return_value.json.return_value = {
            "error": "plant not found",
            "plant_id": 7
        }

        result = get_plant_data(7)

        self.assertIsNone(result)

    def test_extract_botanist_name(self):
        """Test extract_botanist_name function."""
        first_name, last_name = extract_botanist_name("Jakub Poskrop")
        self.assertEqual(first_name, "Jakub")
        self.assertEqual(last_name, "Poskrop")

    def test_parse_plant_data(self):
        """Test parse_plant_data function."""
        raw_data = {
            "plant_id": 1,
            "name": "Test Plant",
            "soil_moisture": 48.0,
            "temperature": 3.0,
            "last_watered": "2024-11-25T14:00:00",
            "recording_taken": "2024-11-25T13:00:00",
            "botanist": {
                "name": "Kurt Martin-Brown",
                "email": "krishna_kumar_seechurn@testemail.com",
                "phone": "123-456-7890"
            }
        }

        parsed_data = parse_plant_data(raw_data)

        self.assertEqual(parsed_data["plant_id"], 1)
        self.assertEqual(parsed_data["botanist_first_name"], "Kurt")
        self.assertEqual(parsed_data["botanist_last_name"], "Martin-Brown")
        self.assertEqual(parsed_data["botanist_email"],
                         "krishna_kumar_seechurn@testemail.com")
        self.assertEqual(parsed_data["botanist_phone"], "123-456-7890")


class TestTransformScript(unittest.TestCase):
    """Tests for the transform portion of the pipeline."""

    def test_clean_plant_data_typing_and_nan_removal(self):
        """Ensure proper data cleaning and type conversion."""
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

        self.assertFalse(cleaned_df.isnull().values.any())

        self.assertTrue(pd.api.types.is_datetime64_any_dtype(
            cleaned_df["recording_at"]))
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(
            cleaned_df["last_watered"]))
        self.assertTrue(pd.api.types.is_numeric_dtype(
            cleaned_df["soil_moisture"]))
        self.assertTrue(pd.api.types.is_numeric_dtype(
            cleaned_df["temperature"]))
        self.assertTrue(pd.api.types.is_numeric_dtype(cleaned_df["plant_id"]))

    def test_clean_plant_data_soil_moisture_range(self):
        """Ensure rows with invalid soil moisture are removed."""
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

        self.assertEqual(len(cleaned_df), 1)
        self.assertEqual(cleaned_df["plant_name"].iloc[0], "Rose")

    def test_clean_plant_data_invalid_dates(self):
        """Ensure rows with invalid dates are removed."""
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

        self.assertEqual(len(cleaned_df), 1)
        self.assertEqual(cleaned_df["plant_name"].iloc[0], "Rose")

    def test_clean_plant_data_empty_df(self):
        """Test behavior on an empty dataframe."""
        plant_df = pd.DataFrame(columns=COLUMNS)
        cleaned_df = clean_plant_data(plant_df)

        self.assertTrue(cleaned_df.empty)


class TestLoadScript(unittest.TestCase):
    """Tests for the load portion of the pipeline."""

    @patch("load.pymssql.connect")
    def test_get_db_connection_success(self, mock_connect):
        """Test successful database connection."""
        mock_connect.return_value = MagicMock()
        connection = get_db_connection()
        self.assertIsNotNone(connection)
        mock_connect.assert_called_once()

    @patch("load.pymssql.connect")
    def test_get_db_connection_failure(self, mock_connect):
        """Test failed database connection."""
        mock_connect.side_effect = Exception("Connection failed")
        with self.assertRaises(Exception):
            get_db_connection()
        mock_connect.assert_called_once()

    def test_insert_botanists(self):
        """Test inserting botanists into the database."""
        mock_cursor = MagicMock()
        data = {
            "botanist_first_name": ["Jakub", "Ellie"],
            "botanist_last_name": ["Poskrop", "Bradley"],
            "botanist_email": ["jakub@example.com", "ellie@example.com"],
            "botanist_phone": ["1234567890", "0987654321"],
        }
        transformed_df = pd.DataFrame(data)

        insert_botanists(mock_cursor, transformed_df)

        self.assertEqual(mock_cursor.execute.call_count, 2)
        mock_cursor.execute.assert_any_call(
            """
            IF NOT EXISTS (
                SELECT 1 FROM gamma.botanist
                WHERE first_name = %s AND last_name = %s AND email = %s AND phone = %s
            )
            BEGIN
                INSERT INTO gamma.botanist (first_name, last_name, email, phone)
                VALUES (%s, %s, %s, %s)
            END
            """,
            (
                'Ellie', 'Bradley', 'ellie@example.com', '0987654321',
                'Ellie', 'Bradley', 'ellie@example.com', '0987654321'
            )
        )

    def test_insert_plants(self):
        """Test inserting plants into the database."""
        mock_cursor = MagicMock()
        data = {
            "plant_id": [1, 2],
            "plant_name": ["Rose", "Tulip"],
            "botanist_first_name": ["Ellie", "Kurt"],
            "botanist_last_name": ["Bradley", "Martin-Brown"],
            "botanist_email": ["ellie@example.com", "kurt@example.com"],
            "botanist_phone": ["1234567890", "0987654321"],
        }
        transformed_df = pd.DataFrame(data)

        insert_plants(mock_cursor, transformed_df)

        self.assertEqual(mock_cursor.execute.call_count, 2)
        mock_cursor.execute.assert_any_call(
            """
            IF NOT EXISTS (
                SELECT 1 FROM gamma.plant
                WHERE plant_id = %s
            )
            BEGIN
                INSERT INTO gamma.plant (plant_id, botanist_id, plant_name)
                VALUES (%s, (SELECT botanist_id FROM gamma.botanist
                             WHERE first_name = %s AND last_name = %s
                             AND email = %s AND phone = %s), %s)
            END
            """,
            (2, 2, 'Kurt', 'Martin-Brown', 'kurt@example.com', '0987654321', 'Tulip')
        )

    def test_insert_recordings(self):
        """Test inserting recordings into the database."""
        mock_cursor = MagicMock()
        data = {
            "plant_id": [1, 2],
            "soil_moisture": [50, 60],
            "temperature": [20, 25],
            "last_watered": ["2023-11-01", "2023-11-02"],
            "recording_at": ["2023-11-25", "2023-11-26"],
        }
        transformed_df = pd.DataFrame(data)

        insert_recordings(mock_cursor, transformed_df)

        self.assertEqual(mock_cursor.execute.call_count, 2)
        mock_cursor.execute.assert_any_call(
            """
            INSERT INTO gamma.recording
            (plant_id, soil_moisture, temperature, last_watered, recording_at)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (2, 60, 25, '2023-11-02', '2023-11-26')
        )


if __name__ == "__main__":
    unittest.main()
