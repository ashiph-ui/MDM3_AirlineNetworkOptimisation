from api import FlightRadar24API
from flight import Flight as FlightRadar24Flight
from openap import Emission, FuelFlow, prop
import numpy as np
import datetime
import random
import math
import copy



class Flights(FlightRadar24API):
    def __init__(self, airline="EZY", airport="LGW", schedule_type="realtime"):
        super().__init__()
        self.airline = airline
        self.airport = airport
        self.airline_flights = self.get_flights(airline=self.airline)
        self.airport_flights = [f for f in self.airline_flights if f.origin_airport_iata == self.airport or f.destination_airport_iata == self.airport]
        self.flights = self.get_real_time_data()

        # Keep only the flights that don't have "None" in self.flights.time_details["scheduled"].values()
        if schedule_type == "scheduled":
            self.flights = [flight for flight in self.flights if None not in flight.time_details["scheduled"].values()]
        elif schedule_type == "realtime":
            self.flights = [flight for flight in self.flights if flight.time_details["estimated"]["arrival"] is not None]

        self.trails = [flight.trail for flight in self.flights]
        self.lats = [[point["lat"] for point in trail] for trail in self.trails]
        self.lons = [[point["lng"] for point in trail] for trail in self.trails]
        self.alts = [[point["alt"] for point in trail] for trail in self.trails]
        self.spds = [[point["spd"] for point in trail] for trail in self.trails]

        self.aircraft_codes = [flight.aircraft_code.upper() for flight in self.flights]

        self.co2_emissions = [self.calculate_co2_emissions(flight) for flight in self.flights]


    def get_real_time_data(self):
        details = [self.get_flight_details(flight.id) for flight in self.airport_flights]
        for flight, detail in zip(self.airport_flights, details):
            try:
                flight.set_flight_details(detail)
            except:
                pass

        realtime_data = [flight for flight in self.airport_flights if len(flight.__dict__) > 19]
        return realtime_data

    
    def calculate_co2_emissions(self, flight):
        """
        Calculates the CO2 emissions of a flight in kg.
        """
        trail = flight.trail
        altitudes = np.array([point["alt"] for point in trail])
        # Get only the altitudes that are greater than or equal to 100 ft
        altitudes_ = altitudes[altitudes >= 100]
        speeds = np.array([point["spd"] for point in trail])[altitudes >= 100]
        latitudes = np.array([point["lat"] for point in trail])[altitudes >= 100]
        longitudes = np.array([point["lng"] for point in trail])[altitudes >= 100]

        aircraft_code = flight.aircraft_code
        aircraft = prop.aircraft(ac=aircraft_code, use_synonym=True)
        fuelflow = FuelFlow(ac=aircraft_code, use_synonym=True)
        emission = Emission(ac=aircraft_code, use_synonym=True)
        speeds_, altitudes_ = np.meshgrid(speeds, altitudes_)
        mass = aircraft["limits"]["MTOW"] * 0.85

        ff = fuelflow.enroute(mass=mass, tas=speeds_, alt=altitudes_, path_angle=0)

        co2 = emission.co2(ff)

        return co2


class SimulatedAnnealing:
    def __init__(self, initial_schedule, temperature, cooling_rate, iterations):
        self.initial_schedule = initial_schedule
        self.temperature = temperature
        self.cooling_rate = cooling_rate
        self.iterations = iterations

    def acceptance_probability(self, cost, new_cost, temperature):
        # Calculate acceptance probability based on current temperature
        if new_cost < cost:
            return 1.0
        return math.exp(-(new_cost - cost) / temperature)

    def run(self):
        current_schedule = self.initial_schedule
        best_schedule = self.initial_schedule
        best_cost = self.initial_schedule.cost()

        for i in range(self.iterations):
            temperature = self.temperature * (1 - self.cooling_rate) ** i

            # Generate a new candidate schedule
            candidate_schedule = copy.deepcopy(current_schedule)
            random.shuffle(candidate_schedule.schedule)
            # candidate_schedule = Schedule(candidate_flights.flights)

            # Calculate the cost of the new schedule
            current_cost = current_schedule.cost()
            candidate_cost = candidate_schedule.cost()

            # Decide whether to accept the new schedule based on acceptance probability
            if self.acceptance_probability(current_cost, candidate_cost, temperature) > random.random():
                current_schedule = candidate_schedule

            # Update the best schedule if the current schedule is better
            if current_schedule.cost() < best_schedule.cost():
                best_schedule = current_schedule
                best_cost = current_schedule.cost()

        return best_schedule, best_cost