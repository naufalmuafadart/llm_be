from abc import ABC, abstractmethod

class AlgorithmRepository():
    @abstractmethod
    def construct_solution(self, selected_ids, id_hotel, doi_duration, doi_cost, doi_rating, n_day, top_n):
        pass
