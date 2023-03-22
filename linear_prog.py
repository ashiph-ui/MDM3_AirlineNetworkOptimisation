#%%
import pandas as pd
import numpy as np
import cvxpy as cp
from make_network import makeNet
from make_network import get_from_and_to
import gdown

# import csv
data = pd.read_csv('MDM3_AirlineNetworkOptimisation\edge_list_final.csv', sep=',')
# getting the network
G = makeNet(data)

# # getting the from and to nodes using the edges attribute
from_to = get_from_and_to(data)

# get all flight times from the data
raw_flight_times = data['flight_time']
flight_times = data['flight_time'].sort_values()
flight_times = flight_times.unique()

A = pd.DataFrame(0, index=from_to, columns=flight_times)

def fill_matrix(A, raw_flight_times, from_to):
    for count, value in enumerate(raw_flight_times):
        A.iloc[count, A.columns.get_loc(value)] = 1
    return A
        
A = fill_matrix(A, raw_flight_times, from_to)
print(A)
