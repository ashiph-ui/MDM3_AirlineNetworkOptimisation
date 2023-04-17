import copy
import random
import math


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
        best_cost = self.initial_schedule.get_total_cost()

        for i in range(self.iterations):
            temperature = self.temperature * (1 - self.cooling_rate) ** i

            # Generate a new candidate schedule
            candidate_schedule = copy.deepcopy(current_schedule)
            candidate_schedule.randomize_schedules()
            # candidate_schedule = Schedule(candidate_flights.flights)

            # Calculate the cost of the new schedule
            current_cost = current_schedule.get_total_cost()
            candidate_cost = candidate_schedule.get_total_cost()

            # Decide whether to accept the new schedule based on acceptance probability
            if self.acceptance_probability(current_cost, candidate_cost, temperature) > random.random():
                current_schedule = candidate_schedule

            # Update the best schedule if the current schedule is better
            if current_schedule.get_total_cost() < best_schedule.get_total_cost():
                best_schedule = current_schedule
                best_cost = current_schedule.get_total_cost()
                print(f"Best cost: {best_cost}\n")

        return best_schedule, best_cost