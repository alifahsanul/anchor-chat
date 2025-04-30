from pydantic import BaseModel
from typing import List, Dict, Optional

class URLRequest(BaseModel):
    url: str

class LoginRequest(BaseModel):
    password: str

class ChatRequest(BaseModel):
    url: str
    question: str
    chat_history: List[Dict[str, str]] = [] 