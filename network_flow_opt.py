from ortools.graph.python import min_cost_flow
import pandas as pd
import numpy as np

# Load nodes and edges from csv file
airports_df = pd.read_csv('node_eurocontrol_w_bases.csv', encoding='cp1252', index_col='index')
flights_df = pd.read_csv('edge_eurocontrol_minute.csv', encoding='cp1252')
# append number of nodes and flights (arcs)
num_nodes = len(airports_df)
num_arcs = len(flights_df)

def passenger_flow(airport_df, flight_df):
    '''Build a passenger flow at each airport in a dataframe and addit as a column in the dataframe.
    Moreover, there should be a column for departing passengers and a column for arriving passengers.
    It is computed using the fact there are 186 passengers on each flight.
    '''
    # get number of inbound flights 
    df = airport_df.copy()
    inbound = flight_df['origin_airport_icao'].value_counts().to_list()
    # get number of outbound flights
    outbound = flight_df['destination_airport_icao'].value_counts().to_list()
    # get the list of airports that are not in the list of inbound flights
    pass_inbound = inbound * 186
    # Compute the number of arriving passengers 
    pass_outbound = outbound * 186
    # Compute the total number of passengers  
    pass_total = pass_inbound + pass_outbound
    
    return inbound, outbound, pass_inbound, pass_outbound, pass_total

new_airport_df = passenger_flow(airports_df, flights_df)

# call the min cost flow solver 
smcf = min_cost_flow.SimpleMinCostFlow()

src = []
dst = []
capacity = np.ones(num_arcs) *180
cost = []
supplies = np.zeros(num_nodes)
origin_airport_icao = new_airport_df['icao'].to_list()
print(origin_airport_icao)
# inverse the sign of the supply for the origin airports
supplies[origin_airport_icao] = -new_airport_df['departing_passengers'].to_list()
destination_airport_icao = new_airport_df['icao'].to_list()
supplies[destination_airport_icao] = new_airport_df['arriving_passengers'].to_list()
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