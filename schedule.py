# Scheduling Flights with Airline Network Optimisation
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from ortools.sat.python import cp_model

# Load nodes and edges from csv file
airports_df = pd.read_csv('MDM3_AirlineNetworkOptimisation\\node_eurocontrol_w_bases.csv', encoding='cp1252', index_col='NodeID')
flights_df = pd.read_csv('MDM3_AirlineNetworkOptimisation\\edge_eurocontrol_minute.csv', encoding='cp1252')
# append number of nodes and flights (arcs)
num_nodes = len(airports_df)
num_arcs = len(flights_df)

locations = airports_df['icao'].unique()

origin = airports_df['icao']
dest = airports_df['iata']

# print(len(list(zip(origin, dest))))
edges = list(zip(origin, dest))

num_of_planes = 77
num_of_routes = len(edges)
time_slots = 25





# locations = ["loc1", "loc2", "loc3", "loc4", "loc5"]
# edges = [("loc1", "loc2"), ("loc2", "loc3"), ("loc3", "loc4"), ("loc4", "loc5")]

# num_of_planes = 2
# num_of_routes = len(edges)
# time_slots = 10

all_planes = range(num_of_planes)
all_routes = range(num_of_routes)
all_time_slots = range(time_slots)

model = cp_model.CpModel()

# Create the decision variables
x = {}  # x[p, r, t] is 1 if plane p is used on route r at time t
y = {}  # y[p, r] 1 if plane p is used on route r - this will denote starting nodes


for p in all_planes:
    for r, edge in enumerate(edges):
        i, j = edge
        for t in all_time_slots:
            x[p, r, t] = model.NewBoolVar('x[%i,%i,%i]' % (p, r, t))

# Create the objective function
model.Minimize(sum(x[p, r, t] for p in all_planes for r in all_routes for t in all_time_slots)) 
# minimize the sum of all x[p, r, t] for all planes p, all routes r and all time slots t

for p in all_planes:
    for r in all_routes:
        y[p, r] = model.NewBoolVar('y[%i,%i]' % (p, r)) # create a new boolean variable y[p, r]

# Create the constraints
# Each plane at each time can use only one route - plane can only be used on one route at any given time
for p in all_planes:
    for t in all_time_slots:
        model.Add(sum(x[p, r, t] for r in all_routes) <= 1)

# Each plane must use at least one route and time slot - plane must be used at least once
for p in all_planes:
    model.Add(sum(x[p, r, t] for r in all_routes for t in all_time_slots) >= 1)

# # Each plane can only be used 6 times - plane can only be used 5 times
# for p in all_planes:
#     model.Add(sum(x[p, r, t] for r in all_routes for t in all_time_slots) <= 6)

# Each route must be used at least once - route must be used at least once
for r in all_routes:
    model.Add(sum(x[p, r, t] for p in all_planes for t in all_time_slots) >= 1)

# Each plane is assigned at most one starting node 
for p in all_planes:
    model.Add(sum(y[p, r] for r in all_routes) <= 1)

# Each plane can only travel on the edges in the list "edges"
for p in all_planes:
    for r in all_routes:
        for t in all_time_slots:
            (i, j) = edges[r]
            if not (i, j) in edges and i == locations.index(j) and j == locations.index(i):
                model.Add(x[p, r, t] == 0)

# plane p can use route r at most once
for p in all_planes:
    for r in all_routes:
        model.Add(sum(x[p, r, t] for t in all_time_slots) <= 1)

# These next two constraints work but could not do without online sources - need to understand them better
# How can we convert this to math notation for presentation

# next route must start at the same node as the previous route ended
for p in all_planes:
    for r in range(num_of_routes-1):  # iterate over all routes except the last one
        (i, j) = edges[r]
        (i_next, j_next) = edges[r+1]
        for t in range(time_slots-1):  # iterate over all time slots except the last one
            model.Add(x[p, r, t] == x[p, r+1, t+1]).OnlyEnforceIf(x[p, r, t]).OnlyEnforceIf(x[p, r+1, t+1])

for p in all_planes:
    for i in range(num_of_routes - 1):
        # Get the start and end times of the current edge and the next edge
        start_time_i = model.NewIntVar(0, time_slots, f'start_time_{p}_{i}')
        end_time_i = model.NewIntVar(0, time_slots, f'end_time_{p}_{i}')
        start_time_j = model.NewIntVar(0, time_slots, f'start_time_{p}_{i+1}')
        end_time_j = model.NewIntVar(0, time_slots, f'end_time_{p}_{i+1}')
        
        # Define the start and end times of the current edge
        model.Add(start_time_i == sum(t * x[p, i, t] for t in all_time_slots))
        model.Add(end_time_i == sum(t * x[p, i, t] for t in all_time_slots))
        
        # Define the start and end times of the next edge
        model.Add(start_time_j == sum(t * x[p, i+1, t] for t in all_time_slots))
        model.Add(end_time_j == sum(t * x[p, i+1, t] for t in all_time_slots))
        
        # Add the constraint that the start time of the next edge must be greater than or equal to the end time of the previous edge
        model.Add(start_time_j >= end_time_i)




# all planes must start at t = 0
# for p in all_planes:
#     model.Add(sum(x[p, r, 0] for r in all_routes) == 1)

# for p in all_planes:
#     model.Add(sum(x[p, r, t] for r in all_routes for t in all_time_slots) >= 1)
#     # Ensure that the last route ends at the starting node
#     model.Add(sum(x[p, r, time_slots-1] for r in all_routes) * y[p, 0] == 1)

# CONSTRAINTS TO ADD: 
# 1. Route = edge(i,j) so route can only be used if j at time t-1 is the same as i at time t
# 2. ensure that the last route ends at the starting node (Bases)
# 3. Find a way to assign starting nodes to planes evenly 


# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print the solution
if status == cp_model.OPTIMAL:
    for p in all_planes:
        for r in all_routes:
            for t in all_time_slots:
                if solver.Value(x[p, r, t]) == 1:
                    # for route print appropriate edge
                    print("Plane", p, "uses route", edges[r], "at time", t)
else:
    print("No solution found.")


                    

