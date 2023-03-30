from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2
import pandas as pd
import numpy as np

# Load nodes and edges from csv file
node_df = pd.read_csv('node_list.csv')
edge_df = pd.read_csv('edge_list_final.csv')
delay_node_df = pd.read_csv('total_time_delay_cleaned.csv')

# Define travel times between airports (in minutes)
travel_times = edge_df['flight_time'].values.reshape((len(node_df), len(node_df)))

# Define delay index for each airport
delay_index = delay_node_df['Time_delayed_scale'].values

num_vehicles = 100
depot_index = 0
# Define routing model
manager = pywrapcp.RoutingIndexManager(len(travel_times), num_vehicles, depot_index)
routing = pywrapcp.RoutingModel(manager)

# Define cost function
def cost_function(from_index, to_index):
    delay_time = sum(delay_index[from_index:to_index+1])
    return travel_times[from_index][to_index] + delay_time

transit_callback_index = routing.RegisterTransitCallback(cost_function)

# Define transit cost dimension
routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

# Set search parameters
search_parameters = pywrapcp.DefaultRoutingSearchParameters()
search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
search_parameters.local_search_metaheuristic = (routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
search_parameters.time_limit.seconds = 10

# Solve the problem
solution = routing.SolveWithParameters(search_parameters)

# Extract the optimal route for each vehicle
for vehicle_id in range(num_vehicles):
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
