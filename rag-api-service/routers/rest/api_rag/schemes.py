from pydantic import BaseModel
from typing import Optional

class LLMAPIRequest(BaseModel):
    question: str
    conversation_id: Optional[int] = None

class LLMAPIResponse(BaseModel):
    answer: str
    