from abc import ABC, abstractmethod

class DataFrameRepository(ABC):
    @abstractmethod
    def get_data(self, file_name):
        pass
