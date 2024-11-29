# 🌱 Liverpool Natural History Museum - Plant Health Monitoring Dashboard

The Streamlit dashboard is a key component of the Liverpool Natural History Museum's plant monitoring project. It provides an interactive interface for visualising real-time and historical plant health data. The dashboard enables museum staff to monitor temperature and soil moisture trends, helping maintain the health of the plants in the botanical wing.

---

## Features

- **Real-Time Data Dashboard**:
  - View the latest temperature and soil moisture readings for each plant.
  - Filter plants dynamically using a dropdown menu.
  - Visualise real-time trends through interactive graphs.

- **Historical Data Dashboard**:
  - Query historical data stored in Amazon S3.
  - Allows users to filter data by plant name and date range.
  - Trend charts for historical temperature and soil moisture values.
  - Time-stamped axes for precise data analysis.

---

## Dashboard Architecture

The dashboard is part of the larger plant monitoring system and relies on the following components:

- Amazon RDS: Stores real-time data for the last 24 hours.
- Amazon S3: Archives historical data in Parquet format for long-term analysis.
- Streamlit: A lightweight web application framework for building interactive dashboards.

## Prerequisites
- An `.env` file with the following variables:
  - `DB_HOST`: Hostname of the RDS instance.
  - `DB_NAME`: Database name.
  - `DB_USER`: Username for the database.
  - `DB_PASSWORD`: Password for the database.
  - `DB_PORT`: Port for the database connection.
- Software Requirements:
  - Python 3.9
  - AWS CLI: Configured with access to your S3 bucket.
  - Docker: For running the application in a containerised environment.

---

## Running the Dashboard

### Local Development 

### 1. Install dependencies:

```bash
pip install -r requirements.txt
```

### 2. Run the application:

```bash
streamlit run app.py
```
The application will be available at http://localhost:8501.

### Docker Deployment

### 1. Build the docker image:

```bash
docker build -t plant-dashboard .
```

### 2. Run the Docker Container:

```bash
docker run -p 8501:8501 --env-file .env plant-dashboard
```
Access the dashboard at http://localhost:8501.

---

## User Interface

- **Navigation**:
  - Real-Time Dashboard: Displays the latest metrics for each plant, including temperature and soil moisture trends.
  - Historical Dashboard: Enables querying historical data by date range and plant name.

- **Visualisations**:
  - Interactive Altair charts for temperature and soil moisture trends.
  - Metrics displayed in the sidebar for quick insights.

---

## Future Improvements

- Add alerts for anomalous readings (e.g., low soil moisture or high temperature).
- Introduce role-based access controls for dashboard features.
- Optimise historical data querying for large datasets.
