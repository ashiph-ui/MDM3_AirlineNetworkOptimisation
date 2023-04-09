from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2

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
def create_networkx_graph(edge_df):
    G = nx.DiGraph()
    for index, row in edge_df.iterrows():
        G.add_edge(row['origin_airport_icao'], row['destination_airport_icao'], weight=row['flight_time_mn'])
    return G

G = create_networkx_graph(edge_df)

shortest_path = dict(nx.all_pairs_dijkstra_path_length(G))

def travel_time_matrix(G):
    # Create the travel time matrix
    travel_time = 0
    n_nodes = len(G.nodes)
    travel_time_matrix = [[None]*n_nodes for i in range(n_nodes)]
    for i, origin in enumerate(G.nodes):
        for j, dest in enumerate(G.nodes):
            if i!=j:
                try :
                    travel_time = shortest_path[origin][dest]
                except KeyError:
                    travel_time = np.inf
            travel_time_matrix[i][j] = travel_time
            
    return travel_time_matrix

travel = travel_time_matrix(G)
 # list of start nodes correponding to each plane leaving a base, using data form node df 

# Assuming you have a dataframe called "nodes_df" containing all the nodes with a "Type" column
# that identifies if the node is a base or not

# Filter nodes that have base=1
base_nodes = node_df[node_df['base'] == 1]
print(len(base_nodes))
# Create lists of start nodes and end nodes
start_nodes = []
end_nodes = []
for _, node in base_nodes.iterrows():
    for i in range(10):
        start_nodes.append(node['NodeID'])
        end_nodes.append(node['NodeID'])

# Print the first 10 start and end nodes
print(start_nodes[:10])
print(end_nodes[:10])

def create_data_model(matrix):
    data = {}
    data['distance_matrix'] = matrix
    data['num_vehicles'] = 260
    data['start'] = start_nodes 
    data['end'] = end_nodes
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
if solution:
    solution_dict = print_solution(data, manager, routing, solution)