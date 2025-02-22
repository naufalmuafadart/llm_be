from abc import ABC, abstractmethod

class AuthRepository(ABC):
    @abstractmethod
    def insert(self, token, user_id, expired_at):
        pass
