from pydantic import BaseModel
from typing import List

class EncoderRequest(BaseModel):
    chunk: str

class EncoderResponse(BaseModel):
    vector: List 