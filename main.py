from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

import os

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": os.getenv('FRONTEND_URL')}}, supports_credentials=True)

@app.route('/')
def index():
    return {
        'status': 'success',
        'message': 'LLM Back End'
    }

app.run(debug=True)
