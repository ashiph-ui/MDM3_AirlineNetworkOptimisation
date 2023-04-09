from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2
from Co2_calculate import *
from network_flow_opt import *

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

shortest_path_time = dict(nx.all_pairs_dijkstra_path_length(G_time))
shortest_path_distance = dict(nx.all_pairs_dijkstra_path_length(G_distance))
print(shortest_path_distance)
def travel_time_matrix(G):
    # Create the travel time matrix
    travel_time = 0
    n_nodes = len(G.nodes)
    travel_time_matrix = [[None]*n_nodes for i in range(n_nodes)]
    for i, origin in enumerate(G.nodes):
        for j, dest in enumerate(G.nodes):
            if i!=j:
                try :
                    travel_time = shortest_path_time[origin][dest]
                except KeyError:
                    travel_time = np.inf
            travel_time_matrix[i][j] = travel_time
            
    return travel_time_matrix

def distance_matrix(G):
    # Create the distance matrix
    distance = 0
    n_nodes = len(G.nodes)
    distance_matrix = [[None]*n_nodes for i in range(n_nodes)]
    for i, origin in enumerate(G.nodes):
        for j, dest in enumerate(G.nodes):
            if i!=j:
                try :
                    distance = shortest_path_distance[origin][dest]
                except KeyError:
                    distance = np.inf
            distance_matrix[i][j] = distance
    return distance_matrix

travel = travel_time_matrix(G_time)
distance = distance_matrix(G_distance)

 # list of start nodes correponding to each plane leaving a base, using data form node df 

# Assuming you have a dataframe called "nodes_df" containing all the nodes with a "Type" column
# that identifies if the node is a base or not

# Filter nodes that have base=1
base_nodes = node_df[node_df['base'] == 1] 

# Create lists of start nodes and end nodes
bases_index = []

for _, node in base_nodes.iterrows():
    bases_index.append(node['NodeID'])
    

# get total distance of all flights
total_distance = df_edges['distance(km)'].sum()

def calculate_planes_needed(aircraft_range):
    num_planes = {}
    for base in bases_index:
        flights = num_flights[base]
        print(flights)
        distance_node = sum(distance[base])
        print(distance_node)
        num_planes[base] = int(round(flights * distance_node / (aircraft_range * 24 * 0.8)))
    return num_planes
num_planes = calculate_planes_needed(6300)
print(num_planes)
# get the start and end nodes for each plane using calculated number of planes per base
bases = []

for base in num_planes:
    for i in range(num_planes[base]):
        bases.append(base)
def create_data_model(matrix):
    data = {}
    data['distance_matrix'] = matrix
    data['num_vehicles'] = 127
    data['bases_index'] = bases_index
    data['flights'] = num_flights
    data['bases_plane'] = bases
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
data = create_data_model(travel) 


     
# Create the routing index manager.
manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                       data['num_vehicles'], data['start'],data['end'])

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

# Define cost of each arc.
routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

# Add Distance constraint.
dimension_name = 'Distance'
routing.AddDimension(
    transit_callback_index,
    0,  # no slack
    5000,  # vehicle maximum travel distance
    True,  # start cumul to zero
    dimension_name)
distance_dimension = routing.GetDimensionOrDie(dimension_name)
distance_dimension.SetGlobalSpanCostCoefficient(100)


# Setting first solution heuristic.
search_parameters = pywrapcp.DefaultRoutingSearchParameters()
search_parameters.first_solution_strategy = (
    routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

# Solve the problem.
solution = routing.SolveWithParameters(search_parameters)

# Print solution on console.
# if solution:
#     solution_dict = print_solution(data, manager, routing, solution)