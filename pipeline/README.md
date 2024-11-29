Plant Data ETL Pipeline - API Endpoint to RDS
=================================

Overview
--------
This folder implements an **ETL (Extract, Transform, Load)** pipeline for plant data. The pipeline retrieves data 
from a public API, cleans and transforms the data, and loads it into a SQL Server database. The scripts are modular and 
handle each phase of the ETL process independently.

Architecture
------------
The pipeline is divided into three key components:
1. **Extraction**: Extract raw data from an API.
2. **Transformation**: Clean and validate the data.
3. **Loading**: Insert the cleaned data into a database.

Scripts
-------
### 1. `pipeline.py`
The `pipeline.py` script orchestrates the entire ETL process by calling the extraction, transformation, and loading scripts 
in sequence.

- **Functions**:
  - `run_extraction()`: Extracts raw data from the API and returns a Pandas DataFrame.
  - `run_transformation(raw_df: pd.DataFrame)`: Cleans and validates the extracted data.
  - `run_loading(cleaned_df: pd.DataFrame)`: Loads the cleaned data into the SQL Server database.
  - `run_pipeline()`: Orchestrates the ETL process.

### 2. `extract.py`
Handles the extraction of raw data from the API.

- **Functions**:
  - `get_plant_data(plant_id: int) -> dict`: Fetches data for a specific plant ID from the API.
  - `parse_plant_data(raw_data: dict) -> dict`: Parses and structures raw data into a dictionary.
  - `extract_botanist_name(name: str) -> tuple`: Splits the botanist's full name into first and last name.
  - `process_data()`: Extracts all plant data and saves it as a CSV file.

- **Output**: Returns raw data as a Pandas DataFrame.

### 3. `transform.py`
Handles the cleaning and validation of the raw data.

- **Functions**:
  - `clean_plant_data(plant_df: pd.DataFrame) -> pd.DataFrame`: Cleans and validates the data, including:
    - Converting data types.
    - Removing invalid rows (e.g., missing or invalid dates, values out of range).
    - Stripping unnecessary characters.

- **Output**: Returns cleaned data as a Pandas DataFrame.

### 4. `load.py`
Loads the cleaned data into a SQL Server database.

- **Functions**:
  - `get_db_connection() -> pymssql.Connection`: Establishes a connection to the database.
  - `insert_botanists(cursor: pymssql.Cursor, transformed_df: pd.DataFrame)`: Inserts botanists into the database.
  - `insert_plants(cursor: pymssql.Cursor, transformed_df: pd.DataFrame)`: Inserts plants into the database.
  - `insert_recordings(cursor: pymssql.Cursor, transformed_df: pd.DataFrame)`: Inserts recordings into the database.
  - `load_data_to_database(connection: pymssql.Connection, transformed_df: pd.DataFrame)`: Handles the full data loading process.

How to Run the Pipeline
-----------------------
1. **Install Dependencies**:
   Ensure you have Python installed and set up a virtual environment(- Python 3.9) Install dependencies by running:
   ```bash
    pip3 install -r requirements.txt
    ```

2. **Set Up Environment Variables**:
    Use a `.env` file to provide database credentials and schema information:
    DB_HOST=<your_database_host> DB_NAME=<your_database_name> DB_USER=<your_database_user> DB_PASSWORD=<your_database_password> DB_PORT=<your_database_port> SCHEMA_NAME=<your_schema_name>

3. **Run the Pipeline**:
    Execute the pipeline by running:
    ```bash
    python3 pipeline.py
    ```


Testing
-------
Unit tests for the pipeline are located in the `test_pipeline.py` script. Run tests using `pytest`:
    ```bash
    pytest test_pipeline.py
    ```

Folder Structure
----------------
- **pipeline.py**: Main pipeline orchestration script.
- **extract.py**: Handles data extraction from the API.
- **transform.py**: Handles data cleaning and transformation.
- **load.py**: Handles data loading into the database.
- **test_pipeline.py**: Contains unit tests for all pipeline components.

