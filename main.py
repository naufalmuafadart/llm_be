from flask import Flask, request
from flask_cors import CORS
from dotenv import load_dotenv
from dependency_injector import containers, providers

# infrastructure
from application.infrastructure.PandasDataFrameRepositoy import PandasDataFrameRepository
from application.infrastructure.RouteAlgorithmRepository import RouteAlgorithmRepository

# use case
from application.use_case.GenerateRecommendationUseCase import GenerateRecommendationUseCase

import os

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": os.getenv('FRONTEND_URL')}}, supports_credentials=True)

# Dependency container
class Container(containers.DeclarativeContainer):
    data_frame_repository = providers.Singleton(PandasDataFrameRepository)
    algorithm_repository = providers.Singleton(RouteAlgorithmRepository)

# Register the container
container = Container()

@app.route('/')
def index():
    return {
        'status': 'success',
        'message': 'LLM Back End'
    }

@app.route('/api/recommender', methods=['post'])
def recommender():
    try:
        data = request.json
        message = data.get('message')
        use_case = GenerateRecommendationUseCase(
            container.data_frame_repository(),
            container.algorithm_repository(),
        )
        content = use_case.execute(message)
        return {
            'status': 'success',
            'data': {
                'content': content
            }
        }
    except Exception as e:
        return {
            'status': 'fail',
            'message': str(e),
            # 'message': 'fail to generate route',
        }, 500

app.run(debug=True)
