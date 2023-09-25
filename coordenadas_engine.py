import math

import pandas as pd
import geopandas as gpd
from shapely import Polygon, LineString
import matplotlib.pyplot as plt
import database_queries as db
from mpl_interactions import ioff, panhandler, zoom_factory
import utm


# function to create a hexagon around a point using h3
def create_hexagon(df):
    # get the vertices of the hexagon using the coordinates of the point and a radius of 5 meters

    df['hexagon_vertices'] = df.apply(lambda row: get_vertices_xy(utm.from_latlon(float(row['latitud']), float(row['longitud'])), 5),
                                      axis=1)
    # convert the vertices to latlon
    df['hexagon_vertices'] = df.apply(lambda row: [utm.to_latlon(row['hexagon_vertices'][i][0],
                                                                    row['hexagon_vertices'][i][1],
                                                                    row['hexagon_vertices'][i][2],
                                                                    row['hexagon_vertices'][i][3])[::-1] for i in
                                                    range(len(row['hexagon_vertices']))], axis=1)

    # create a polygon from the coordinates
    df['hexagon_polygon'] = df.apply(lambda row: Polygon(row['hexagon_vertices']), axis=1)
    # save the polygons in a geodataframe
    gdf = gpd.GeoDataFrame(df, geometry='hexagon_polygon')
    # gdf.crs = {'init': 'epsg:4326'}

    return gdf


# function to get the vertices of a hexagon
def get_vertices_xy(center, radius):
    vertices = []
    for i in range(0, 6):
        angle = 2 * math.pi / 6 * i
        x_i = center[0] + radius * math.cos(angle)
        y_i = center[1] + radius * math.sin(angle)
        vertices.append([x_i, y_i, center[2], center[3]])
    return vertices


# function to draw spots and coordinates
def draw_data(spots, coordinates, spots_visited=None):
    fig, ax = plt.subplots()
    # ax.set_axis_off()
    # plot the hexagons polygons
    spots.plot(ax=ax, color='white', edgecolor='black')
    coordinates_gdf = gpd.GeoDataFrame(coordinates, geometry=gpd.points_from_xy(coordinates.longitud, coordinates.latitud))
    # create a line from the coordinates points
    recorrido = coordinates_gdf.groupby('lote_id')['geometry'].apply(lambda x: LineString(x.tolist()))
    recorrido.plot(ax=ax, color='blue', markersize=1)

    # select the spots visited by a person in a day
    if spots_visited is not None:
        spots_visited = spots_visited[spots_visited['visited'] == 1]
        spots_visited.plot(ax=ax, color='red', edgecolor='black')

    # set the aspect of the plot
    fig.tight_layout()
    ax.set_aspect(1)
    ax.set_adjustable('datalim')
    # get the bigest value of the lon coordinates
    max_lon = coordinates['longitud'].max()
    ax.setxlim = (0, max_lon)
    ax = zoom_factory(ax, base_scale=1.1)
    ax = panhandler(fig)
    plt.show()


# function to get the spots visited by a person in a day using the coordinates
def get_spots_visited(spots, coordinates):
    # create a geodataframe with the coordinates
    coordinates_gdf = gpd.GeoDataFrame(coordinates, geometry=gpd.points_from_xy(coordinates.longitud, coordinates.latitud))
    # create a geodataframe with the spots
    spots_gdf = gpd.GeoDataFrame(spots, geometry='hexagon_polygon')
    # mark the spots visited by a person in a day
    spots_gdf['visited'] = spots_gdf.apply(lambda row: 1 if coordinates_gdf.within(row['hexagon_polygon']).any() else 0
                                           , axis=1)

    return spots_gdf






coordinates = db.get_coordinates(379, 37143, '2023-08-23')
# get the unique values of the column lote_id from the dataframe
lotes = coordinates['lote_id'].unique()
# get the spots using the unique values of the column lote_id
spots = db.get_spots(379, lotes)
# create a hexagon around each spot
hexagons = create_hexagon(spots)
spots_visited = get_spots_visited(hexagons, coordinates)

draw_data(hexagons, coordinates, spots_visited)
pass