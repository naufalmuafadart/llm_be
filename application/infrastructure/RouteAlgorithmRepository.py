from application.repository.AlgorithmRepository import AlgorithmRepository
from algorithm.algorithm_bfoa import BfOA_VRP

class RouteAlgorithmRepository(AlgorithmRepository):
    def construct_solution(self, selected_ids, id_hotel, doi_duration, doi_cost, doi_rating, n_day, top_n):
        bfoa = BfOA_VRP(
            selected_ids, # selected ids
            id_hotel, # id hotel
            doi_duration, # doi duration
            doi_cost, # doi cost
            doi_rating, # doi rating
            n_day, # n day
            top_n # top N
        )
        return bfoa.construct_solution() # return output, Fbest
