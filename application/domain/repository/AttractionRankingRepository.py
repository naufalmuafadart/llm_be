from abc import ABC, abstractmethod

class AttractionRankingRepository(ABC):
    @abstractmethod
    def sort_attraction(self, registered_attractions, rating_weight, cost_weight):
        pass
