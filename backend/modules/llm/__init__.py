"""
LLM模块
大语言模型调用相关功能
"""

from .core.llm_core import SimpleEmotionalChatEngine
# from .services.llm_service import LLMService  # LLMService依赖LLMCore，暂时禁用
from .models.llm_models import LLMRequest, LLMResponse, LLMProvider
from .providers.openai_provider import OpenAIProvider

__all__ = [
    "SimpleEmotionalChatEngine",
    # "LLMService",  # 暂时禁用
    "LLMRequest",
    "LLMResponse",
    "LLMProvider",
    "OpenAIProvider"
]

# 可选的提供商
try:
    from .providers.anthropic_provider import AnthropicProvider
    __all__.append("AnthropicProvider")
except ImportError:
    pass
