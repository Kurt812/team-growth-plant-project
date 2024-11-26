"""Tests for extracting raw data from API, transforming and loading into database."""
import unittest
from unittest.mock import patch
import requests
from extract import get_plant_data, parse_plant_data, extract_botanist_name


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


if __name__ == "__main__":
    unittest.main()
