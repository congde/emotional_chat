#!/usr/bin/env python3
"""
聊天相关数据模型
定义聊天API的请求和响应模型
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum

from .common_schemas import BaseResponse, PaginationRequest, PaginationResponse


class MessageRole(str, Enum):
    """消息角色枚举"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class EmotionType(str, Enum):
    """情绪类型枚举"""
    HAPPY = "开心"
    SAD = "难过"
    ANGRY = "愤怒"
    ANXIOUS = "焦虑"
    FEAR = "恐惧"
    SURPRISED = "惊讶"
    DISGUSTED = "厌恶"
    NEUTRAL = "平静"
    EXCITED = "兴奋"
    WORRIED = "担心"
    FRUSTRATED = "沮丧"
    LONELY = "孤独"
    CONFUSED = "困惑"


class ChatMessage(BaseModel):
    """聊天消息模型"""
    id: str = Field(..., description="消息ID")
    role: MessageRole = Field(..., description="消息角色")
    content: str = Field(..., min_length=1, max_length=2000, description="消息内容")
    emotion: Optional[EmotionType] = Field(None, description="情绪类型")
    emotion_intensity: Optional[float] = Field(None, ge=0, le=10, description="情绪强度")
    timestamp: datetime = Field(default_factory=datetime.now, description="消息时间")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    
    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('消息内容不能为空')
        return v.strip()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str = Field(..., min_length=1, max_length=2000, description="用户消息")
    user_id: str = Field(..., min_length=3, max_length=50, description="用户ID")
    session_id: Optional[str] = Field(None, description="会话ID，不提供则自动生成")
    emotion: Optional[EmotionType] = Field(None, description="用户当前情绪")
    emotion_intensity: Optional[float] = Field(None, ge=0, le=10, description="情绪强度")
    use_memory: bool = Field(True, description="是否使用记忆系统")
    use_rag: bool = Field(True, description="是否使用RAG知识库")
    context: Optional[Dict[str, Any]] = Field(None, description="额外上下文")
    
    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('消息内容不能为空')
        return v.strip()
    
    @validator('user_id')
    def validate_user_id(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('用户ID长度不能少于3个字符')
        return v.strip()
    
    class Config:
        schema_extra = {
            "example": {
                "message": "我最近总是失眠，怎么办？",
                "user_id": "user123",
                "session_id": "session456",
                "emotion": "焦虑",
                "emotion_intensity": 7.5,
                "use_memory": True,
                "use_rag": True,
                "context": {
                    "previous_emotion": "平静",
                    "user_preferences": {
                        "response_style": "专业且温暖"
                    }
                }
            }
        }


class ChatResponse(BaseResponse):
    """聊天响应模型"""
    response: str = Field(..., description="机器人回复")
    emotion: EmotionType = Field(..., description="检测到的用户情绪")
    emotion_intensity: float = Field(..., ge=0, le=10, description="情绪强度")
    session_id: str = Field(..., description="会话ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文信息")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "success": True,
                "message": "回复生成成功",
                "response": "我理解你的困扰。失眠确实很痛苦，让我来帮你分析一下可能的原因和解决方法...",
                "emotion": "焦虑",
                "emotion_intensity": 7.5,
                "session_id": "session456",
                "timestamp": "2025-10-16T14:30:00Z",
                "status_code": 200,
                "context": {
                    "memories_count": 5,
                    "emotion_trend": "上升",
                    "has_profile": True,
                    "used_rag": True,
                    "knowledge_sources": 3
                }
            }
        }


class SessionInfo(BaseModel):
    """会话信息模型"""
    session_id: str = Field(..., description="会话ID")
    user_id: str = Field(..., description="用户ID")
    title: Optional[str] = Field(None, description="会话标题")
    message_count: int = Field(0, ge=0, description="消息数量")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    last_activity: Optional[datetime] = Field(None, description="最后活动时间")
    emotion_summary: Optional[Dict[str, Any]] = Field(None, description="情绪摘要")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserProfile(BaseModel):
    """用户档案模型"""
    user_id: str = Field(..., description="用户ID")
    nickname: Optional[str] = Field(None, description="昵称")
    preferences: Optional[Dict[str, Any]] = Field(None, description="用户偏好")
    emotion_history: Optional[List[Dict[str, Any]]] = Field(None, description="情绪历史")
    session_count: int = Field(0, ge=0, description="会话数量")
    total_messages: int = Field(0, ge=0, description="总消息数")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    last_active: Optional[datetime] = Field(None, description="最后活跃时间")
    profile_summary: Optional[str] = Field(None, description="档案摘要")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SessionHistoryRequest(BaseModel):
    """会话历史请求模型"""
    session_id: str = Field(..., description="会话ID")
    limit: int = Field(20, ge=1, le=100, description="限制数量")
    offset: int = Field(0, ge=0, description="偏移量")
    include_emotions: bool = Field(True, description="是否包含情绪信息")


