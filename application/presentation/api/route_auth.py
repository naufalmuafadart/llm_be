from flask import Blueprint, request
from dependency_injector import containers, providers
from exception.CustomError import CustomError

# use case
from application.use_case.auth.AddAuthUseCase import AddAuthUseCase
from application.use_case.auth.UpdateAuthUseCase import UpdateAuthUseCase

# infrastructure
from application.infrastructure.repository.BcryptHashingRepository import BcryptHashingRepository
from application.infrastructure.repository.JWTAuthTokenRepository import JWTAuthTokenRepository
from application.infrastructure.repository.MongoAuthRepository import MongoAuthRepository
from application.infrastructure.repository.MongoUserRepository import MongoUserRepository

route_auth = Blueprint('route_auth', __name__)

# Dependency container
class Container(containers.DeclarativeContainer):
    hashing_repository = providers.Singleton(BcryptHashingRepository)
    auth_token_repository = providers.Singleton(JWTAuthTokenRepository)
    auth_repository = providers.Singleton(MongoAuthRepository)
    user_repository = providers.Singleton(MongoUserRepository)

# Register the container
container = Container()

@route_auth.route('/', methods=['POST', 'PUT'])
def auth_handler():
    if request.method == 'POST':
        data = request.json
        email = data.get('email')
        password = data.get('password')

        use_case = AddAuthUseCase(
            container.hashing_repository(),
            container.auth_token_repository(),
            container.auth_repository(),
            container.user_repository()
        )

        access_token, refresh_token = use_case.execute(email, password)

        return {
            'status': 'success',
            'message': 'success add auth',
            'data': {
                'access_token': access_token,
                'refresh_token': refresh_token,
            }
        }
    elif request.method == 'PUT':
        data = request.json
        refresh_token = data.get('refresh_token')

        use_case = UpdateAuthUseCase(
            container.auth_token_repository(),
            container.auth_repository(),
        )

        access_token = use_case.execute(refresh_token)
        return {
            'status': 'success',
            'message': 'success update auth',
            'data': {
                'access_token': access_token,
            }
        }

@route_auth.errorhandler(Exception)
def handle_error(e):
    if isinstance(e, CustomError):
        return {
            'status': 'fail',
            'message': str(e),
        }, e.code
    return {
        'status': 'fail',
        'message': 'internal server error',
        # 'error': str(e),
    }, 500
