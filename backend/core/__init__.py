"""
核心模块
包含系统的核心组件和基础设施
"""

from .config import Config, get_config
from .exceptions import (
    EmotionalChatException,
    ConfigurationError,
    DatabaseError,
    RAGError,
    ValidationError
)
from .interfaces import (
    IChatEngine,
    IMemoryService,
    IContextService,
    IEmotionAnalyzer,
    IRAGService
)

__all__ = [
    "Config",
    "get_config",
    "EmotionalChatException",
    "ConfigurationError", 
    "DatabaseError",
    "RAGError",
    "ValidationError",
    "IChatEngine",
    "IMemoryService",
    "IContextService",
    "IEmotionAnalyzer",
    "IRAGService"
]
