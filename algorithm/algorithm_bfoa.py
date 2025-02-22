from enum import Enum
from algorithm.algorithm import Algorithm
from numpy import linalg as LA

import random
import math
import numpy as np

class Agent:
    def __init__(self, agent_length, lower_bound, upper_bound, f, is_maximizing, random_seed, is_squad_1 = True):
        self.agent_length = agent_length
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.f = f
        self.vector = []
        self.new_vector = []
        self.is_maximizing = is_maximizing
        self.random_seed = random_seed
        self.is_squad_1 = is_squad_1
        self.cavalry_constant = math.pow(2, -1)
        self.commander_constant = math.pow(2, -1)
        self.mid_point = ((self.upper_bound - self.lower_bound) / 2) - self.lower_bound
        self.fitness_value = 0
        self.generate_random_vector()
    
    # Function to generate random vector
    def generate_random_vector(self):
        random.seed(self.random_seed)
        self.vector = [(0 + random.random()) * self.upper_bound - self.lower_bound for i in range(self.agent_length)]
        self.fitness_value = self.f(self.vector)
        # self.fix_out_airplane_movement()
    
    # Fix element that outside of bound
    def fix_out(self):
        for i in range(len(self.vector)):
            if self.vector[i] < self.lower_bound:
                self.vector[i] = self.lower_bound
            elif self.vector[i] > self.upper_bound:
                self.vector[i] = self.upper_bound

    def calculate_fitness(self):
        self.fitness_value = self.f(self.vector)
    
    # Fix element that outside of bound (in airplane movement)
    def fix_out_airplane_movement(self):
        for i in range(len(self.vector)):
            if i == 0: # if first element
                if self.is_squad_1:
                    if self.vector[i] > self.mid_point:
                        self.vector[i] = self.mid_point
                    elif self.vector[i] < self.lower_bound:
                        self.vector[i] = self.lower_bound
                else:
                    if self.vector[i] < self.mid_point:
                        self.vector[i] = self.mid_point
                    elif self.vector[i] > self.upper_bound:
                        self.vector[i] = self.upper_bound
            else: # if 2nd element, 3rd element, etc
                if self.vector[i] > self.upper_bound:
                    self.vector[i] = self.upper_bound
                elif self.vector[i] < self.lower_bound:
                    self.vector[i] = self.lower_bound

    def airplane_movement(self):
        for i in range(len(self.vector)):
            self.vector[i] = self.vector[i] + self.vector[i] * (random.random() - 0.5) * 2.2
        self.fix_out_airplane_movement()
        self.calculate_fitness()
    
    def builder_movement(self, i):
        # i-th iteration
        i = i % 400
        power = -1 - int(i / 50)
        for i in range(len(self.vector)):
            self.vector[i] = self.vector[i] - (random.random() * 2 - 1) * math.pow(1, power)
        self.fix_out()
        self.calculate_fitness()

    def commander_movement(self, enemy_commander_vector):
        for i in range(len(self.vector)):
            self.vector[i] = self.vector[i] + (enemy_commander_vector[i] - self.vector[i]) / LA.norm(enemy_commander_vector[i] - self.vector[i]) * random.random() * self.commander_constant
        self.fix_out()
        self.calculate_fitness()

    def cavalry_movement(self, is_left_cavalry, enemy_commander_vector):
        # get perpendicular vector
        A = np.array(self.vector)
        B = np.array(enemy_commander_vector)

        # Direction vector of the line between A and B
        direction_L = B - A

        # Find a perpendicular direction vector D
        # We can choose D such that it is orthogonal to direction_L
        # For simplicity, set D as a vector with all zeros except one element
        D = np.zeros_like(A)
        D[0] = 1  # Set the first element to 1

        # Ensure D is orthogonal to direction_L by subtracting the projection
        D = D - np.dot(D, direction_L) / np.dot(direction_L, direction_L) * direction_L

        perpendicular_vector = A + B[0] * D

        if is_left_cavalry:
            for i in range(len(self.vector)):
                self.vector[i] = (self.vector[i] - perpendicular_vector[i]) * self.cavalry_constant
        else: # Right cavalry
            for i in range(len(self.vector)):
                self.vector[i] = (self.vector[i] - perpendicular_vector[i]) * self.cavalry_constant
        self.fix_out()
        self.calculate_fitness()

    def special_force_movement(self):
        for i in range(len(self.vector)):
            self.vector[i] = (1 + random.random()) * self.vector[i] * 1.01
        self.fix_out()
        self.calculate_fitness()

