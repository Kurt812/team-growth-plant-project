import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import pandas as pd
from etl_pipeline import (
    get_db_connection,
    load_data_to_dataframe,
    save_to_parquet,
    upload_to_s3
)


class TestETLPipeline(unittest.TestCase):
    """Unit tests for the RDS-to-S3 ETL pipeline."""

    @patch("etl_pipeline.pymssql.connect")
    def test_get_db_connection_success(self, mock_connect):
        """Test successful database connection."""
        mock_connect.return_value = MagicMock()
        connection = get_db_connection()
        self.assertIsNotNone(connection)
        mock_connect.assert_called_once()

    @patch("etl_pipeline.pymssql.connect")
    def test_get_db_connection_failure(self, mock_connect):
        """Test failed database connection."""
        mock_connect.side_effect = Exception("Connection failed")
        with self.assertRaises(Exception):
            get_db_connection()
        mock_connect.assert_called_once()

    @patch("etl_pipeline.pd.read_sql")
    def test_load_data_to_dataframe(self, mock_read_sql):
        """Test loading data from the database into a DataFrame."""
        mock_connection = MagicMock()
        mock_dataframe = pd.DataFrame(
            {"column1": [1, 2], "column2": ["a", "b"]})
        mock_read_sql.return_value = mock_dataframe

        dataframe = load_data_to_dataframe(mock_connection)
        self.assertIsNotNone(dataframe)
        self.assertTrue(mock_dataframe.equals(dataframe))

    def test_save_to_parquet_success(self):
        """Test saving DataFrame to a Parquet file."""
        dataframe = pd.DataFrame({"column1": [1, 2], "column2": ["a", "b"]})
        file_date = datetime.now().strftime("%Y-%m-%d")
        local_file = f"{file_date}.parquet"

        with patch("etl_pipeline.pd.DataFrame.to_parquet") as mock_to_parquet:
            save_to_parquet(dataframe, file_date)
            mock_to_parquet.assert_called_once_with(
                local_file, engine="pyarrow", index=False)

    @patch("etl_pipeline.boto3.client")
    def test_upload_to_s3_success(self, mock_boto_client):
        """Test successful upload to S3."""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        parquet_file = "test.parquet"
        bucket = "test-bucket"
        s3_key = "test-key/test.parquet"

        upload_to_s3(parquet_file, bucket, s3_key)
        mock_s3.upload_file.assert_called_once_with(
            parquet_file, bucket, s3_key)


if __name__ == "__main__":
    unittest.main()
