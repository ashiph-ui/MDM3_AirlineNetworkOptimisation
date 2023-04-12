# Scheduling Flights with Airline Network Optimisation
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from ortools.sat.python import cp_model

locations = ["loc1", "loc2", "loc3", "loc4", "loc5"]
edges = [("loc1", "loc2"), ("loc2", "loc3"), ("loc3", "loc4"), ("loc4", "loc5"), ("loc5", "loc1")]


num_of_planes = 2
num_of_routes = len(edges)
time_slots = 10

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

# Each plane can only be used 5 times - plane can only be used 5 times
for p in all_planes:
    model.Add(sum(x[p, r, t] for r in all_routes for t in all_time_slots) <= 3)

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
            if not (i, j) in edges:
                model.Add(x[p, r, t] == 0)

# plane p can use route r at most once
for p in all_planes:
    for r in all_routes:
        model.Add(sum(x[p, r, t] for t in all_time_slots) <= 1)

for p in all_planes:
    model.Add(sum(x[p, r, t] for r in all_routes for t in all_time_slots) >= 1)
    # Ensure that the last route ends at the starting node
    model.Add(sum(x[p, r, time_slots-1] for r in all_routes) * y[p, 0] == 1)

# CONSTRAINTS TO ADD: 
# 1. Route = edge(i,j) so route can only be used if j at time t-1 is the same as i at time t
# 2. ensure that the last route ends at the starting node (Bases)
# 3. Find a way to assign starting nodes to planes evenly 


# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print the solution
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    for p in all_planes:
        for r in all_routes:
            for t in all_time_slots:
                if solver.Value(x[p, r, t]) == 1:
                    # for route print appropriate edge
                    print("Plane", p, "uses route", edges[r], "at time", t)


                    