class SquadMode(Enum):
    ATTACKING = 1
    DEFENDING = 2

class Squad():
    def __init__(self, mode):
        self.mode = mode
        self.air_forces = []
        self._commander = None
        self._left_cavalry = None
        self._right_cavalry = None
        self._special_force = None
        self._builder = None

    def sort_air_forces(self, is_maximizing):
        self.air_forces.sort(key=lambda agent: agent.fitness_value, reverse=not is_maximizing)

    def assign_squad(self, is_maximizing):
        if self._commander  is None: # if squad is still empty
            self.sort_air_forces(is_maximizing)
            self._commander = self.air_forces[0]
            self._left_cavalry = self.air_forces[1]
            self._right_cavalry = self.air_forces[2]
            self._special_force = self.air_forces[3]
            self._builder = self.air_forces[4]
            return
        # if squad is not empty
        self.air_forces[0] = self._commander
        self.air_forces[1] = self._left_cavalry
        self.air_forces[2] = self._right_cavalry
        self.air_forces[3] = self._special_force
        self.air_forces[4] = self._builder
        self.sort_air_forces(is_maximizing)
        self._commander = self.air_forces[0]
        self._left_cavalry = self.air_forces[1]
        self._right_cavalry = self.air_forces[2]
        self._special_force = self.air_forces[3]
        self._builder = self.air_forces[4]

class BfOA:
    def __init__(self, agent_length, fitness, lower_bound, upper_bound, max_iter, N, is_maximizing=False):
        self.agent_length = agent_length
        self.fitness_function = fitness
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.max_iter = max_iter
        self.is_maximizing = is_maximizing
        self.N = N
        self.n_plane = 8
        self.population = []
        self.phase_1_max_iteration = 1
        self.phase_2_max_iteration = 1
        self.squad1 = Squad(SquadMode.ATTACKING)
        self.squad2 = Squad(SquadMode.DEFENDING)
        self.best_troops = None
        self.best_troops_fitness = 0

    # Function to initialize population (airplane) in phase 1
    def phase_1_initialization(self):
        for i in range(self.n_plane):
            self.squad1.air_forces.append(Agent(
                self.agent_length, # Agent length
                0,
                10,
                self.fitness_function,
                self.is_maximizing,
                100,
                True
            ))
            self.squad2.air_forces.append(Agent(
                self.agent_length,
                0,
                10,
                self.fitness_function,
                self.is_maximizing,
                100,
                False
            ))

    def is_squad_1_better(self):
        return (self.squad1._commander.fitness_value > self.squad2._commander.fitness_value and self.is_maximizing) or (self.squad1._commander.fitness_value < self.squad2._commander.fitness_value and not self.is_maximizing) 

    def is_fitness_value_a_better_than_b(self, a, b):
        if self.is_maximizing:
            return a > b
        return a <= b

    def update_best_troops(self):
        if self.best_troops is None:
            self.best_troops = self.squad1._commander.vector
            self.best_troops_fitness = self.squad1._commander.fitness_value
        if self.is_squad_1_better() and self.is_fitness_value_a_better_than_b(self.squad1._commander.fitness_value, self.best_troops_fitness):
            self.best_troops = self.squad1._commander.vector
            self.best_troops_fitness = self.squad1._commander.fitness_value
        elif not self.is_squad_1_better() and self.is_fitness_value_a_better_than_b(self.squad2._commander.fitness_value, self.best_troops_fitness):
            self.best_troops = self.squad2._commander.vector
            self.best_troops_fitness = self.squad2._commander.fitness_value
    
    def execute(self):
        # start phase 1
        print('start phase 1')
        self.phase_1_initialization() # initialize population
        for i in range(self.phase_1_max_iteration): # Airplane movement
            for j in range(self.n_plane):
                self.squad1.air_forces[j].airplane_movement()
                self.squad2.air_forces[j].airplane_movement()

        # assign air force to squad
        self.squad1.assign_squad(self.is_maximizing)
        self.squad2.assign_squad(self.is_maximizing)

        # determine attacking and defending squad
        if self.is_squad_1_better():
            self.squad1.mode = SquadMode.DEFENDING
            self.squad2.mode = SquadMode.ATTACKING
        print('phase 1 done')

        # start phase 2
        print('start phase 2')
        for i in range(self.phase_2_max_iteration):
            if self.is_squad_1_better():
                self.squad1._commander.builder_movement(i)
                self.squad1._left_cavalry.builder_movement(i)
                self.squad1._right_cavalry.builder_movement(i)
                self.squad1._builder.builder_movement(i)

                self.squad2._commander.commander_movement(self.squad1._commander.vector)
                self.squad2._left_cavalry.cavalry_movement(True, self.squad1._commander.vector)
                self.squad2._right_cavalry.cavalry_movement(False, self.squad1._commander.vector)
                self.squad2._builder.builder_movement(i)
            else:
                self.squad1._commander.commander_movement(self.squad2._commander.vector)
                self.squad1._left_cavalry.cavalry_movement(True, self.squad1._commander.vector)
                self.squad1._right_cavalry.cavalry_movement(False, self.squad1._commander.vector)
                self.squad1._builder.builder_movement(i)
                
                self.squad2._commander.builder_movement(i)
                self.squad2._left_cavalry.builder_movement(i)
                self.squad2._right_cavalry.builder_movement(i)
                self.squad2._builder.builder_movement(i)
            
            # Move special force
            self.squad1._special_force.special_force_movement()
            self.squad2._special_force.special_force_movement()

            # assign squad based on fitness
            self.squad1.assign_squad(self.is_maximizing)
            self.squad2.assign_squad(self.is_maximizing)
        
            # update best troops
            self.update_best_troops()

            # determine attacking and defending squad
            if self.is_squad_1_better():
                self.squad1.mode = SquadMode.DEFENDING
                self.squad2.mode = SquadMode.ATTACKING
            else:
                self.squad1.mode = SquadMode.ATTACKING
                self.squad2.mode = SquadMode.DEFENDING
        print('phase 2 done')
        print('best troops: ', self.best_troops)
        print('best troops fitness: ', self.best_troops_fitness)
        return [self.best_troops], self.best_troops_fitness

