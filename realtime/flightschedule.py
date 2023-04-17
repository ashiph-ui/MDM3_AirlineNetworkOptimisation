from api import FlightRadar24API
import datetime
import random
import numpy as np
import copy
from openap import Emission, FuelFlow, prop

class FlightSchedule():
    def __init__(self, flight):
        self.fr_api = FlightRadar24API()
        self.flight = copy.deepcopy(flight)
        self.aircraft_history = self.flight.aircraft_history
        self.aircraft_details = [self.fr_api.get_flight_details(history["identification"]["id"]) for history in self.aircraft_history]
        self.errors_fixed = 0
        for i in range(len(self.aircraft_details)):
            if type(self.aircraft_details[i]) == bytes:
                print(f"Error: Could not get flight details for flight id {self.aircraft_history[i]['identification']['id']}")
                print("Attempting to get flight details again...")
                self.fr_api = FlightRadar24API()
                self.aircraft_details[i] = self.fr_api.get_flight_details(self.aircraft_history[i]['identification']['id'])
                if type(self.aircraft_details[i]) == bytes:
                    print("Error: Could not get flight details")
                    print("Skipping flight...")
                    self.aircraft_details[i] = {}
                    return
                else:
                    print("Successfully got flight details")
                    self.errors_fixed += 1

        self.aircraft_times = [detail["time"] for detail in self.aircraft_details][::-1]
        self.aircraft_airports = [detail["airport"] for detail in self.aircraft_details][::-1]
        self.aircraft_codes = [detail["aircraft"]["model"]["code"] for detail in self.aircraft_details][::-1]
        self.departure_airports = [airport["origin"] for airport in self.aircraft_airports][::-1]
        self.arrival_airports = [airport["destination"] for airport in self.aircraft_airports][::-1]
        self.scheduled_departure_times = [time["scheduled"]["departure"] for time in self.aircraft_times][::-1]
        self.scheduled_arrival_times = [time["scheduled"]["arrival"] for time in self.aircraft_times][::-1]
        self.real_departure_times = [time["real"]["departure"] for time in self.aircraft_times][::-1]
        self.real_arrival_times = [time["real"]["arrival"] for time in self.aircraft_times][::-1]
        self.trails = [detail["trail"] for detail in self.aircraft_details][::-1]

        self.schedule = self.get_schedule()
        self.scheduled = True
        for i in range(1,5):
            if f"flight{i}" not in self.schedule:
                self.scheduled = False
                break
            else:
                self.flight1 = copy.deepcopy(self.schedule["flight1"][0])
                self.flight2 = copy.deepcopy(self.schedule["flight2"][0])
                self.flight3 = copy.deepcopy(self.schedule["flight3"][0])
                self.flight4 = copy.deepcopy(self.schedule["flight4"][0])
                

    def get_schedule(self, actual=False):
        departure_times = (self.real_departure_times, self.scheduled_departure_times)
        arrival_times = (self.real_arrival_times, self.scheduled_arrival_times)
        schedule = {}
        c = 4
        for departure_airport, arrival_airport, departure_time_scheduled, departure_time_real, arrival_time_scheduled, arrival_time_real in zip(self.departure_airports,self.arrival_airports, departure_times[0], departure_times[1], arrival_times[0], arrival_times[1]):
            if None in (departure_time_scheduled, departure_time_real, arrival_time_scheduled, arrival_time_real):
                c+=1
                break
            departure_time_scheduled = datetime.datetime.fromtimestamp(departure_time_scheduled)
            arrival_time_scheduled = datetime.datetime.fromtimestamp(arrival_time_scheduled)
            departure_time_real = datetime.datetime.fromtimestamp(departure_time_real)
            arrival_time_real = datetime.datetime.fromtimestamp(arrival_time_real)
            schedule[f"flight{c}"] = {
                "aircraft_code" : self.aircraft_codes[c-1],
                "trail": copy.deepcopy(self.trails[c-1]),
                "departure_airport": departure_airport["code"]["iata"], 
                "arrival_airport": arrival_airport["code"]["iata"], 
                "departure_time": departure_time_scheduled, 
                "arrival_time": arrival_time_scheduled,
                "duration": (arrival_time_scheduled - departure_time_scheduled).total_seconds() // 60, # convert to minutes
                "departure_time_real": departure_time_real,
                "arrival_time_real": arrival_time_real,
                "duration_real": (arrival_time_real - departure_time_real).total_seconds() // 60}, # convert to minutes 
            c -= 1

        return schedule
    
    
    def randomize_schedule(self):
        # Randomly swap the departure and arrival airports of each flight
        # E.g. if flight1 is scheduled to depart from LHR at 2pm and arrive at JFK at 4pm and has a duration of 2 hours
        # and flight2 is scheduled to depart from JFK at 6pm and arrive at LHR at 9pm and has a duration of 3 hours
        # then the new schedule could be:
        #   flight1: JFK -> LHR | 6pm -> 9pm | duration: 3 hours
        #   flight2: LHR -> JFK | 2pm -> 4pm | duration: 2 hours
        for flight in self.schedule:
            if random.randint(0,1) == 1:
                self.swap_flights(flight1=flight, flight2="flight4")
            else:
                self.swap_flights(flight1=flight, flight2="flight3")



    def swap_flights(self, flight1, flight2):
        flight1_departure_airport = self.schedule[flight1][0]["departure_airport"]
        flight1_arrival_airport = self.schedule[flight1][0]["arrival_airport"]
        flight1_duration = self.schedule[flight1][0]["duration"]
        flight1_real_duration = self.schedule[flight1][0]["duration_real"]

        flight2_departure_airport = self.schedule[flight2][0]["departure_airport"]
        flight2_arrival_airport = self.schedule[flight2][0]["arrival_airport"]
        flight2_duration = self.schedule[flight2][0]["duration"]
        flight2_real_duration = self.schedule[flight2][0]["duration_real"]

        self.schedule[flight1][0]["trail"] = copy.deepcopy(self.schedule[flight2][0]["trail"])
        self.schedule[flight1][0]["departure_airport"] = flight2_departure_airport
        self.schedule[flight1][0]["arrival_airport"] = flight2_arrival_airport
        self.schedule[flight1][0]["duration"] = flight2_duration
        self.schedule[flight1][0]["arrival_time"] = self.schedule[flight1][0]["departure_time"] + datetime.timedelta(minutes=flight2_duration)
        self.schedule[flight1][0]["duration_real"] = flight2_real_duration
        self.schedule[flight1][0]["arrival_time_real"] = self.schedule[flight1][0]["departure_time_real"] + datetime.timedelta(minutes=flight2_real_duration)

        self.schedule[flight2][0]["trail"] = copy.deepcopy(self.schedule[flight1][0]["trail"])
        self.schedule[flight2][0]["departure_airport"] = flight1_departure_airport
        self.schedule[flight2][0]["arrival_airport"] = flight1_arrival_airport
        self.schedule[flight2][0]["duration"] = flight1_duration
        self.schedule[flight2][0]["arrival_time"] = self.schedule[flight2][0]["departure_time"] + datetime.timedelta(minutes=flight1_duration)
        self.schedule[flight2][0]["duration_real"] = flight1_real_duration
        self.schedule[flight2][0]["arrival_time_real"] = self.schedule[flight2][0]["departure_time_real"] + datetime.timedelta(minutes=flight1_real_duration)


    def get_cost(self):
        # Get the cost of the flight schedule
        # The cost is the sum of the absolute differences between the scheduled and actual departure and arrival times
        # The cost is also the sum of the absolute differences between the scheduled and actual durations
        cost = 0
        for flight in self.schedule:
            scheduled_duration = self.schedule[flight][0]["duration"]
            actual_duration = self.schedule[flight][0]["duration_real"]
            co2 = self.calculate_co2_emissions(self.schedule[flight][0]).sum()
            cost += abs(scheduled_duration - actual_duration) + co2
        return cost

    def display_schedule(self):
        for flight, time in self.schedule.items():
            print(f"{flight}: {time[0]['departure_airport']} -> {time[0]['arrival_airport']} | {time[0]['departure_time']} -> {time[0]['arrival_time']} | duration: {time[0]['duration']} minutes")

    def calculate_co2_emissions(self, flight):
        """
        Calculates the CO2 emissions of a flight in kg.
        """
        trail = flight["trail"]
        altitudes = np.array([point["alt"] for point in trail])
        # Get only the altitudes that are greater than or equal to 100 ft
        altitudes_ = altitudes[altitudes >= 100]
        speeds = np.array([point["spd"] for point in trail])[altitudes >= 100]

        aircraft_code = flight["aircraft_code"]
        aircraft = prop.aircraft(ac=aircraft_code, use_synonym=True)
        fuelflow = FuelFlow(ac=aircraft_code, use_synonym=True)
        emission = Emission(ac=aircraft_code, use_synonym=True)
        mass = aircraft["limits"]["MTOW"] * 0.85

        ff = fuelflow.enroute(mass=mass, tas=speeds, alt=altitudes_, path_angle=0)

        co2 = emission.co2(ff)

        return co2