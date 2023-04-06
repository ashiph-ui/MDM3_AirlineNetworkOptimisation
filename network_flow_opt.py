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
    df['num_outbound_flights'] = flight_df['origin_airport_icao'].value_counts().to_list()
    # get number of inbound flights
    df['num_inbound_flights'] = flight_df['destination_airport_icao'].value_counts().to_list()
    # Compute the number of departing passengers 
    df['passenger_outbound'] = df['num_outbound_flights'].apply(lambda x: x*186)
    # Compute the number of arriving passengers 
    df['passenger_inbound'] = df['num_inbound_flights'].apply(lambda x: x*186)
    # Compute the total number of passengers  
    df['pass_total'] = df['passenger_inbound'] + df['passenger_outbound']
    df['supplies_pass'] = df['passenger_inbound'] - df['passenger_outbound'] 
   
    return df

new_df = passenger_flow(airports_df, flights_df)

# call the min cost flow solver 
smcf = min_cost_flow.SimpleMinCostFlow()

src = []
dst = []
capacity = np.ones(num_arcs, dtype=int) * 5000
cost = []
supplies = np.zeros(num_nodes)
# get indices of origin airports
airports = list(range(0, num_nodes))
supplies[airports]= new_df['supplies_pass'].to_list()
supplies = [int(i) for i in supplies]

for i in range(num_arcs):
    # Add an arc for the flight i
    src.append(airports_df[airports_df['icao']==flights_df.iloc[i]['origin_airport_icao']].index.values[0])
    dst.append(airports_df[airports_df['icao']==flights_df.iloc[i]['destination_airport_icao']].index.values[0])
    cost.append(int(flights_df.iloc[i]['co2']))
   

for i in range(num_arcs):
    smcf.add_arc_with_capacity_and_unit_cost(src[i], dst[i],
                                             capacity[i], cost[i])
# Add node supplies.
for i in range(len(supplies)):
    smcf.set_node_supply(i, supplies[i])

# Define any additional constraints, such as minimum or maximum delay times
status = smcf.solve()

if status == smcf.OPTIMAL:
    print('Total cost = ', smcf.optimal_cost())
    print()
    print(smcf.num_arcs())
    for arc in range(smcf.num_arcs()):
        # Can ignore arcs leading out of source or into sink.


        print('Worker %d assigned to task %d.  Cost = %d' %
                (smcf.tail(arc), smcf.head(arc), smcf.unit_cost(arc)))
else:
    print('There was an issue with the min cost flow input.')
    print(f'Status: {status}')