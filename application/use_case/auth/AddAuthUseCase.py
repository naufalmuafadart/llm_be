from exception.UnauthorizedError import UnauthorizedError
from application.domain.entity.auth_token.RegisterAuthTokenPayloadEntity import RegisterAuthTokenPayloadEntity

class AddAuthUseCase:
    def __init__(self, hashing_repository, auth_token_repository, auth_repository, user_repository):
        self.hashing_repository = hashing_repository
        self.auth_token_repository = auth_token_repository
        self.auth_repository = auth_repository
        self.user_repository = user_repository

    def execute(self, email, password):
        registered_user = self.user_repository.get_by_email(email)

        # Verify the password
        try:
            self.hashing_repository.verify(password, registered_user.password)
        except Exception as e:
            raise UnauthorizedError('Email or password is invalid')
        
        payload = RegisterAuthTokenPayloadEntity(registered_user.id)
        access_token = self.auth_token_repository.create(payload, True)
        refresh_token = self.auth_token_repository.create(payload, False)
        refresh_token_exp = self.auth_token_repository.get_expired_at(refresh_token, False)

        # store refresh token in database
        self.auth_repository.insert(refresh_token, registered_user.id, refresh_token_exp)

        return access_token, refresh_token
