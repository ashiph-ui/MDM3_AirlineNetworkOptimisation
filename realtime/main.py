from simulatedannealing import SimulatedAnnealing
from flightschedules import FlightSchedules
from flightschedule import FlightSchedule
from flights import Flights
import random

# Create a list of flights
flights = Flights()

# Create a list of flight schedules
N = 2
flight_schedules = FlightSchedules(flights, N)

# Create a simulated annealing object
temperature = 100
cooling_rate = 0.01
iterations = 100
simulated_annealing = SimulatedAnnealing(flight_schedules, temperature, cooling_rate, iterations)

# Run the simulated annealing algorithm
best_schedule, best_cost = simulated_annealing.run()

# Display the best schedule
print("Best schedule:")
print(f"Total cost: {best_cost}")
best_schedule.display_scheduled_flights()

# Display the initial schedule
print("Initial schedule:")
print(f"Total cost: {flight_schedules.get_total_cost()}")
flight_schedules.display_scheduled_flights()