class BfOA_VRP(Algorithm):
    def run(self):
        al = BfOA(
            len(self.PREFERENCE_ID), # agent length
            self.fitness_function, # fitness function
            0, # lower bound
            10, # upper bound
            self.MAX_ITERATIONS, # max iteration
            self.AGENT_COUNT, # N
            True # is maximizing
        )
        return al.execute()

    def construct_solution(self):
        Xbests, Fbest = self.run()
        output = self.get_output(Xbests)

        # normalized_fitness = (Fbest - self.FITNESS_VALUE_RANGE[0]) / (self.FITNESS_VALUE_RANGE[1] - self.FITNESS_VALUE_RANGE[0])
        return output, Fbest

class BfOA_TSP(Algorithm):
    def run(self):
        al = BfOA(
            len(self.PREFERENCE_ID), # agent length
            self.fitness_function, # fitness function
            0, # lower bound
            10, # upper bound
            self.MAX_ITERATIONS, # max iteration
            self.AGENT_COUNT, # N
            True # is maximizing
        )
        return al.execute()

    def construct_solution(self):
        Xbests, Fbest = self.run()
        output = self.get_output(Xbests)

        # normalized_fitness = (Fbest - self.FITNESS_VALUE_RANGE[0]) / (self.FITNESS_VALUE_RANGE[1] - self.FITNESS_VALUE_RANGE[0])
        return output, Fbest

bfoa = BfOA_VRP(
    [37, 2, 16, 18, 36, 10, 5, 17, 96, 12, 6, 94, 44, 40, 24], # selected ids
    129, # id hotel
    1, # doi duration
    1, # doi cost
    1, # doi rating
    1, # n day
    1 # top N
)

# bfoa.construct_solution()
