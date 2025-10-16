#!/usr/bin/env python3
"""
Anthropic提供商实现
"""

from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime

import anthropic

from .base_provider import BaseLLMProvider
from ..models.llm_models import (
    LLMResponse,
    CompletionResponse,
    ChatMessage,
    LLMUsage,
    LLMProvider
)


class AnthropicProvider(BaseLLMProvider):
    """Anthropic提供商"""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """
        初始化Anthropic提供商
        
        Args:
            api_key: Anthropic API密钥
            base_url: API基础URL
        """
        super().__init__(api_key, base_url)
        
        self.client = anthropic.AsyncAnthropic(
            api_key=api_key,
            base_url=base_url
        )
        
        self.provider = LLMProvider.ANTHROPIC
    
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
        """
        try:
            # 转换消息格式（Anthropic使用不同的格式）
            system_message = None
            user_messages = []
            
            for msg in messages:
                if msg.role.value == "system":
                    system_message = msg.content
                else:
                    user_messages.append({
                        "role": "user" if msg.role.value == "user" else "assistant",
                        "content": msg.content
                    })
            
            # 构建请求参数
            request_params = {
                "model": model,
                "messages": user_messages,
                "temperature": temperature,
                "max_tokens": max_tokens or 4000,
                **kwargs
            }
            
            if system_message:
                request_params["system"] = system_message
            
            # 调用Anthropic API
            start_time = datetime.now()
            response = await self.client.messages.create(**request_params)
            response_time = (datetime.now() - start_time).total_seconds()
            
            # 解析响应
            content = response.content[0].text if response.content else ""
            
            return LLMResponse(
                content=content,
                model=response.model,
                provider=self.provider,
                usage=self._parse_anthropic_usage(response.usage),
                finish_reason=response.stop_reason or "unknown",
                response_time=response_time,
                metadata={
                    "id": response.id,
                    "type": response.type,
                    "role": response.role
                }
            )
            
        except Exception as e:
            raise self._create_error("anthropic_api_error", str(e))
    
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
        """
        try:
            # 转换消息格式
            system_message = None
            user_messages = []
            
            for msg in messages:
                if msg.role.value == "system":
                    system_message = msg.content
                else:
                    user_messages.append({
                        "role": "user" if msg.role.value == "user" else "assistant",
                        "content": msg.content
                    })
            
            # 构建请求参数
            request_params = {
                "model": model,
                "messages": user_messages,
                "temperature": temperature,
                "max_tokens": max_tokens or 4000,
                "stream": True,
                **kwargs
            }
            
            if system_message:
                request_params["system"] = system_message
            
            # 流式调用
            async with self.client.messages.stream(**request_params) as stream:
                async for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            raise self._create_error("anthropic_stream_error", str(e))
    
    async def text_completion(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> CompletionResponse:
        """
        文本补全（Anthropic主要支持聊天格式，这里转换为聊天格式）
        """
        try:
            # 将文本补全转换为聊天格式
            messages = [
                ChatMessage(role="user", content=prompt)
            ]
            
            response = await self.chat_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            # 转换为补全响应格式
            return CompletionResponse(
                text=response.content,
                model=response.model,
                provider=response.provider,
                usage=response.usage,
                finish_reason=response.finish_reason,
                response_time=response.response_time
            )
            
        except Exception as e:
            raise self._create_error("anthropic_completion_error", str(e))
    
    async def list_models(self) -> List[str]:
        """
        获取可用模型列表
        """
        # Anthropic的常用模型
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
    
    async def get_model_info(self, model: str) -> Dict[str, Any]:
        """
        获取模型信息
        """
        # 返回基本的模型信息
        return {
            "id": model,
            "provider": "anthropic",
            "type": "chat",
            "max_tokens": 4096,
            "supports_streaming": True,
            "supports_function_calling": True
        }
    
    def _parse_anthropic_usage(self, usage: Any) -> LLMUsage:
        """
        解析Anthropic使用统计
        """
        if not usage:
            return LLMUsage()
        
        return LLMUsage(
            prompt_tokens=getattr(usage, 'input_tokens', 0),
            completion_tokens=getattr(usage, 'output_tokens', 0),
            total_tokens=getattr(usage, 'input_tokens', 0) + getattr(usage, 'output_tokens', 0),
            prompt_cost=0.0,  # 需要根据模型计算
            completion_cost=0.0,  # 需要根据模型计算
            total_cost=0.0  # 需要根据模型计算
        )
