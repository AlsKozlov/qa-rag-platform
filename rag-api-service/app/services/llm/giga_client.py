import requests
from app.config import settings
from .base import BaseLLMClient

class GigaChatLLMClient(BaseLLMClient):
    async def get_answer(self, system_msg: str, user_msg: str) -> str:
        prompt = {
            "modelUri": settings.GIGACHAT_MODEL_URI,
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
            "Authorization": f"Bearer {settings.GIGACHAT_API_KEY}"
        }

        response = requests.post(settings.GIGACHAT_URL, headers=headers, json=prompt)
        response.raise_for_status()
        return response.json()['result']['alternatives'][0]['message']['text']
