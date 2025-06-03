from pydantic import BaseModel, Field
from typing import Optional


class LocalModelRequest(BaseModel):
    system_msg: str
    user_msg: str
    temperature: Optional[float] = Field(0.2, ge=0, le=1, description="Temperature value between 0 and 1")
    top_p: Optional[float] = Field(0.95, ge=0, le=1, description="Top_p value between 0 and 1")
    max_tokens: Optional[int] = Field(20000, description="max_tokens of model output")

    