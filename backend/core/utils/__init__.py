"""
工具模块
包含各种实用工具和辅助函数
"""

from .dependency_injection import Container, Dependency, Singleton, Transient
from .decorators import retry, rate_limit, cache, validate_input, log_execution
from .validators import (
    validate_email,
    validate_phone,
    validate_text_length,
    validate_session_id,
    validate_user_id
)
from .formatters import (
    format_response,
    format_error,
    format_timestamp,
    format_emotion_result
)
from .helpers import (
    generate_id,
    sanitize_text,
    extract_emotion_keywords,
    calculate_similarity,
    merge_dicts
)

__all__ = [
    # 依赖注入
    "Container",
    "Dependency",
    "Singleton",
    "Transient",
    
    # 装饰器
    "retry",
    "rate_limit",
    "cache",
    "validate_input",
    "log_execution",
    
    # 验证器
    "validate_email",
    "validate_phone",
    "validate_text_length",
    "validate_session_id",
    "validate_user_id",
    
    # 格式化器
    "format_response",
    "format_error",
    "format_timestamp",
    "format_emotion_result",
    
    # 辅助函数
    "generate_id",
    "sanitize_text",
    "extract_emotion_keywords",
    "calculate_similarity",
    "merge_dicts"
]
