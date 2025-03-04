from flask import Flask, request
from flask_cors import CORS
from dotenv import load_dotenv
from dependency_injector import containers, providers
from application.infrastructure.database.mongo_db import MongoDBClient

# route
from application.presentation.api.route_auth import route_auth
from application.presentation.api.route_llm import route_llm

# infrastructure
from application.infrastructure.repository.PandasDataFrameRepositoy import PandasDataFrameRepository
from application.infrastructure.repository.RouteAlgorithmRepository import RouteAlgorithmRepository
from application.infrastructure.repository.GeminiLLMRepository import GeminiLLMRepository
from application.infrastructure.repository.MongoAttractionRepository import MongoAttractionRepository

# use case
from application.use_case.GenerateRecommendationUseCase import GenerateRecommendationUseCase

import os

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": os.getenv('FRONTEND_URL')}}, supports_credentials=True)

#setup mongodb
client = MongoDBClient()
db = client.get_database()

# Dependency container
class Container(containers.DeclarativeContainer):
    data_frame_repository = providers.Singleton(PandasDataFrameRepository)
    algorithm_repository = providers.Singleton(RouteAlgorithmRepository)
    llm_repository = providers.Singleton(GeminiLLMRepository)
    attraction_repository = providers.Singleton(MongoAttractionRepository)

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
            container.llm_repository(),
            container.attraction_repository(),
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
            'message': 'fail to generate route',
            # 'message': str(e),
        }, 500

app.register_blueprint(route_auth, url_prefix='/api/auth')
app.register_blueprint(route_llm, url_prefix='/api/llm')

app.run(debug=True)
