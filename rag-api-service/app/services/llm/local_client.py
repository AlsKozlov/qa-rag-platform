import requests
from app.config import settings
from .base import BaseLLMClient

class LocalLLMClient(BaseLLMClient):
    async def get_answer(self, 
                         system_msg: str, 
                         user_msg: str) -> str:
        headers = {"Content-Type": "application/json"}
        data = {"system_msg": system_msg, "user_msg": user_msg}

        response = requests.post(settings.LOCAL_LMM_SERVICE_API, headers=headers, json=data)
        response.raise_for_status()
        
        return response.json()["content"]
