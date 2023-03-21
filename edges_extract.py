import requests
import json
import csv
import pandas as pd
import airportsdata
import os
import glob

airports_icao = airportsdata.load('ICAO')
airports_iata = airportsdata.load('IATA')
# dir = r'C:\Users\ndvll\Desktop'
# node_csv = 'node_list.csv'
# df = pd.read_csv(node_csv, sep=",", header = 0)
# airport_list = df['icao'].tolist()


# missing_airport_list = r"C:\Users\ndvll\Downloads\missing_airport_list.txt"
# with open(missing_airport_list, 'r') as f:
#     missing_airport_list = f.read().split(",")
# print(len(missing_airport_list))
def create_edges_list(node):

    '''This function takes a list of nodes and returns a list of edges
    that connect the nodes. The edges are in the form of tuples, where
    the first element is the source node and the second element is the
    destination node.'''

    # Set up the headers for the API request
    headers = {
        "X-RapidAPI-Key": "791b4d97cemshe431629c33a2f66p124871jsne802b70f9743",
        "X-RapidAPI-Host": "aerodatabox.p.rapidapi.com" }

    # Send a request to the API for each airport and store the responses in a list
    responses = []

    url = f"https://aerodatabox.p.rapidapi.com/airports/icao/{node}/stats/routes/daily"

    headers = {
        "X-RapidAPI-Key": "791b4d97cemshe431629c33a2f66p124871jsne802b70f9743",
        "X-RapidAPI-Host": "aerodatabox.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers)

    # Append the response JSON data to the list
    responses.append(response.json())


    # Save the list of responses to a JSON file
    with open(os.path.join(dir,'aerodatabox_responses_'+str(i)+'.json'), 'w') as json_file:
        json.dump(responses, json_file)

def read_json(path):
    '''This function reads the JSON file created by the create_edges_list function
    and returns a list of edges.'''

    # Read the JSON file
    with open(path, mode="r") as json_file:
        data = json.load(json_file)

    # Create a list of edges
    edges = []
    daily_flights = []
    header = list(data[0]['routes'][0]['destination'].keys())
    header.append('daily_flights')
    for airport in data[0]['routes']:
        for airline in airport['operators']:
                if airline['name'] == 'easyJet':
                    edges.append(list(airport['destination'].values()))
                    daily_flights.append(airport['averageDailyFlights'])
    
    return edges, header, daily_flights


def write_csv(path, edges_list, header_row, daily_flights):
    '''This function takes a list of edges and writes them to a CSV file.'''

    # Open a CSV file for writing
    with open(path, mode='w', newline='\n') as file:

        # Create a CSV writer object
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        # Write the header row
        writer.writerow(header_row)

        for i in range(len(daily_flights)):
            edges_list[i].append(daily_flights[i])
        # Write the data rows
        for edge in edges_list:
            writer.writerow(edge)


def concatenat_csv_files(dir_path):

    all_files = glob.glob(os.path.join(dir_path , "*.csv"))

    li = []

    for filename in all_files:
        df = pd.read_csv(filename, index_col=None, header=0, encoding='cp1252', on_bad_lines='skip')
        df.insert(0, 'origin_airport', filename[filename.find('s_')+2:filename.find('.')])
        li.append(df)

    frame = pd.concat(li, axis=0, ignore_index=True)
    return frame

def fixing_csv(dir_path):
    

    for index, row in df.iterrows():
        row_number = index+1
        if pd.isna(row['destination_airport_icao']):
            row['destination_airport_icao']=airports_iata[row['destination_airport_iata']]['icao']
    
    
def filling_missing_airports(row):
    icao = airports_iata[row['destination_airport_iata']]['icao'] if pd.isna(row['destination_airport_icao']) else row['destination_airport_icao']
    return icao
df = pd.read_csv("MDM3_AirlineNetworkOptimisation/almost_there.csv", delimiter=';',index_col=None, header=0, encoding='cp1252')
df = df.apply(lambda row: row.fillna(value = filling_missing_airports(row)), axis=1)

# function to extract airport information from dictionary
def extract_origin_airport_info(row):
    origin_dict = airports_icao[row['origin_airport']]
    return pd.Series([origin_dict['icao'], origin_dict['iata'], origin_dict['name'], origin_dict['city'], origin_dict['subd'], origin_dict['country'], origin_dict['lat'], origin_dict['lon'], origin_dict['tz'], origin_dict['lid']])

# split dictionary string into column, drop the original column and save to csv
df['destination_airport_location'] = df['destination_airport_location'].apply(lambda x: json.loads(x))
df = df.join(df['destination_airport_location'].apply(lambda x: pd.Series(x)))
print(df.head())
# drop the original column of dictionaries
df = df.drop(columns=['destination_airport_location'])

# apply function to dataframe
# df = df.merge(df.apply(extract_origin_airport_info, axis=1), left_index=True, right_index=True)
# df.to_csv('modified_full_edge_list_3.csv', index=False, header = True, sep=';')
# path_to_dir = os.path.join(dir)
# all_files = concatenat_csv_files(path_to_dir)



# with open('full_edge_list.csv', 'w', newline='') as file:
#     all_files.to_csv(file, index=False, header = True)
# for i in airport_list:
# path_to_files = os.path.join(dir,'aerodatabox_responses_'+str(i))
#     try:    
#         #create_edges_list(i)
#         node_json = read_json(path+'.json')
#         write_csv(path+ '.csv', node_json[0], node_json[1], node_json[2])
#     except (TypeError, FileNotFoundError):
#         pass