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
    emotion_intensity: Optional[float] = None
    suggestions: Optional[List[str]] = None
    timestamp: datetime = datetime.now()
    context: Optional[Dict[str, Any]] = None

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

# 评估相关模型
class EvaluationRequest(BaseModel):
    """评估请求模型"""
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    message_id: Optional[int] = None
    user_message: str
    bot_response: str
    user_emotion: Optional[str] = "neutral"
    emotion_intensity: Optional[float] = 5.0
    prompt_version: Optional[str] = None  # 用于A/B测试

class EvaluationResponse(BaseModel):
    """评估响应模型"""
    evaluation_id: int
    empathy_score: float
    naturalness_score: float
    safety_score: float
    average_score: float
    total_score: float
    overall_comment: str
    strengths: List[str]
    weaknesses: List[str]
    improvement_suggestions: List[str]
    created_at: datetime

class BatchEvaluationRequest(BaseModel):
    """批量评估请求模型"""
    session_id: Optional[str] = None
    limit: Optional[int] = 10  # 最多评估多少条对话

class ComparePromptsRequest(BaseModel):
    """Prompt对比请求模型"""
    user_message: str
    responses: Dict[str, str]  # prompt_name -> bot_response
    user_emotion: Optional[str] = "neutral"
    emotion_intensity: Optional[float] = 5.0

class HumanVerificationRequest(BaseModel):
    """人工验证请求模型"""
    evaluation_id: int
    empathy_score: int  # 1-5
    naturalness_score: int  # 1-5
    safety_score: int  # 1-5
    comment: Optional[str] = None

class EvaluationStatistics(BaseModel):
    """评估统计模型"""
    total_count: int
    average_scores: Dict[str, float]
    score_ranges: Optional[Dict[str, Dict[str, float]]] = None
    
class EvaluationListResponse(BaseModel):
    """评估列表响应模型"""
    evaluations: List[Dict[str, Any]]
    total: int
    statistics: Optional[Dict[str, Any]] = None