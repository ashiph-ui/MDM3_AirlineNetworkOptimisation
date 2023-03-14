import requests

# Set up the aviationstack API credentials
access_key = "37d43409f3df781bc74849e4e1da5413"
import requests

url = "https://aerodatabox.p.rapidapi.com/airports/icao/EDDF/stats/routes/daily"

headers = {
	"X-RapidAPI-Key": "791b4d97cemshe431629c33a2f66p124871jsne802b70f9743",
	"X-RapidAPI-Host": "aerodatabox.p.rapidapi.com"
}
import csv
import requests

# Set up the API parameters
api_key = "791b4d97cemshe431629c33a2f66p124871jsne802b70f9743"
date = "2022-03-12"
airline = "U2"

import csv
import requests

# Set up the API parameters
api_key = "YOUR_API_KEY"
airport_codes = ["EDDF", "LFPG", "EHAM"]  # Example airport codes

# Set up the headers for the API request
headers = {
    "X-RapidAPI-Key": "791b4d97cemshe431629c33a2f66p124871jsne802b70f9743",
    "X-RapidAPI-Host": "aerodatabox.p.rapidapi.com"
}

# Create a list to store all the flight routes
all_flight_routes = []

# Loop over each airport code and retrieve the flight routes for that airport
for airport_code in airport_codes:
    # Make a GET request to the Aerodatabox API
    url = f"https://aerodatabox.p.rapidapi.com/airports/icao/{airport_code}/stats/routes/daily"
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Extract the flight routes from the API response
        flight_routes = response.json()["routes"]
        
        # Append the flight routes to the list of all flight routes
        all_flight_routes.extend(flight_routes)
    else:
        print(f"Error: Could not retrieve flight routes from Aerodatabox API for {airport_code}")

# Save the flight routes data to a CSV file
with open("flight_routes.csv", "w", newline="") as f:
    writer = csv.writer(f)
    
    # Write the header row
    writer.writerow(["Airline", "Flight Number", "Origin Airport", "Destination Airport"])
    
    # Write the data rows
    for flight_route in all_flight_routes:
        airline = flight_route["airline"]
        flight_number = flight_route["flight_number"]
        origin_airport = flight_route["origin_airport"]
        destination_airport = flight_route["destination_airport"]
        writer.writerow([airline, flight_number, origin_airport, destination_airport])
