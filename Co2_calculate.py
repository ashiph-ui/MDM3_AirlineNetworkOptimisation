import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import pandas as pd
from geopy.distance import distance
import csv


def copy_paste_csv(source_file: str, destination_file: str) -> None:
    """Copy and paste a csv file

    Args:
        source_file (str): source file
        destination_file (str): destination file

    Returns:
        None(a destination file is created which copies the source file)
    """
    with open(source_file, "r") as f:
        csv_reader = csv.reader(f)
        with open(destination_file, "w") as f:
            csv_writer = csv.writer(f)
            for row in csv_reader:
                csv_writer.writerow(row)


"""
copies "edge_list_final.csv" to "edge_eurocontrol.csv"
copy_paste_csv("edge_list_final.csv", "edge_eurocontrol.csv")
"""

# Read the data for finding coordinates
df_nodes: pd.DataFrame = pd.read_csv("node_eurocontrol")
icaos: np.ndarray = df_nodes["icao"].to_numpy()
lats: np.ndarray = df_nodes["lat"].to_numpy()
lons: np.ndarray = df_nodes["lon"].to_numpy()
# print(len(icaos)) # 106 why not the same as the number of unique icaos? was with node_list.csv
# print(len(df_nodes["icao"].unique()))# 105

# create a dictionary of icao: (lat, lon) which hold coordinates of each airport
icao_coord: dict = {}
for icao, lat, lon in zip(icaos, lats, lons):
    icao_coord[icao]: tuple = (lat, lon)

# Read the data for finding the different flights
df_edges: pd.DataFrame = pd.read_csv("edge_list_final.csv")
origin_airport_icao: np.ndarray = df_edges["origin_airport_icao"].to_numpy()
dest_airport_icao: np.ndarray = df_edges["destination_airport_icao"].to_numpy()

# get rid of airports with no delay data
origin_airport_icao_unique: set = set(origin_airport_icao)
dest_airport_icao_unique: set = set(dest_airport_icao)
# find difference between origin and nodes, destination and nodes, symmetric difference gets what not in both sets
mismatched_origin: set = set(origin_airport_icao_unique.symmetric_difference(icaos))
mismatched_dest: set = set(dest_airport_icao_unique.symmetric_difference(icaos))
total_mismatched: list = list(mismatched_origin.union(mismatched_dest))


def remove_unwanted_airports(
    df: pd.DataFrame, mismatched_airports: list
) -> pd.DataFrame:
    """Removes airports that are not in the nodes list

    Args:
        df (pd.DataFrame): dataframe of edges
        mismatched_airports (list): list of airports to be removed

    Returns:
        pd.DataFrame: dataframe of edges with airports removed
    """
    for airport in mismatched_airports:
        df = df[df["origin_airport_icao"] != airport]
        df = df[df["destination_airport_icao"] != airport]
    return df


df_edges = remove_unwanted_airports(df_edges, total_mismatched)
origin_airport_icao: np.ndarray = df_edges["origin_airport_icao"].to_numpy()
dest_airport_icao: np.ndarray = df_edges["destination_airport_icao"].to_numpy()

# finding the distance between airports
# PASSENGER_AVERAGE_CO2_EMISSIONS_PER_MILE = 89.9  # in grams per passenger per mile
PASSENGER_AVERAGE_CO2_EMISSIONS_PER_MILE = 79  # in grams per passenger per km


def find_distance(origin: str, destination: str) -> float:
    """Find the distance between two airports in km"""
    origin_coord: tuple = icao_coord[origin]
    dest_coord: tuple = icao_coord[destination]
    return distance(origin_coord, dest_coord).km


# print(orgin_airport_icao)
# print(icao_coord)
co2_array = np.zeros(len(origin_airport_icao))
dist_array = np.copy(co2_array)
for count, (origin, destination) in enumerate(
    zip(origin_airport_icao, dest_airport_icao)
):
    dist = find_distance(origin, destination)
    dist_array[count] = dist
    co2_array[count] = dist * PASSENGER_AVERAGE_CO2_EMISSIONS_PER_MILE

# add the co2 column to the dataframe
df_edges["co2"] = co2_array
df_edges["distance(km)"] = dist_array
print(df_edges.head())
"""
to create the new csv file for the eurocontrol edges
df_edges.to_csv("edge_eurocontrol.csv", index=False)
"""
""""""
