from abc import ABC, abstractmethod

class AttractionRepository(ABC):
    @abstractmethod
    def get_ids_by_selected_tags(self, tags):
        pass

    @abstractmethod
    def get_registered_attraction_by_ids(self, ids):
        pass
