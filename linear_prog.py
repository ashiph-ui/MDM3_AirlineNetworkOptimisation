#%%
import pandas as pd
import numpy as np
from make_network import makeNet
from make_network import get_from_and_to
import gdown
import cvxopt as opt  
import cvxpy as cp
import networkx as nx

# import csv
data = pd.read_csv('edge_list_final.csv', sep=',')
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

# plot the matrix
import seaborn as  sns
import matplotlib.pyplot as plt
plt.figure(figsize=(20,20))
xlabel = A.columns
ylabel = A.index
sns.heatmap(A, cmap='Blues')
plt.show()

# function to get the number of flights for each flight time
def get_number_of_flights(A):
    number_of_flights = []
    for i in range(len(A.columns)):
        number_of_flights.append(A.iloc[:,i].sum())
    return number_of_flights

number_of_flights = get_number_of_flights(A)

# plot the number of flights for each flight time
plt.figure(figsize=(20,10))
plt.plot(number_of_flights, 'x')
plt.xticks(range(len(number_of_flights)), A.columns, rotation='vertical')
plt.xlabel('Flight time')
plt.ylabel('Number of flights')
plt.title('Number of flights for each flight time')
plt.show()

# create a dictionary with the flight time as key and the number of flights as value
flight_time_dict = dict(zip(A.columns, number_of_flights))


##########

# make new df but all entries are zero
df = pd.DataFrame(0, index=from_to, columns=flight_times)


# plot the matrix
import seaborn as  sns
import matplotlib.pyplot as plt
plt.figure(figsize=(20,20))
xlabel = df.columns
ylabel = df.index
sns.heatmap(df, cmap='Blues')
plt.show()

# total number of flights
total_number_of_flights = len(df.index)
print(total_number_of_flights)

