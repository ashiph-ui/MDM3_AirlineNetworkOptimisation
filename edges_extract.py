import requests
import json
import csv

def create_edges_list(nodes_list):

    '''This function takes a list of nodes and returns a list of edges
    that connect the nodes. The edges are in the form of tuples, where
    the first element is the source node and the second element is the
    destination node.'''

    # Set up the headers for the API request
    headers = {
        "X-RapidAPI-Key": "YOUR_API_KEY",
        "X-RapidAPI-Host": "aerodatabox.p.rapidapi.com" }

    # Send a request to the API for each airport and store the responses in a list
    responses = []
    for node in nodes_list:
        url = f"https://aerodatabox.p.rapidapi.com/airports/icao/{node}/stats/routes/daily"

        headers = {
            "X-RapidAPI-Key": "791b4d97cemshe431629c33a2f66p124871jsne802b70f9743",
            "X-RapidAPI-Host": "aerodatabox.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers)

        # Append the response JSON data to the list
        responses.append(response.json())

    # Save the list of responses to a JSON file
    with open('aerodatabox_responses.json', 'w') as json_file:
        json.dump(responses, json_file)

def read_json():
    '''This function reads the JSON file created by the create_edges_list function
    and returns a list of edges.'''

    # Read the JSON file
    with open('aerodatabox_responses.json') as json_file:
        data = json.load(json_file)

    # Create a list of edges
    edges = []

    for airport in data[0]['routes']:
        for destination in airport['destination']:
            print(destination['icao'])
            edges.append(destination[0])
    return edges

def write_csv(edges_list):
    '''This function takes a list of edges and writes them to a CSV file.'''

    # Open a CSV file for writing
    with open('edges.csv', mode='w', newline='\n') as file:

        # Create a CSV writer object
        writer = csv.writer(file)

        # Write the header row
        writer.writerow(['Source', 'Target'])

        # Write the data rows
        for edge in edges_list:
            writer.writerow(edge)

a = read_json()
print(a[0:10])