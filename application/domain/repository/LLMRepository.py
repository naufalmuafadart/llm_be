from abc import ABC, abstractmethod

class LLMRepository(ABC):
    @abstractmethod
    def get_request_key_detail(self, content):
        pass
