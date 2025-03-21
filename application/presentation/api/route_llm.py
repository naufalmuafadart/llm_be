from flask import Blueprint, request
from dependency_injector import containers, providers
from exception.CustomError import CustomError

# infrastructure
from application.infrastructure.repository.GeminiLLMRepository import GeminiLLMRepository

# use case
from application.use_case.llm.ExtractKeyDetailUseCase import ExtractKeyDetailUseCase

# Dependency container
class Container(containers.DeclarativeContainer):
    llm_repository = providers.Singleton(GeminiLLMRepository)

# Register the container
container = Container()

route_llm = Blueprint('route_llm', __name__)

@route_llm.route('/extract_key_detail', methods=['POST'])
def extract_key_detail():
    use_case = ExtractKeyDetailUseCase(
        container.llm_repository()
    )
    data = request.json
    message = data.get('message')

    detail = use_case.execute(message)

    return {
        'status': 'success',
        'message': 'success extract key detail',
        'data': detail
    }

@route_llm.errorhandler(Exception)
def handle_error(e):
    if isinstance(e, CustomError):
        return {
            'status': 'fail',
            'message': str(e),
        }, e.code
    return {
        'status': 'fail',
        'message': 'internal server error',
        'error': str(e),
    }, 500
