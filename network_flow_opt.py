from ortools.graph.python import min_cost_flow
import pandas as pd
import numpy as np

# Load nodes and edges from csv file
airports_df = pd.read_csv('node_eurocontrol_w_bases.csv', encoding='cp1252', index_col='index')
flights_df = pd.read_csv('edge_eurocontrol_minute.csv', encoding='cp1252')
# append number of nodes and flights (arcs)
num_nodes = len(airports_df)
num_arcs = len(flights_df)

# call the min cost flow solver 
smcf = min_cost_flow.SimpleMinCostFlow()

src = []
dst = []
capacity = np.ones(num_arcs) *180
cost = []
supplies = []
for i in range(num_arcs):
    # Add an arc for the flight i
    src.append(airports_df[airports_df['icao']==flights_df.iloc[i]['origin_airport_icao']].index.values[0])
    dst.append(airports_df[airports_df['icao']==flights_df.iloc[i]['destination_airport_icao']].index.values[0])
    cost.append(flights_df.iloc[i]['co2'])
   
# Add constraint and capacity for each arc.
all_arcs = smcf.add_arcs_with_capacity_and_unit_cost(src, dst, capacity, cost)

# Define the flow conservation constraints for each airport
# Add supply for each nodes. (not yet implemented)
smcf.set_nodes_supplies(np.arange(0, len(supplies)), supplies)
# Define any additional constraints, such as minimum or maximum delay times
status = smcf.solve()

# Solve the problem and print the optimal solution
if status != smcf.OPTIMAL:
        print('There was an issue with the min cost flow input.')
        print(f'Status: {status}')
        exit(1)
print(f'Minimum cost: {smcf.optimal_cost()}')