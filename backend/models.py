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

class FeedbackRequest(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    message_id: Optional[int] = None
    feedback_type: str  # irrelevant, lack_empathy, overstepping, helpful, other
    rating: int  # 1-5
    comment: Optional[str] = None
    user_message: Optional[str] = None
    bot_response: Optional[str] = None

class FeedbackResponse(BaseModel):
    feedback_id: int
    session_id: str
    feedback_type: str
    rating: int
    created_at: datetime
    message: str = "Feedback received successfully"

class FeedbackStatistics(BaseModel):
    total_count: int
    avg_rating: float
    by_type: List[Dict[str, Any]]
    
class FeedbackListResponse(BaseModel):
    feedbacks: List[Dict[str, Any]]
    total: int