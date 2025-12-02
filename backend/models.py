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
    deep_thinking: Optional[bool] = False  # 深度思考模式

class ChatResponse(BaseModel):
    response: str
    session_id: str
    emotion: Optional[str] = None
    emotion_intensity: Optional[float] = None
    suggestions: Optional[List[str]] = None
    timestamp: datetime = datetime.now()
    context: Optional[Dict[str, Any]] = None
    plugin_used: Optional[str] = None  # 使用的插件名称
    plugin_result: Optional[Dict[str, Any]] = None  # 插件调用结果

# 多模态支持
class MultimodalRequest(BaseModel):
    """多模态聊天请求"""
    text: Optional[str] = None  # 文本消息
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    audio_transcript: Optional[str] = None  # 音频转录文本
    audio_features: Optional[Dict[str, Any]] = None  # 音频特征
    image_analysis: Optional[Dict[str, Any]] = None  # 图像分析结果

class MultimodalResponse(BaseModel):
    """多模态聊天响应"""
    response: str
    session_id: str
    emotion: Optional[str] = None
    emotion_intensity: Optional[float] = None
    suggestions: Optional[List[str]] = None
    timestamp: datetime = datetime.now()
    context: Optional[Dict[str, Any]] = None
    audio_url: Optional[str] = None  # 语音回复URL
    multimodal_emotion: Optional[Dict[str, Any]] = None  # 多模态情感融合结果

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

# 个性化配置相关模型
class PersonalizationConfig(BaseModel):
    """个性化配置模型"""
    user_id: str
    
    # 角色层
    role: str = "温暖倾听者"
    role_name: str = "心语"
    role_background: Optional[str] = None
    personality: str = "温暖耐心"
    core_principles: Optional[List[str]] = None
    forbidden_behaviors: Optional[List[str]] = None
    
    # 表达层
    tone: str = "温和"
    style: str = "简洁"
    formality: float = 0.3
    enthusiasm: float = 0.5
    empathy_level: float = 0.8
    humor_level: float = 0.3
    response_length: str = "medium"
    use_emoji: bool = False
    
    # 记忆层
    preferred_topics: Optional[List[str]] = None
    avoided_topics: Optional[List[str]] = None
    communication_preferences: Optional[Dict[str, Any]] = None
    
    # 高级设置
    learning_mode: bool = True
    safety_level: str = "standard"
    context_window: int = 10
    
    # 情境化角色
    situational_roles: Optional[Dict[str, Any]] = None
    active_role: str = "default"

class PersonalizationUpdateRequest(BaseModel):
    """个性化配置更新请求"""
    role: Optional[str] = None
    role_name: Optional[str] = None
    role_background: Optional[str] = None
    personality: Optional[str] = None
    core_principles: Optional[List[str]] = None
    forbidden_behaviors: Optional[List[str]] = None
    
    tone: Optional[str] = None
    style: Optional[str] = None
    formality: Optional[float] = None
    enthusiasm: Optional[float] = None
    empathy_level: Optional[float] = None
    humor_level: Optional[float] = None
    response_length: Optional[str] = None
    use_emoji: Optional[bool] = None
    
    preferred_topics: Optional[List[str]] = None
    avoided_topics: Optional[List[str]] = None
    communication_preferences: Optional[Dict[str, Any]] = None
    
    learning_mode: Optional[bool] = None
    safety_level: Optional[str] = None
    context_window: Optional[int] = None
    
    situational_roles: Optional[Dict[str, Any]] = None
    active_role: Optional[str] = None

class PersonalizationResponse(BaseModel):
    """个性化配置响应"""
    user_id: str
    config: PersonalizationConfig
    total_interactions: int
    positive_feedbacks: int
    config_version: int
    created_at: datetime
    updated_at: datetime

class RoleTemplate(BaseModel):
    """角色模板"""
    id: str
    name: str
    role: str
    personality: str
    tone: str
    style: str
    description: str
    icon: str
    background: Optional[str] = None
    core_principles: List[str]
    sample_responses: List[str]