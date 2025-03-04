from application.domain.repository.LLMRepository import LLMRepository
from google import genai
from dotenv import load_dotenv

import json
import os

class GeminiLLMRepository(LLMRepository):
    def get_request_key_detail(self, content):
        load_dotenv()
        client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

        response = client.models.generate_content(
            model=os.getenv('GEMINI_MODEL'),
            contents=content,
        )

        text = response.text
        text = text[8:-4]
        text = text.replace('\n', '')
        text = text.replace(' ', '')

        return json.loads(text)
