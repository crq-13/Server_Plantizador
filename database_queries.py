# file where all the queries are stored for mysql database\
import h3 as h3
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode
from decouple import config
import pandas as pd
import geopandas as gpd
from shapely import Polygon, LineString
import matplotlib.pyplot as plt
import folium



# connection to the database using .env file
def create_server_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host=config('DB_HOST'),
            user=config('DB_USERNAME'),
            password=config('DB_PASSWORD'),
            database=config('DB_DATABASE')
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection


# function to execute queries and return the data
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        data = cursor.fetchall()
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")
    return data


# function to get coordinates by finca_id, persona_id and fecha
def get_coordinates(finca_id, persona_id, fecha):
    # build the table name
    prefix = 'coordenadas_'
    table_name = prefix + str(finca_id)
    # build dates for the query
    fecha1 = fecha + ' 00:00:00'
    fecha2 = fecha + ' 23:59:59'
    # build the query to get by persona_id and fecha
    query = f"SELECT coordenada_id, finca_id, persona_id, fecha, lat, lng, lote_id  FROM {table_name} WHERE persona_id = {persona_id} AND fecha between '{fecha1}' AND '{fecha2}'"
    # execute the query
    connection = create_server_connection()
    data = execute_query(connection, query)
    # create a dataframe with the data
    df = pd.DataFrame(data, columns=['id', 'finca_id', 'persona_id', 'fecha', 'latitud', 'longitud', 'lote_id'])
    return df
    pass


# function to get plants using the table plantas and take the coordinates of the plant using the inner with table spots
def get_spots(finca_id, lote_id):
    # build array of lote_id
    lote_id = tuple(lote_id)
    # build the query
    query = f"SELECT p.planta_id, p.nombre , s.finca_id, s.lote_id, s.lat, s.lng, s.linea, s.posicion FROM plantas p " \
            f"INNER JOIN spots s ON p.spot_id = s.spot_id WHERE s.finca_id = {finca_id} AND s.lote_id in {lote_id}"
    # execute the query
    connection = create_server_connection()
    data = execute_query(connection, query)
    # create a dataframe with the data
    df = pd.DataFrame(data, columns=['planta_id', 'nombre', 'finca_id', 'lote_id', 'latitud', 'longitud', 'linea', 'posicion'])
    return df




