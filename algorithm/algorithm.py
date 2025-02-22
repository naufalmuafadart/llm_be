from datetime import datetime, timedelta
import pandas as pd

import copy
import random
import numpy as np


class Algorithm:
    AGENT_COUNT = 10
    MAX_ITERATIONS = 1

    def __init__(self, ids, hotel_id, doi_duration, doi_cost, doi_rating, days_count, n):
        self.PREFERENCE_ID = list(map(int, ids)) # => [1,2,3]
        self.HOTEL_ID = hotel_id
        self.DOI_DURATION = doi_duration
        self.DOI_COST = doi_cost
        self.DOI_RATING = doi_rating
        self.DOI_POI_INCLUDED = doi_rating
        self.DAYS_COUNT = days_count
        self.AGENT_LENGTH = len(self.PREFERENCE_ID)
        self.DEPART_TIME = 8 * 3600
        self.ARRIVAL_TIME = 21 * 3600
        self.n = n

        # get dataset
        self.prepare_dataset()

        # generate initial population
        self.agents = self.generate_initial_population(self.AGENT_COUNT, self.AGENT_LENGTH)

        # set range for each MAUT attributes
        self.DURATION_RANGE = self.get_min_max_duration(self.agents)
        self.RATING_RANGE = [self.get_min_rating(), self.get_max_rating()]
        self.COST_RANGE = [self.get_min_cost(), self.get_cost(self.PREFERENCE_ID)]
        self.POI_INCLUDED_RANGE = [self.DAYS_COUNT, len(self.PREFERENCE_ID)]
        self.FITNESS_VALUE_RANGE = [1, 3]

    def get_pois_cost(self, _ids):
        return self.df_places[self.df_places['id'].isin(_ids)]['tarif'].tolist()

    def get_pois_rating(self, _ids):
        return self.df_places[self.df_places['id'].isin(_ids)]['rating'].tolist()

    def get_poi_closing_hour(self, _id):
        return self.df_schedule[self.df_schedule['id_tempat'] == _id].iloc[0]['jam_tutup']

    def get_min_rating(self):
        min_series = self.df_places.min(numeric_only=True)
        return min_series['rating']

    def get_max_rating(self):
        max_series = self.df_places.max(numeric_only=True)
        return max_series['rating']

    def get_average_rating(self, _ids):
        return self.df_places[self.df_places['id'].isin(_ids)].mean(numeric_only=True)['rating']

    @staticmethod
    def get_min_cost():
        return 0

    def get_cost(self, selected_agents):
        return self.df_places[self.df_places['id'].isin(selected_agents)].sum()['tarif']

    def get_poi_duration(self, _id):
        return self.df_places[self.df_places['id'] == _id].iloc[0]['durasi']

    def get_poi_opening_hour(self, _id):
        return self.df_schedule[self.df_schedule['id_tempat'] == _id].iloc[0]['jam_buka']

    def get_travel_time(self, _id1, _id2):
        df_filter = self.df_time_matrix[(self.df_time_matrix['id_a'] == _id1) & (self.df_time_matrix['id_b'] == _id2)]
        return df_filter.iloc[0]['durasi']

    @staticmethod
    def generate_initial_population(agent_count, agent_length):
        random.seed(5454)
        return [[random.random() * 10 for i in range(agent_length)] for j in range(agent_count)]

    # Fungsi untuk mendapatkan total durasi pada suatu hari
    def get_single_day_duration(self, single_day_route):
        if len(single_day_route) == 0:
            return 0

        if len(single_day_route) == 1:
            duration = self.get_travel_time(self.HOTEL_ID, single_day_route[0])
            duration += self.get_poi_duration(single_day_route[0])
            duration += self.get_travel_time(single_day_route[0], self.HOTEL_ID)
            return duration

        duration = 0
        for i in range(len(single_day_route)):
            if i == 0: # first poi
                duration += self.get_travel_time(self.HOTEL_ID, single_day_route[i])
                duration += self.get_poi_duration(single_day_route[i])
            elif i != len(single_day_route)-1:
                duration += self.get_travel_time(single_day_route[i], single_day_route[i+1])
                duration += self.get_poi_duration(single_day_route[i+1])
            else: # last poi
                duration += self.get_travel_time(single_day_route[i], self.HOTEL_ID)

        return duration

    def get_single_day_travel_duration(self, single_day_route):
        if len(single_day_route) == 0:
            return 0

        if len(single_day_route) == 1:
            duration = self.get_travel_time(self.HOTEL_ID, single_day_route[0])
            duration += self.get_travel_time(single_day_route[0], self.HOTEL_ID)
            return duration

        duration = 0
        for i in range(len(single_day_route)):
            if i == 0: # first poi
                duration += self.get_travel_time(self.HOTEL_ID, single_day_route[i])
            elif i != len(single_day_route)-1:
                duration += self.get_travel_time(single_day_route[i], single_day_route[i+1])
            else: # last poi
                duration += self.get_travel_time(single_day_route[i], self.HOTEL_ID)

        return duration

    # Fungsi untuk mendapatkan total durasi selama N hari
    def get_multi_day_duration(self, routes):
        durations = 0
        for route in routes:
            durations += self.get_single_day_duration(route)
        return durations

    def get_multi_day_travel_duration(self, routes):
        durations = 0
        for route in routes:
            durations += self.get_single_day_travel_duration(route)
        return durations

    # Fungsi untuk mengecek apakah poi_id dapat dimasukkan ke single_day_route
    def check_poi_able_to_be_assigned(self, single_day_route, poi_id):
        if len(single_day_route) == 0:
            return True
        sdr = copy.deepcopy(single_day_route)
        sdr.append(poi_id)

        last_poi_id = single_day_route[len(single_day_route)-1]
        single_day_duration = self.get_single_day_duration(single_day_route)
        single_day_duration -= self.get_travel_time(last_poi_id, self.HOTEL_ID)
        single_day_duration += self.DEPART_TIME

        arrival_time_to_poi = single_day_duration + self.get_travel_time(last_poi_id, poi_id)
        departure_time_from_poi = arrival_time_to_poi + self.get_poi_duration(poi_id)
        arrival_time_to_hotel = departure_time_from_poi + self.get_travel_time(poi_id, self.HOTEL_ID)

        if arrival_time_to_hotel > self.ARRIVAL_TIME:
            return False

        if departure_time_from_poi > self.get_poi_closing_hour(poi_id):
            return False

        if arrival_time_to_poi < self.get_poi_opening_hour(poi_id):
            return False

        return True

    # Fungsi untuk mengecek apakah ada poi yang mungkin diassign ke routes
    def check_any_poi_able_to_be_assigned(self, routes, R, R_assigned):
        for _id in R:  # perulangan untuk setiap _id POI
            if _id not in R_assigned:  # jika _id termasuk unassigned POI
                for route in routes:  # Perulangan untuk setiap day route
                    if self.check_poi_able_to_be_assigned(route, _id):  # cek apakah _id POI diassign ke hari tersebut
                        return True
        return False

    @staticmethod
    def get_day_with_fewest_poi(routes, index_ignored):
        selected_index = 0
        min_poi_assigned = 200
        for i in range(len(routes)):
            if i not in index_ignored:
                if len(routes[i]) < min_poi_assigned:
                    selected_index = i
                    min_poi_assigned = len(routes[i])
        return selected_index

    def greedy_separate_route(self, agent, selected_poi, days_count):
        A = np.argsort(agent)
        R = [selected_poi[A[i]] for i in range(len(selected_poi))]
        R_assigned = []  # id yang sudah dimasukkan ke rute

        routes = [[] for _ in range(days_count)] # for storing route for each day
        is_any_poi_able_to_assign = self.check_any_poi_able_to_be_assigned(routes, R, R_assigned)
        while is_any_poi_able_to_assign: # if any POI able to be assigned
            days_included = []
            selected_day = self.get_day_with_fewest_poi(routes, days_included)
            poi_has_assigned = False
            while not poi_has_assigned:
                i = 0
                while i < len(R) and not poi_has_assigned:
                    if self.check_poi_able_to_be_assigned(routes[selected_day], R[i]) and R[i] not in R_assigned:
                        routes[selected_day].append(R[i])
                        R_assigned.append(R[i])
                        poi_has_assigned = True
                    i += 1
                if not poi_has_assigned: # jika tidak ada poi yang diassign, pilih hari lain
                    days_included.append(selected_day)
                    selected_day = self.get_day_with_fewest_poi(routes, days_included)
            is_any_poi_able_to_assign = self.check_any_poi_able_to_be_assigned(routes, R, R_assigned)

        return routes

    def get_min_max_duration(self, agents):
        min_duration = 1000000
        max_duration = 0
        for agent in agents:
            routes = self.greedy_separate_route(agent, self.PREFERENCE_ID, self.DAYS_COUNT)
            duration = self.get_multi_day_duration(routes)
            if duration < min_duration:
                min_duration = duration
            if duration > max_duration:
                max_duration = duration
        return [min_duration, max_duration]

    @staticmethod
    def get_v(value, min, max, is_greater_better):
        if value < min:
            if is_greater_better:
                return 0
            return 1
        if value > max:
            if is_greater_better:
                return 1
            return 0
        return (abs(value - min) / (max - min)) if is_greater_better else (abs(max - value) / (max - min))

    def fitness_function(self, agent):
        # Mendapatkan rute dari agen
        routes = self.greedy_separate_route(agent, self.PREFERENCE_ID, self.DAYS_COUNT)

        # Mendapatkan total durasi perjalanan
        duration = self.get_multi_day_travel_duration(routes)

        assigned_ids = []
        for day_route in routes:
            assigned_ids.extend(day_route)
        # df_temp = df_places[df_places['id'].isin(assigned_ids)]

        rating = self.get_average_rating(assigned_ids)
        costs = self.get_cost(assigned_ids)

        MAUT = 0
        MAUT += self.get_v(duration, self.DURATION_RANGE[0], self.DURATION_RANGE[1], False) * self.DOI_DURATION
        MAUT += self.get_v(rating, self.RATING_RANGE[0], self.RATING_RANGE[1], True) * self.DOI_RATING
        MAUT += self.get_v(costs, self.COST_RANGE[0], self.COST_RANGE[1], False) * self.DOI_COST
        MAUT += self.get_v(len(assigned_ids), self.POI_INCLUDED_RANGE[0], self.POI_INCLUDED_RANGE[1], True) * self.DOI_POI_INCLUDED
        return MAUT

    def tsp_fitness_function(self, agent):
        routes = self.greedy_separate_route(agent, self.PREFERENCE_ID, self.DAYS_COUNT)
        return self.get_multi_day_travel_duration(routes)

    def get_best_agent(self, agents):
        index = -1
        max = 0
        i = 0
        for agent in agents:
            fitness_value = self.fitness_function(agent)
            if fitness_value > max:
                max = fitness_value
                index = i
            i += 1
        return (max, agents[index])

    def get_time_line(self, l):
        if len(l) == 0:
            return []
        current_time = datetime(2023, 11, 19, 8, 0, 0)
        time_line = [current_time.strftime('%H:%M:%S')]

        i = 0
        while i < len(l):
            if i == 0:
                travel_time = self.get_travel_time(self.HOTEL_ID, l[i])
                time_delta = timedelta(seconds=np.int16(travel_time).item())
                current_time += time_delta
                time_line.append(current_time.strftime('%H:%M:%S'))
            elif i != len(l)-1:
                time_spent = self.get_poi_duration(l[i])
                travel_time = self.get_travel_time(l[i], l[i+1])
                time_delta = timedelta(seconds=np.int16(travel_time).item() + np.int16(time_spent).item())
                current_time += time_delta
                time_line.append(current_time.strftime('%H:%M:%S'))
            else:
                time_spent = self.get_poi_duration(l[i])
                time_delta = timedelta(seconds=np.int16(time_spent).item())
                current_time += time_delta
                time_line.append(current_time.strftime('%H:%M:%S'))

                travel_time = self.get_travel_time(l[i], self.HOTEL_ID)
                time_delta = timedelta(seconds=np.int16(travel_time).item())
                current_time += time_delta
                time_line.append(current_time.strftime('%H:%M:%S'))
            i += 1

        return time_line

    def prepare_dataset(self):
        self.df_places = pd.read_csv('./dataset/places.csv')
        self.df_time_matrix = pd.read_csv('./dataset/place_timematrix.csv')
        self.df_schedule = pd.read_csv('./dataset/place_jadwal.csv')
        self.df_schedule['jam_buka'] = self.df_schedule['jam_buka'].apply(lambda x: int(x[:2]) * 3600 + int(x[3:]) * 60)
        self.df_schedule['jam_tutup'] = self.df_schedule['jam_tutup'].apply(lambda x: int(x[:2]) * 3600 + int(x[3:]) * 60)

    # fungsi yang mengembalikan output untuk API
    def get_output(self, agents):
        output = []
        for agent in agents:
            route = self.greedy_separate_route(agent, self.PREFERENCE_ID, self.DAYS_COUNT)
            fitness_value = self.fitness_function(agent)
            normalized_fitness_value = self.fitness_function(agent) / (self.FITNESS_VALUE_RANGE[0]+self.FITNESS_VALUE_RANGE[1])
            duration = self.get_multi_day_travel_duration(route)

            pois = []
            for i in range(len(route)):
                for poi in route[i]:
                    pois.append(poi)
            cost = self.get_cost(pois)
            ratings = self.get_pois_rating(pois)

            print(f'Fitness value : {fitness_value}')
            print(f'Normalized Fitness value : {normalized_fitness_value}')
            print(F'Duration: {duration}')
            print(F'Cost: {cost}')
            print(F'Rating: {sum(ratings) / len(ratings)}')

            results = []
            for day_route in route:
                results.append({
                    'index': day_route,
                    'waktu': self.get_time_line(day_route),
                    'rating': self.get_pois_rating(day_route),
                    'tarif': self.get_pois_cost(day_route),
                })
            print('results')
            print(results)
            output.append({'results': results})
        return output
