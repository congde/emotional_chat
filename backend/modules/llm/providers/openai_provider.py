#!/usr/bin/env python3
"""
OpenAI提供商实现
"""

import json
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime

import openai
from openai import AsyncOpenAI

from .base_provider import BaseLLMProvider
from ..models.llm_models import (
    LLMRequest,
    LLMResponse,
    CompletionRequest,
    CompletionResponse,
    ChatMessage,
    LLMUsage,
    LLMProvider
)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI提供商"""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """
        初始化OpenAI提供商
        
        Args:
            api_key: OpenAI API密钥
            base_url: API基础URL
        """
        super().__init__(api_key, base_url)
        
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url or "https://api.openai.com/v1"
        )
        
        self.provider = LLMProvider.OPENAI
    
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
            # 转换消息格式
            openai_messages = []
            for msg in messages:
                openai_msg = {
                    "role": msg.role.value,
                    "content": msg.content
                }
                if msg.name:
                    openai_msg["name"] = msg.name
                if msg.function_call:
                    openai_msg["function_call"] = msg.function_call
                if msg.tool_calls:
                    openai_msg["tool_calls"] = msg.tool_calls
                
                openai_messages.append(openai_msg)
            
            # 构建请求参数
            request_params = {
                "model": model,
                "messages": openai_messages,
                "temperature": temperature,
                **kwargs
            }
            
            if max_tokens:
                request_params["max_tokens"] = max_tokens
            
            # 调用OpenAI API
            start_time = datetime.now()
            response = await self.client.chat.completions.create(**request_params)
            response_time = (datetime.now() - start_time).total_seconds()
            
            # 解析响应
            choice = response.choices[0]
            message = choice.message
            
            return LLMResponse(
                content=message.content or "",
                model=response.model,
                provider=self.provider,
                usage=self._parse_openai_usage(response.usage),
                finish_reason=choice.finish_reason or "unknown",
                response_time=response_time,
                metadata={
                    "id": response.id,
                    "object": response.object,
                    "created": response.created
                }
            )
            
        except Exception as e:
            raise self._create_error("openai_api_error", str(e))
    
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
            openai_messages = []
            for msg in messages:
                openai_msg = {
                    "role": msg.role.value,
                    "content": msg.content
                }
                if msg.name:
                    openai_msg["name"] = msg.name
                
                openai_messages.append(openai_msg)
            
            # 构建请求参数
            request_params = {
                "model": model,
                "messages": openai_messages,
                "temperature": temperature,
                "stream": True,
                **kwargs
            }
            
            if max_tokens:
                request_params["max_tokens"] = max_tokens
            
            # 流式调用
            stream = await self.client.chat.completions.create(**request_params)
            
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            raise self._create_error("openai_stream_error", str(e))
    
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
        """
        try:
            # 构建请求参数
            request_params = {
                "model": model,
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
                **kwargs
            }
            
            # 调用OpenAI API
            start_time = datetime.now()
            response = await self.client.completions.create(**request_params)
            response_time = (datetime.now() - start_time).total_seconds()
            
            # 解析响应
            choice = response.choices[0]
            
            return CompletionResponse(
                text=choice.text,
                model=response.model,
                provider=self.provider,
                usage=self._parse_openai_usage(response.usage),
                finish_reason=choice.finish_reason or "unknown",
                response_time=response_time
            )
            
        except Exception as e:
            raise self._create_error("openai_completion_error", str(e))
    
    async def list_models(self) -> List[str]:
        """
        获取可用模型列表
        """
        try:
            models = await self.client.models.list()
            return [model.id for model in models.data if model.id.startswith(('gpt-', 'text-'))]
        except Exception as e:
            raise self._create_error("openai_models_error", str(e))
    
    async def get_model_info(self, model: str) -> Dict[str, Any]:
        """
        获取模型信息
        """
        try:
            model_obj = await self.client.models.retrieve(model)
            return {
                "id": model_obj.id,
                "object": model_obj.object,
                "created": model_obj.created,
                "owned_by": model_obj.owned_by,
                "permission": model_obj.permission,
                "root": model_obj.root,
                "parent": model_obj.parent
            }
        except Exception as e:
            raise self._create_error("openai_model_info_error", str(e))
    
    def _parse_openai_usage(self, usage: Any) -> LLMUsage:
        """
        解析OpenAI使用统计
        """
        if not usage:
            return LLMUsage()
        
        return LLMUsage(
            prompt_tokens=getattr(usage, 'prompt_tokens', 0),
            completion_tokens=getattr(usage, 'completion_tokens', 0),
            total_tokens=getattr(usage, 'total_tokens', 0),
            prompt_cost=0.0,  # 需要根据模型计算
            completion_cost=0.0,  # 需要根据模型计算
            total_cost=0.0  # 需要根据模型计算
        )
