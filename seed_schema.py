'''
Module to initially seed the botanist and plant tables with the 
static data (botanist names and contact info and plant names and their botanists)
'''
from os import environ
from dotenv import load_dotenv
import pymssql
from pymssql import connect, Cursor, Connection
import requests
import logging

logging.basicConfig(level=logging.INFO)

NUM_OF_PLANTS = 50
BASE_URL = "https://data-eng-plants-api.herokuapp.com/plants/"


def get_connection() -> Connection:
    '''Function to get the connection to the database'''
    logging.info("Connecting to the database")
    try:
        return connect(server=environ["DB_HOST"],
                       user=environ["DB_USER"],
                       port=environ["DB_PORT"],
                       database=environ["DB_NAME"],
                       password=environ["DB_PASSWORD"])
    except pymssql.exceptions.Error as e:
        logging.error("Failed to connect to the database - %s", e)
        return None


def get_cursor(conn: Connection) -> Cursor:
    '''Function to get the cursor for the connection to the database'''
    return conn.cursor()


def get_data() -> None:
    '''Function to get all of the botanists and plants data'''
    plants_details = []
    for plant_id in range(1, NUM_OF_PLANTS+1):
        logging.info("Retrieving data for plant ID %s", plant_id)
        response = requests.get(f"{BASE_URL}{plant_id}", timeout=10)
        if response.status_code != 200:
            logging.error("Failed to retrieve data on plant ID %s", plant_id)
            continue
        data = response.json()
        plants_details.append(
            {"plant_id": data["plant_id"], "name": data["name"], "botanist": data["botanist"]})
    return plants_details


def insert_botanist(botanist_info: dict, cursor: Cursor) -> None:
    '''Function to insert a new botanist row into the botanist table and returns the botanist_id of the row'''
    first_name = botanist_info["name"].split()[0]
    last_name = botanist_info["name"].split()[-1]
    email = botanist_info["email"]
    phone = botanist_info["phone"]
    cursor.execute(f"""INSERT INTO {environ["SCHEMA_NAME"]}.botanist(
                   first_name, last_name, email, phone)
                   VALUES
                   ('{first_name}','{last_name}','{email}','{phone}');
                   SELECT SCOPE_IDENTITY();""")
    botanist_id = cursor.fetchone()
    return botanist_id[0]


def get_foreign_id(plant_botanist: dict, botanists: dict) -> int:
    '''Function to get the botanist_id for a botanist'''
    botanist_id = [key for key, value in botanists.items()
                   if value == plant_botanist]
    return botanist_id[0]


def seed_data(plants_data: list[dict]) -> None:
    connection = get_connection()
    cursor = get_cursor(connection)
    botanists = {}
    for plant in plants_data:
        if plant["botanist"] not in botanists.values():
            botanist_id = insert_botanist(plant["botanist"], cursor)
            botanists[botanist_id] = plant["botanist"]
        plant_name = plant["name"]
        plant_id = plant["plant_id"]
        botanist_foreign_id = get_foreign_id(plant["botanist"], botanists)
        cursor.execute(f"""INSERT INTO {environ["SCHEMA_NAME"]}.plant(
                       plant_id, botanist_id,plant_name)
                       VALUES
                       ({plant_id},{botanist_foreign_id},'{plant_name}');""")
        connection.commit()


if __name__ == "__main__":
    load_dotenv()
    plants = get_data()
    seed_data(plants)
