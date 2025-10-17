"""
数据模型和验证器模块
定义API请求/响应的数据模型
"""

from .chat_schemas import (
    ChatRequest,
    ChatResponse,
    ChatMessage,
    SessionInfo,
    UserProfile
)

from .common_schemas import (
    BaseResponse,
    ErrorResponse,
    PaginationRequest,
    PaginationResponse,
    HealthCheckResponse
)

__all__ = [
    # Chat schemas
    "ChatRequest",
    "ChatResponse", 
    "ChatMessage",
    "SessionInfo",
    "UserProfile",
    
    # Common schemas
    "BaseResponse",
    "ErrorResponse",
    "PaginationRequest",
    "PaginationResponse",
    "HealthCheckResponse"
]
