# Scheduling Flights with Airline Network Optimisation
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from ortools.sat.python import cp_model

num_of_planes = 5
num_of_routes = 5
time_slots = 5

all_planes = range(num_of_planes)
all_routes = range(num_of_routes)
all_time_slots = range(time_slots)

model = cp_model.CpModel()

# Create the decision variables
x = {}  # x[p, r, t] is 1 if plane p is used on route r at time t


for p in all_planes: # for each plane p in all_planes 
    for r in all_routes: # for each route r in all_routes
        for t in all_time_slots: # for each time slot t in all_time_slots
            x[p, r, t] = model.NewBoolVar('x[%i,%i,%i]' % (p, r, t)) # create a new boolean variable x[p, r, t]
# Create the objective function
model.Minimize(sum(x[p, r, t] for p in all_planes for r in all_routes for t in all_time_slots)) 
# minimize the sum of all x[p, r, t] for all planes p, all routes r and all time slots t

# Create the constraints
# Each plane at each time can use only one route - plane can only be used on one route at a time
for p in all_planes:
    for t in all_time_slots:
        model.Add(sum(x[p, r, t] for r in all_routes) <= 1)

# Each plane must use at least one route and time slot - plane must be used at least once
for p in all_planes:
    model.Add(sum(x[p, r, t] for r in all_routes for t in all_time_slots) >= 1)

# Each route must be used at least once - route must be used at least once
for r in all_routes:
    model.Add(sum(x[p, r, t] for p in all_planes for t in all_time_slots) >= 1)


# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print the solution
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    for p in all_planes:
        for r in all_routes:
            for t in all_time_slots:
                if solver.Value(x[p, r, t]) == 1:
                    print('Plane %i flies route %i at time slot %i.' % (p, r, t))

