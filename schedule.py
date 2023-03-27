# Scheduling Flights with Airline Network Optimisation
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from ortools.sat.python import cp_model

num_of_planes = 5
num_of_routes = 10
time_slots = 10

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

print(x[0,0,0])
# Create the objective function
model.Minimize(sum(x[p, r, t] for p in all_planes for r in all_routes for t in all_time_slots)) 
# minimize the sum of all x[p, r, t] for all planes p, all routes r and all time slots t

# Create the constraints
for p in all_planes:    # for each plane p in all_planes
    for t in all_time_slots:    # for each time slot t in all_time_slots
        model.Add(sum(x[p, r, t] for r in all_routes) <= 1) # sum of all x[p, r, t] for all routes r must be less than or equal to 1

for r in all_routes:
    model.Add(sum(x[p, r, t] for p in all_planes for t in all_time_slots) == 1)

for p in all_planes:
    for r in all_routes:
        model.Add(sum(x[p, r, t] for t in all_time_slots) <= 1)

for p in all_planes: 
    for t in all_time_slots: 
        model.Add(sum(x[p, r, t] for r in all_routes) <= 1)

for r in all_routes:
    for t in all_time_slots:
        model.Add(sum(x[p, r, t] for p in all_planes) <= 1)

# constraint for max number of routes per plane
for p in all_planes:
    model.Add(sum(x[p, r, t] for r in all_routes for t in all_time_slots) <= 2)

# constraint for flight time per plane
for p in all_planes:
    model.Add(sum(x[p, r, t] for r in all_routes for t in all_time_slots) <= 2)



# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print the solution
if status == cp_model.OPTIMAL:
    for p in all_planes:
        for r in all_routes:
            for t in all_time_slots:
                if solver.Value(x[p, r, t]) == 1:
                    print('Plane %i flies route %i at time slot %i.' % (p, r, t))


