from flights import Flights
from flightschedule import FlightSchedule
import random
import copy


class FlightSchedules():
    # Class to hold all the flight schedules of all the planes
    # each plane has 4 flights, each flight has a departure and arrival airport, a departure and arrival time, and a duration
    # there will be a method to get the scheduled flights today, this will be used to generate the initial population of the genetic algorithm
    # Then using the FlightSchedule method to randomize the schedule, the genetic algorithm will be able to generate new schedules and evaluate their cost
    def __init__(self, flights, N=None):
        self.flights = flights
        self.N = N
        self.errors_fixed = 0
        self.flight_schedules = {}
        self.get_flight_schedules()
        self.fix_errors()


    def get_flight_schedules(self):
        # Get the flight schedules for N planes, the planes will be randomly selected from the flights list
        # This will be used to generate the initial population of the genetic algorithm
        i = 0
        if self.N is None:
            self.N = len(self.flights.flights)
        for i in range(self.N):
            plane = random.choice(copy.deepcopy(self.flights.flights))
            
            self.flight_schedules[f"plane{i}"] = copy.deepcopy(FlightSchedule(plane))
            if len([detail for detail in self.flight_schedules[f"plane{i}"].aircraft_details if len(detail) == 0]) > 0:
                self.flight_schedules.pop(f"plane{i}")
                print("DELETED!!!")
            else:
                self.errors_fixed += self.flight_schedules[f"plane{i}"].errors_fixed
                print(plane)

    def fix_errors(self):
        # Fix any naming issues in the flight schedules:
        #   e.g. if plane1 was popped from the flight schedules,
        #        the next plane will be plane2, 
        #        so we need to rename the next plane key to plane1.

        # Get the values of the flight schedules
        values = list(self.flight_schedules.values())
        # Create a new dictionary to hold the fixed flight schedules
        fixed_flight_schedules = {}
        # Loop through the keys and values
        for i, val in enumerate(values):
            # Rename the key to the index of the key
            fixed_flight_schedules[f"plane{i}"] = val

        # Set the flight schedules to the fixed flight schedules
        self.flight_schedules = fixed_flight_schedules

        # Print the number of errors fixed
        print(f"Errors fixed: {self.errors_fixed}")




    def display_scheduled_flights(self):
        for plane in self.flight_schedules:
            print(f"{plane}:")
            self.flight_schedules[plane].display_schedule()
            print()

    def randomize_schedules(self):
        for plane in self.flight_schedules:
            self.flight_schedules[plane].randomize_schedule()


    def get_costs(self):
        costs = {}
        for plane in self.flight_schedules:
            costs[plane] = self.flight_schedules[plane].get_cost()
        return costs
    
    def get_total_cost(self):
        total_cost = 0
        for plane in self.flight_schedules:
            total_cost += self.flight_schedules[plane].get_cost()
        return total_cost