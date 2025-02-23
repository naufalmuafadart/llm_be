from application.domain.entity.auth_token.RegisterAuthTokenPayloadEntity import RegisterAuthTokenPayloadEntity

class UpdateAuthUseCase:
    def __init__(self, auth_token_repository, auth_repository):
        self.auth_token_repository = auth_token_repository
        self.auth_repository = auth_repository

    def execute(self, refresh_token):
        # validate refresh token
        auth_token_payload = self.auth_token_repository.validate(refresh_token, False)

        # validate refresh token exist in database
        self.auth_repository.validate_token_exist(refresh_token, auth_token_payload.id)

        # create payload for access token
        payload = RegisterAuthTokenPayloadEntity(auth_token_payload.id)

        # create new access token
        access_token = self.auth_token_repository.create(payload, True)

        # return new access token
        return access_token
