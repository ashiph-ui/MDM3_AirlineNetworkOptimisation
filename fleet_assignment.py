from ortools.linear_solver import pywraplp
from routing_optimisation import *
from network_flow_opt import *
# Define the data
n_planes = 90
plane_capacity = 189


# Create the OR tools solver
solver = pywraplp.Solver('AirlineFleetAssignment', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

# Define the decision variables
x = {} # x[(i, j, k)] is a binary variable indicating whether plane k is assigned to fly from airport i to airport j
for i in range(len(new_df)):
    for j in range(len(new_df)):
        for k in range(n_planes):
            x[(i, j, k)] = solver.BoolVar('x[%i,%i,%i]' % (i, j, k))

# Define the objective function
objective = solver.Objective()
for i in range(len(new_df)):
    for j in range(len(new_df)):
        for k in range(n_planes):

            objective.SetCoefficient(x[(i, j, k)], distance_opt[i][j])
objective.SetMinimization()

# Add the constraints
# Constraint 1: Each route must be flown by exactly one plane
for i in range(len(new_df)):
    for j in range(len(new_df)):
        solver.Add(solver.Sum([x[(i, j, k)] for k in range(n_planes)]) == 1)

# Constraint 2: Each plane can only fly one route at a time
for k in range(n_planes):
    solver.Add(solver.Sum([x[(i, j, k)] for i in range(len(new_df)) for j in range(len(new_df))]) <= 1)

# Constraint 3: The number of passengers on each plane cannot exceed the plane's capacity
for k in range(n_planes):
    for i in range(len(new_df)):
        for j in range(len(new_df)):
            solver.Add(solver.Sum([x[(i, j, k)]]*plane_capacity) <= new_df.iloc[i]['passenger_outbound'] + new_df.iloc[j]['passenger_inbound'])

# Constraint: a plane has to leave from the airport it landed at
for j in range(len(new_df)):
    for k in range(n_planes):
        # Find all incoming flights to airport j
        incoming_flights = [x[(i, j, k)] for i in range(len(new_df)) if x[(i, j, k)].solution_value() > 0]
        # Find all outgoing flights from airport j
        outgoing_flights = [x[(j, i, k)] for i in range(len(new_df )) if x[(j, i, k)].solution_value() > 0]
        # If there are any incoming flights, the plane must leave from airport j
        if len(incoming_flights) > 0:
            for flight in outgoing_flights:
                flight.SetCoefficient(1, incoming_flights)


# Solve the model
solver.Solve()

# Print the results
for i in range(len(new_df)):
    for j in range(len(new_df)):
        for k in range(n_planes):
            if x[(i, j, k)].solution_value() > 0:
                print('Plane %i is assigned to fly from airport %i to airport %i' % (k, i, j))
