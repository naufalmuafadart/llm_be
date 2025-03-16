from application.domain.repository.AttractionRankingRepository import AttractionRankingRepository
import numpy as np

class AHPAttractionRankingRepository(AttractionRankingRepository):
    @staticmethod
    def ahp(weights):
        normalized_matrix = np.matrix([[1, weights[0] / weights[1]], [weights[1] / weights[0], 1]])
        weighted_sum = normalized_matrix.sum(axis=1)
        weighted_sum = [weighted_sum[0].A1[0], weighted_sum[1].A1[0]]

        normalized_matrix = normalized_matrix / np.array(weighted_sum)[:, np.newaxis]
        weighted_sum = normalized_matrix.sum(axis=1)
        weighted_sum = [weighted_sum[0].A1[0], weighted_sum[1].A1[0]]
        return weighted_sum

    @staticmethod
    def smart(ahp_scores, matrix):
        scores = []
        for i in range(len(matrix)):
            scores.append(matrix[i][0] * ahp_scores[0] + matrix[i][0] * ahp_scores[0])
        return scores

    def sort_attraction(self, registered_attractions, rating_weight, cost_weight):
        attractions = []
        for i in range(len(registered_attractions)):
            attractions.append({
                'name': '',
                'rating': registered_attractions[i].rating,
                'price': registered_attractions[i].cost + 1
            })

        # Convert data to matrix
        ratings = np.array([attr["rating"] for attr in attractions])
        prices = np.array([attr["price"] for attr in attractions])
        matrix = np.array([ratings, 1 / prices]).T  # Invert price for cost criteria

        # Criteria weights
        weights = np.array([rating_weight, cost_weight])

        # AHP Calculation
        ahp_scores = self.ahp(weights)

        # SMART Calculation
        smart_scores = self.smart(ahp_scores, matrix)

        for i in range(len(smart_scores)):
            registered_attractions[i].smart_score = smart_scores[i]

        return sorted(registered_attractions, key=lambda x: x.smart_score, reverse=False)
