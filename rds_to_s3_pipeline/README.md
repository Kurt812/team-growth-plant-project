ETL Pipeline - RDS to S3
=================================

Overview
--------
This folder implements an **ETL (Extract, Transform, Load)** pipeline designed to extract plant data from an RDS database, transform the data into a structured format, and upload it as a Parquet file to an AWS S3 bucket.


Features
------------
1. **Extraction**: Connects to an RDS database and queries plant data using `pymssql`.
2. **Transformation**: Converts the data into a Pandas DataFrame for further processing.
3. **Loading**: Saves the DataFrame as a timestamped Parquet file and uploads it to an S3 bucket.

Script
-------
### `etl_pipeline.py`
The `etl_pipeline.py` script is the main script for extracting data from RDS and uploading to S3

- **Functions**:
  - `get_db_connection()`: Establishes a connection to the RDS database using credentials from the .env file.
  - `load_data_to_dataframe(db_connectionn: pymssql.Connection)`: Executes SQL queries to extract data from the RDS database into a Pandas DataFrame.
  - `save_to_parquet(dataframe: pd.DataFrame, file_date: str))`: Converts the DataFrame into a Parquet file and saves it locally with a timestamped filename.
  - `upload_to_s3(parquet_file: str, bucket: str, s3_key: str)`: Uploads the Parquet file to the specified AWS S3 bucket.


How to Run the Pipeline
-----------------------
1. **Install Dependencies**:
   Ensure you have Python installed and set up a virtual environment. Install dependencies by running:
   ```bash
    pip3 install -r requirements.txt
    ```

2. **Set Up Environment Variables**:
    Use a `.env` file to provide database credentials and schema information:
    DB_HOST=<your_database_host> DB_NAME=<your_database_name> DB_USER=<your_database_user> DB_PASSWORD=<your_database_password> DB_PORT=<your_database_port> SCHEMA_NAME=<your_schema_name>
    S3_BUCKET=<s3_bucket_name>
    ACCESS_KEY_ID=<your_AWS_access_key_id>
    SECRET_ACCESS_KEY=<your_AWS_secret_access_key>
    AWS_REGION=<aws_region>

3. **AWS Configuration**:

    Ensure the IAM user has the appropriate permissions to upload files to the S3 bucket.
    RDS Database Schema:

4. **The script assumes the following database schema**:

    gamma.plant
    gamma.recording
    gamma.botanist

5. **Run the Pipeline**:
    Execute the pipeline by running:
    ```bash
    python3 etl_pipeline.py
    ```

Testing
-------
Unit tests for the pipeline are located in the `test_etl_pipeline.py` script. Run tests using `pytest`:
    ```bash
    pytest test_etl_pipeline.py
    ```