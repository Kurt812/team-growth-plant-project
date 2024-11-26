"""Transforms the plant data to make it ready for loading"""
import pandas as pd


def clean_plant_data(plant_df: pd.DataFrame) -> pd.DataFrame:
    """Setting the types for dataframe columns and removing NaN values"""

    plant_df['recording_at'] = pd.to_datetime(plant_df['recording_at'])
    plant_df['last_watered'] = pd.to_datetime(plant_df['last_watered'])
    plant_df['soil_moisture'] = pd.to_numeric(plant_df['soil_moisture'])
    plant_df['temperature'] = pd.to_numeric(plant_df['temperature'])
    plant_df['plant_id'] = pd.to_numeric(plant_df['plant_id'])
    plant_df = plant_df[(plant_df['soil_moisture'] >= 0) &
                        (plant_df['soil_moisture'] <= 100)]

    plant_df = plant_df.dropna()
    return plant_df
