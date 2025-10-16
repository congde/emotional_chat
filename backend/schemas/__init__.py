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

from .rag_schemas import (
    RAGRequest,
    RAGResponse,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
    DocumentUploadRequest
)

from .memory_schemas import (
    MemoryRequest,
    MemoryResponse,
    MemoryInfo,
    ContextInfo
)

from .evaluation_schemas import (
    EvaluationRequest,
    EvaluationResponse,
    EvaluationResult,
    PerformanceMetrics
)

from .feedback_schemas import (
    FeedbackRequest,
    FeedbackResponse,
    FeedbackInfo,
    FeedbackAnalysis
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
    
    # RAG schemas
    "RAGRequest",
    "RAGResponse",
    "KnowledgeSearchRequest",
    "KnowledgeSearchResponse",
    "DocumentUploadRequest",
    
    # Memory schemas
    "MemoryRequest",
    "MemoryResponse",
    "MemoryInfo",
    "ContextInfo",
    
    # Evaluation schemas
    "EvaluationRequest",
    "EvaluationResponse",
    "EvaluationResult",
    "PerformanceMetrics",
    
    # Feedback schemas
    "FeedbackRequest",
    "FeedbackResponse",
    "FeedbackInfo",
    "FeedbackAnalysis",
    
    # Common schemas
    "BaseResponse",
    "ErrorResponse",
    "PaginationRequest",
    "PaginationResponse",
    "HealthCheckResponse"
]
