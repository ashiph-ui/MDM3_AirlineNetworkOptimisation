from Flights import Flights        
from datetime import datetime
import pandas as pd
import airportsdata
import requests

flightstack_key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI0IiwianRpIjoiNThlNzY3NTNkZjQ4Y2I5MzViOGQ3MzQzYzQwMmFmYjNlM2U5M2NmM2NjNGE4MGE4NjNlY2UxMzU5NTM4MTUwOTMyMmI4Nzk5ZTVkODg0MjQiLCJpYXQiOjE2Nzg3MjA1OTEsIm5iZiI6MTY3ODcyMDU5MSwiZXhwIjoxNzEwMzQyOTkxLCJzdWIiOiIyMDQ0OSIsInNjb3BlcyI6W119.QSW0Qh663z_nRnEWK8ocJbVwBq-SW7tlQSxUwRcVdrJYO0UmOQqU_YKaPFXkmJ3m2sHckQ7xKW5Jfw_in9SmoQ"
airports = airportsdata.load('IATA')
# datetime object containing current date and time
now = datetime.now()

# easyjet = Flights(airline="EZY", airport="all")
# easyjet.df.to_csv(now.strftime("%Y-%m-%d_%H-%M-%S") + "_EZY.csv")
df = pd.read_csv("2023-03-13_13-29-44_EZY.csv")

# creating dataset of nodes and edges for network graph
nodes = []
edges = []
item = []
header = []
for flight in df.origin_airport_iata.unique():
    nodes.append(flight)

for flight in df.itertuples():
    edges.append((flight.origin_airport_iata, flight.destination_airport_iata))

# creating network graph
header.append(airports['LGW'].keys())
print(str(header))
import csv
values = []
keys = list(airports['LGW'].keys())
#create dict of data
for airport in nodes:
    

    values.append(list(airports[airport].values()))
    


# open a CSV file for writing
with open('output.csv', mode='w', newline='\n') as file:

    # create a CSV writer object
    writer = csv.writer(file)

    # write the header row
    writer.writerow(keys)

    # write the data row
    for value in values:    
        writer.writerow(value)



# with open("network_set.csv", "w") as f:
#     f.write(f"{item}")

params = {
  'access_key': flightstack_key,
  'airline_iata': 'EZY',
  'iataCode': 'LGW'
}

# api_result = requests.get('https://app.goflightlabs.com/flights', params)

# api_response = api_result.json()
# print(api_response)