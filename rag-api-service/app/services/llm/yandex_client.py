import requests
from app.config import settings
from .base import BaseLLMClient

class YandexLLMClient(BaseLLMClient):
    async def get_answer(self, 
                         system_msg: str, 
                         user_msg: str) -> str:
        prompt = {
            "modelUri": settings.MODEL_URI_32k,
            "completionOptions": {
                "stream": False,
                "temperature": 0.3,
                "maxTokens": settings.MAX_TOKENS
            },
            "messages": [
                {"role": "system", "text": system_msg},
                {"role": "user", "text": user_msg}
            ]
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": settings.YANDEX_API_KEY
        }

        resp = requests.post(settings.COMP_URL, headers=headers, json=prompt)
        return resp.json()['result']['alternatives'][0]['message']['text']
