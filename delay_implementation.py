from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2

import pandas as pd
import numpy as np
import networkx as nx

# Load nodes and edges from csv file
node_df = pd.read_csv('node_eurocontrol_w_bases.csv', encoding='cp1252')
edge_df = pd.read_csv('edge_eurocontrol.csv')

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
print(G)
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

def create_data_matrix(matrix, node_df):
    data = {}
    data['distance_matrix'] = matrix
    data['num_vehicles'] = 200
    data['depot'] = 0
    return data

data = create_data_matrix(travel, node_df)

def time_callback(from_index, to_index):
    """Returns the travel time between the two nodes."""
    # Convert from routing variable Index to distance matrix NodeIndex.
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)
    return data['distance_matrix'][from_node][to_node]

# Define routing model
manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']), data['num_vehicles'], data['depot'])
routing = pywrapcp.RoutingModel(manager)

transit_callback_index = routing.RegisterTransitCallback(time_callback)
routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)



# Set search parameters
search_parameters = pywrapcp.DefaultRoutingSearchParameters()
search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
search_parameters.local_search_metaheuristic = (routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
search_parameters.time_limit.seconds = 30

# Solve the problem
solution = routing.SolveWithParameters(search_parameters)

# Extract the optimal route for each vehicle
for vehicle_id in range(data['num_vehicles']):
    index = routing.Start(vehicle_id)
    plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
    route_distance = 0
    while not routing.IsEnd(index):
        node_index = manager.IndexToNode(index)
        next_node_index = manager.IndexToNode(routing.NextVar(index).Value())
        route_distance += routing.GetArcCostForVehicle(node_index, next_node_index, vehicle_id)
        plan_output += ' {} ->'.format(node_index)
        index = routing.NextVar(index)
    node_index = manager.IndexToNode(index)
    plan_output += ' {}\n'.format(node_index)
    route_distance += routing.GetArcCostForVehicle(node_index, manager.Start(vehicle_id), vehicle_id)
    plan_output += 'Distance of the route: {} minutes\n'.format(route_distance)
    print(plan_output)


# Define depot index
# for i in range(len(node_df)):
#     if node_df['base'][i] == 1:
#         routing.AddDepot(i)
#         break

# # Define cost function
# def cost_function(from_index, to_index):
#     delay_time = sum(delay_index[from_index:to_index+1])
#     return travel_times[from_index][to_index] + delay_time

# transit_callback_index = routing.RegisterTransitCallback(cost_function)

# # Define transit cost dimension
# routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)