import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from analysis import *

# import csv
data = pd.read_csv('MDM3_AirlineNetworkOptimisation\modified_full_edge_list_3.csv', sep=';')

# prepare data for networkx
def make_network(data):
    df = data[['origin_airport', 'destination_airport_icao']]
    G = nx.Graph()
    G = nx.from_pandas_edgelist(df, source='origin_airport', target='destination_airport_icao', create_using=nx.DiGraph())
    figure.figsize=(20,20)
    nx.draw_shell(G, with_labels=True, font_weight='bold')
    plt.show()
    return G

G = make_network(data)

print('Degree centrality: ', degree_centrality(G))
print('Closeness centrality: ', closeness_centrality(G))
print('Betweenness centrality: ', betweenness_centrality(G))
print('Eigenvector centrality: ', eigenvector_centrality(G))

# Analysis of the graph: Measure of centrality

deg_centrality = degree_centrality(G)
close_centrality = closeness_centrality(G)
betw_centrality = betweenness_centrality(G)
eigen_centrality = eigenvector_centrality(G)
keys = deg_centrality.keys()

# Plot the centrality measures
def plot_centrality(deg_centrality, close_centrality, betw_centrality, eigen_centrality):
    plt.figure(figsize=(20,10))
    plt.plot(deg_centrality.values(), 'x', label='Degree centrality')
    plt.plot(close_centrality.values(), 'x', label='Closeness centrality')
    plt.plot(betw_centrality.values(), 'x', label='Betweenness centrality')
    plt.plot(eigen_centrality.values(), 'x', label='Eigenvector centrality')
    plt.xticks(range(len(deg_centrality)), deg_centrality.keys(), rotation='vertical')
    plt.legend()
    plt.show()

plot_centrality(deg_centrality, close_centrality, betw_centrality, eigen_centrality)

# highest values for each centrality measure
def highest_centrality(deg_centrality, close_centrality, betw_centrality, eigen_centrality):
    print('Highest degree centrality: ', max(deg_centrality, key=deg_centrality.get))
    print('Highest closeness centrality: ', max(close_centrality, key=close_centrality.get))
    print('Highest betweenness centrality: ', max(betw_centrality, key=betw_centrality.get))
    print('Highest eigenvector centrality: ', max(eigen_centrality, key=eigen_centrality.get))

highest_centrality(deg_centrality, close_centrality, betw_centrality, eigen_centrality)
