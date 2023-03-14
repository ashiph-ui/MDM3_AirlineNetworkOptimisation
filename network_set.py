from Flights import Flights        
from datetime import datetime
import pandas as pd
import airportsdata
import requests
import csv


airports_icao = airportsdata.load('ICAO')
airports_iata = airportsdata.load('IATA')
# datetime object containing current date and time
now = datetime.now()

# easyjet = Flights(airline="EZY", airport="all")
# easyjet.df.to_csv(now.strftime("%Y-%m-%d_%H-%M-%S") + "_EZY.csv")
df = pd.read_csv("2023-03-13_13-29-44_EZY.csv")

airport_df = pd.read_csv("output.csv")
airport_missing_list = ["EGPE EGPD EGAA EGAC LSZH LCLK EDDM EDNY LYBE LEST EGNM LEAM LEMI LEBB LFBZ LFMT LFML LFTH LFLS LFRB LFOB EGSS EGHL EGHI LGSR LGIR LGRP LIME LIPX LIRP LIPE LIBD LIBR LICC GMAD LPPS ESSA EFRO LTBS LTAI OJAQ HESH HEGN HEMA"]
airport_missing_list = airport_missing_list[0].split(" ")


values = []
for airport in airport_missing_list:
    values.append(list(airports_icao[airport].values()))

# creating dataset of nodes and edges for network graph
nodes = []
edges = []
item = []
header = []
for flight in df.origin_airport_iata.unique():
    nodes.append(flight)

for flight in df.itertuples():
    edges.append((flight.origin_airport_iata, flight.destination_airport_iata))

values_2 = []
keys = list(airports_icao['EGKK'].keys())
#create dict of data
for airport in nodes:
    values.append(list(airports_iata[airport].values()))


# open a CSV file for writing
with open('output.csv', mode='w', newline='\n') as file:

    # create a CSV writer object
    writer = csv.writer(file)

    # write the header row
    writer.writerow(keys)

    for value_2 in values_2:
        writer.writerow(value_2)

    # write the data row
    for value in values:    
        writer.writerow(value)


# params = {
#   'access_key': flightstack_key,
#   'airline_iata': 'EZY',
#   'iataCode': 'LGW'
# }

# api_result = requests.get('https://app.goflightlabs.com/flights', params)

# api_response = api_result.json()
# print(api_response)