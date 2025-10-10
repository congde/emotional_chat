from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = datetime.now()
    emotion: Optional[str] = None  # 情感标签

class ChatSession(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    messages: List[Message] = []
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    emotion_state: Optional[Dict[str, Any]] = None  # 当前情感状态

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    emotion: Optional[str] = None
    suggestions: Optional[List[str]] = None
    timestamp: datetime = datetime.now()

class EmotionAnalysis(BaseModel):
    emotion: str
    confidence: float
    intensity: float
    suggestions: List[str]
