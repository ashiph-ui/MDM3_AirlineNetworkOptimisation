import pulp

# Create a new optimization problem
prob = pulp.LpProblem("MILP Problem", pulp.LpMinimize)

# Define decision variables
x = pulp.LpVariable("x", lowBound=0, cat="Integer")
y = pulp.LpVariable("y", lowBound=0, cat="Integer")

# Define objective function
prob += 2*x + 3*y

# Define constraints
prob += 4*x + 3*y >= 20
prob += 2*x + 5*y >= 15

# Solve the problem
status = prob.solve()

# Print the solution
print("Status:", pulp.LpStatus[status])
print("Optimal value:", pulp.value(prob.objective))
print("x =", pulp.value(x))
print("y =", pulp)









