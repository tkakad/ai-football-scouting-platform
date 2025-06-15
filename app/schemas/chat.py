from pydantic import BaseModel
from typing import Optional

class ChatInsightRequest(BaseModel):
    prompt: str
    context: Optional[str] = None

class ChatInsightResponse(BaseModel):
    insight: str