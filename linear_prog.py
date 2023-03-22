import pandas as pd
import numpy as np
import cvxpy as cp
from make_network import makeNet
from make_network import get_from_and_to

# import csv
data = pd.read_csv('MDM3_AirlineNetworkOptimisation\edge_list_final.csv', sep=',')

# # getting the network

G = makeNet(data)

# # getting the from and to nodes using the edges attribute
from_to = get_from_and_to(G)
t = np.linspace(1, 10, 10)
print(t)
A = pd.DataFrame(0, index=from_to, columns=t)
print(A)