class SessionHistoryResponse(BaseResponse):
    """会话历史响应模型"""
    session_id: str = Field(..., description="会话ID")
    messages: List[ChatMessage] = Field(..., description="消息列表")
    total: int = Field(..., description="总消息数")
    pagination: Optional[PaginationResponse] = Field(None, description="分页信息")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "获取会话历史成功",
                "session_id": "session456",
                "messages": [
                    {
                        "id": "msg1",
                        "role": "user",
                        "content": "我最近总是失眠",
                        "emotion": "焦虑",
                        "emotion_intensity": 7.5,
                        "timestamp": "2025-10-16T14:30:00Z"
                    },
                    {
                        "id": "msg2",
                        "role": "assistant",
                        "content": "我理解你的困扰...",
                        "timestamp": "2025-10-16T14:30:05Z"
                    }
                ],
                "total": 2,
                "timestamp": "2025-10-16T14:30:10Z",
                "status_code": 200
            }
        }


class UserSessionsRequest(BaseModel):
    """用户会话列表请求模型"""
    user_id: str = Field(..., description="用户ID")
    pagination: PaginationRequest = Field(default_factory=PaginationRequest, description="分页参数")
    include_inactive: bool = Field(False, description="是否包含非活跃会话")


class UserSessionsResponse(BaseResponse):
    """用户会话列表响应模型"""
    user_id: str = Field(..., description="用户ID")
    sessions: List[SessionInfo] = Field(..., description="会话列表")
    pagination: PaginationResponse = Field(..., description="分页信息")


class EmotionTrendRequest(BaseModel):
    """情绪趋势请求模型"""
    user_id: str = Field(..., description="用户ID")
    days: int = Field(7, ge=1, le=30, description="统计天数")
    include_intensity: bool = Field(True, description="是否包含强度信息")


class EmotionTrendResponse(BaseResponse):
    """情绪趋势响应模型"""
    user_id: str = Field(..., description="用户ID")
    time_range: str = Field(..., description="时间范围")
    emotion_distribution: Dict[str, int] = Field(..., description="情绪分布")
    trend_data: List[Dict[str, Any]] = Field(..., description="趋势数据")
    summary: Optional[Dict[str, Any]] = Field(None, description="趋势摘要")


class SessionSummaryRequest(BaseModel):
    """会话摘要请求模型"""
    session_id: str = Field(..., description="会话ID")
    include_emotions: bool = Field(True, description="是否包含情绪摘要")
    include_keywords: bool = Field(True, description="是否包含关键词")


class SessionSummaryResponse(BaseResponse):
    """会话摘要响应模型"""
    session_id: str = Field(..., description="会话ID")
    summary: str = Field(..., description="会话摘要")
    key_topics: List[str] = Field(..., description="主要话题")
    emotion_summary: Optional[Dict[str, Any]] = Field(None, description="情绪摘要")
    message_count: int = Field(..., description="消息数量")
    duration: Optional[str] = Field(None, description="会话时长")


class BatchChatRequest(BaseModel):
    """批量聊天请求模型"""
    messages: List[ChatRequest] = Field(..., description="聊天请求列表")
    batch_options: Optional[Dict[str, Any]] = Field(None, description="批量处理选项")
    
    @validator('messages')
    def validate_messages(cls, v):
        if not v:
            raise ValueError('消息列表不能为空')
        if len(v) > 10:
            raise ValueError('批量消息不能超过10条')
        return v


class BatchChatResponse(BaseResponse):
    """批量聊天响应模型"""
    responses: List[ChatResponse] = Field(..., description="响应列表")
    total_processed: int = Field(..., description="处理总数")
    successful: int = Field(..., description="成功数量")
    failed: int = Field(..., description="失败数量")
    processing_time: float = Field(..., description="处理时间（秒）")
