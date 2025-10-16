#!/usr/bin/env python3
"""
LLM提供商基类
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime

from ..models.llm_models import (
    LLMRequest,
    LLMResponse,
    CompletionRequest,
    CompletionResponse,
    ChatMessage,
    LLMUsage,
    LLMError
)


class BaseLLMProvider(ABC):
    """LLM提供商基类"""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """
        初始化提供商
        
        Args:
            api_key: API密钥
            base_url: API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def chat_completion(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        聊天补全
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大令牌数
            **kwargs: 其他参数
            
        Returns:
            LLM响应
        """
        pass
    
    @abstractmethod
    async def stream_chat_completion(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        流式聊天补全
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大令牌数
            **kwargs: 其他参数
            
        Yields:
            流式响应文本
        """
        pass
    
    @abstractmethod
    async def text_completion(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> CompletionResponse:
        """
        文本补全
        
        Args:
            prompt: 提示文本
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大令牌数
            **kwargs: 其他参数
            
        Returns:
            补全响应
        """
        pass
    
    @abstractmethod
    async def list_models(self) -> List[str]:
        """
        获取可用模型列表
        
        Returns:
            模型名称列表
        """
        pass
    
    @abstractmethod
    async def get_model_info(self, model: str) -> Dict[str, Any]:
        """
        获取模型信息
        
        Args:
            model: 模型名称
            
        Returns:
            模型信息
        """
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        
        Returns:
            健康状态信息
        """
        try:
            # 发送简单测试请求
            messages = [
                ChatMessage(role="user", content="Hello")
            ]
            
            start_time = datetime.now()
            response = await self.chat_completion(
                messages=messages,
                model="gpt-3.5-turbo",
                max_tokens=10,
                temperature=0.1
            )
            response_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "status": "healthy",
                "provider": self.name,
                "response_time": response_time,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": self.name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _parse_usage(self, usage_data: Dict[str, Any]) -> LLMUsage:
        """
        解析使用统计
        
        Args:
            usage_data: 原始使用数据
            
        Returns:
            使用统计
        """
        return LLMUsage(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0),
            prompt_cost=usage_data.get("prompt_cost", 0.0),
            completion_cost=usage_data.get("completion_cost", 0.0),
            total_cost=usage_data.get("total_cost", 0.0)
        )
    
    def _create_error(self, error_type: str, message: str, details: Optional[Dict[str, Any]] = None) -> LLMError:
        """
        创建错误对象
        
        Args:
            error_type: 错误类型
            message: 错误消息
            details: 错误详情
            
        Returns:
            错误对象
        """
        return LLMError(
            error_type=error_type,
            error_code=error_type.upper(),
            message=message,
            details=details or {}
        )
