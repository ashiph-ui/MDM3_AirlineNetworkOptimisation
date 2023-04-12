from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2
from Co2_calculate import *
from network_flow_opt import *
from make_network import *

import pandas as pd
import numpy as np
import networkx as nx

# Load nodes and edges from csv file
node_df = pd.read_csv('node_eurocontrol_w_bases.csv', encoding='cp1252')
edge_df = pd.read_csv('edge_eurocontrol_minute.csv', encoding='cp1252')

# Define travel times between airports (in minutes)
travel_times = edge_df['flight_time']

# Define delay index for each airport
delay_index = node_df['Time_delayed_scale'].values

# create travel time matrix using NetworkX
def create_networkx_graph(edge_df, weight: str):
    G = nx.DiGraph()
    for index, row in edge_df.iterrows():
        G.add_edge(row['origin_airport_icao'], row['destination_airport_icao'], weight=row[weight])
    return G

G_time = create_networkx_graph(edge_df, 'flight_time_mn')
G_distance = create_networkx_graph(df_edges, 'distance(km)')

# get list of tuples of origin and destination airports
def get_from_and_to(data):
    from_to = []
    origin = data['origin_airport_icao']
    destination = data['destination_airport_icao']
    for i in range(len(origin)):
        from_to.append((origin[i], destination[i]))
    return from_to

from_to = get_from_and_to(edge_df)

# use from_to to make a dictionary of destinations for each origin
def get_destinations(from_to):
    destinations = {}
    for i in range(len(from_to)):
        if from_to[i][0] in destinations:
            destinations[from_to[i][0]].append(from_to[i][1])
        else:
            destinations[from_to[i][0]] = [from_to[i][1]]
    return destinations

# Dictionary of destinations for each origin airport
destinations = get_destinations(from_to)

shortest_path_time = dict(nx.all_pairs_dijkstra_path_length(G_time))
shortest_path_distance = dict(nx.all_pairs_dijkstra_path_length(G_distance))
# print(shortest_path_distance)
def travel_time_matrix(G):
    # Create the travel time matrix
    n_nodes = len(G.nodes)
    travel_time_matrix = [[None]*n_nodes for i in range(n_nodes)]
    for i, origin in enumerate(sorted(G.nodes)):
        for j, dest in enumerate(sorted(G.nodes)):
            if (origin, dest) in G.edges:
                travel_time_matrix[i][j] = G.edges[origin, dest]['weight']
            else:
                travel_time_matrix[i][j] = 0
    return travel_time_matrix
# Filter nodes that have base=1
base_nodes = node_df[node_df['base'] == 1] 

# Create lists of start nodes and end nodes
bases_index = {}

for _, node in base_nodes.iterrows():
    bases_index[node['icao']] = node['NodeID']
node_list = list(node_df['icao'].unique())

def matrix_opt(G):
    # Create the distance matrix
    n_nodes = len(G.nodes)
    distance_matrix = [[0]*n_nodes for i in range(n_nodes)]
    for u, v, weight in G.edges.data('weight'):
        i = node_list.index(u)
        j = node_list.index(v)
        distance_matrix[i][j] = weight
    return distance_matrix

def distance_matrix_full(G):
    # Create the distance matrix
    n_nodes = len(G.nodes)
    distance_matrix = [[0]*n_nodes for i in range(n_nodes)]
    for i, origin in enumerate(sorted(G.nodes)):
        for j, dest in enumerate(sorted(G.nodes)):
            if i!=j:
                try:
                    distance_matrix[i][j] = int(shortest_path_distance[origin][dest])
                except KeyError:
                    distance_matrix[i][j] = 0
    return distance_matrix

travel = matrix_opt(G_time)
distance_opt =matrix_opt(G_distance)
distance_full = distance_matrix_full(G_distance)

 # list of start nodes correponding to each plane leaving a base, using data form node df 

# Assuming you have a dataframe called "nodes_df" containing all the nodes with a "Type" column
# that identifies if the node is a base or not


# get total distance of all flights
total_distance = df_edges['distance(km)'].sum()
print(len(travel[0]))
def calculate_planes_needed(aircraft_range):
    num_planes = {}
    for key, value in bases_index.items():
        flights = num_flights[key]
        distance_node = sum(distance_opt[value])
        num_planes[key] = int(round(flights * distance_node / (aircraft_range *24* 0.8)))
    return num_planes

num_planes = calculate_planes_needed(6300)

# create a list of the origin and destination airports index for each flight from edge_df
def get_flights_list():
    flights = []
    for index, row in df_edges.iterrows():
        flights.append((row['origin_airport_icao'], row['destination_airport_icao']))
    return flights
pickups = get_flights_list()
print(pickups)
# get the start and end nodes for each plane using calculated number of planes per base
def get_bases_list(num_planes):
    bases = []
    num_planes_list = list(num_planes)
    for base in num_planes_list:
        for i in range(num_planes[base]):
            bases.append(bases_index[base])
    return bases
bases = get_bases_list(num_planes)

def create_data_model(matrix):
    data = {}
    data['distance_matrix'] = matrix
    data['num_vehicles'] = len(bases)
    data['demands'] = supplies
    data['vehicle_capacities'] = [186] * len(bases)
    data['pickups_deliveries'] = pickups
    data['starts'] = bases
    data['ends'] = bases
    return data

def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    max_route_distance = 0
    solutions = {}
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        vehicle_solution = []
        while not routing.IsEnd(index):
            vehicle_solution.append(manager.IndexToNode(index))
            plan_output += ' {} -> '.format(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        plan_output += '{}\n'.format(manager.IndexToNode(index))
        plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        print(plan_output)
        max_route_distance = max(route_distance, max_route_distance)
        solutions[vehicle_id] = vehicle_solution
    print('Maximum of the route distances: {}m'.format(max_route_distance))
    return solutions

"""Solve the CVRP problem."""
# Instantiate the data problem.
data = create_data_model(distance_full) 

# Create the routing index manager.
manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                       data['num_vehicles'], data['starts'], data['ends'])

# Create Routing Model.
routing = pywrapcp.RoutingModel(manager)


# Create and register a transit callback.
def distance_callback(from_index, to_index):
    """Returns the distance between the two nodes."""
    # Convert from routing variable Index to distance matrix NodeIndex.
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)
    return data['distance_matrix'][from_node][to_node]

transit_callback_index = routing.RegisterTransitCallback(distance_callback)

def demand_callback(from_index):
    """Returns the demand of the node."""
    # Convert from routing variable Index to demands NodeIndex.
    from_node = manager.IndexToNode(from_index)
    return data['demands'][from_node]

demand_callback_index = routing.RegisterUnaryTransitCallback(
    demand_callback)


# Define cost of each arc.
routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

# Add Distance constraint.
dimension_name = 'Distance'
routing.AddDimension(
    transit_callback_index,
    0,  # no slack
    10000,  # vehicle maximum travel distance
    True,  # start cumul to zero
    dimension_name)
distance_dimension = routing.GetDimensionOrDie(dimension_name)
distance_dimension.SetGlobalSpanCostCoefficient(100)


# Setting first solution heuristic.
search_parameters = pywrapcp.DefaultRoutingSearchParameters()
search_parameters.local_search_metaheuristic = (
    routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
search_parameters.time_limit.seconds = 30
search_parameters.log_search = True
# Solve the problem.
solution = routing.SolveWithParameters(search_parameters)

# Print solution on console.
if solution:
    solution_dict = print_solution(data, manager, routing, solution)
else:
    print('No solution found !')
