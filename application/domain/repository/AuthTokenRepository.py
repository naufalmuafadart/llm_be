from abc import ABC, abstractmethod

class AuthTokenRepository(ABC):
    @abstractmethod
    def create(self, payload, is_access_token):
        pass

    @abstractmethod
    def validate(self, token, is_access_token):
        pass

    @abstractmethod
    def get_expired_at(self, token, is_access_token):
        pass
