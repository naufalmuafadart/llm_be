from abc import ABC, abstractmethod

class HashingRepository:
    @abstractmethod
    def hash(self, text):
        pass

    @abstractmethod
    def verify(self, plain_text, hashed_text):
        pass
