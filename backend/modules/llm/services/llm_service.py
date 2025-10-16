#!/usr/bin/env python3
"""
LLM服务层
统一的大语言模型调用服务
"""

import time
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime

from ..core.llm_core import LLMCore
from ..models.llm_models import (
    LLMRequest,
    LLMResponse,
    LLMProvider,
    ChatMessage,
    CompletionRequest,
    CompletionResponse,
    LLMUsage,
    LLMError,
    LLMConfig
)
from backend.core.exceptions import ExternalServiceError
from backend.core.utils.decorators import retry, timeout_async


class LLMService:
    """LLM服务 - 统一的大语言模型调用接口"""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """
        初始化LLM服务
        
        Args:
            config: LLM配置
        """
        self.config = config or LLMConfig(
            api_key="",
            provider=LLMProvider.OPENAI
        )
        self.llm_core = LLMCore(self.config)
        
    async def chat_completion(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
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
        start_time = time.time()
        
        try:
            # 构建请求
            request = LLMRequest(
                messages=messages,
                model=model or self.config.default_model,
                temperature=temperature or self.config.temperature,
                max_tokens=max_tokens or self.config.max_tokens,
                provider=self.config.provider,
                **kwargs
            )
            
            # 调用LLM核心
            response = await self.llm_core.chat_completion(request)
            
            # 计算响应时间
            response_time = time.time() - start_time
            response.response_time = response_time
            
            return response
            
        except Exception as e:
            raise ExternalServiceError(
                message=f"LLM聊天补全失败: {str(e)}",
                service_name="LLM",
                status_code=500
            )
    
    async def text_completion(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
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
        start_time = time.time()
        
        try:
            # 构建请求
            request = CompletionRequest(
                prompt=prompt,
                model=model or self.config.default_model,
                temperature=temperature or self.config.temperature,
                max_tokens=max_tokens or self.config.max_tokens,
                provider=self.config.provider,
                **kwargs
            )
            
            # 调用LLM核心
            response = await self.llm_core.text_completion(request)
            
            # 计算响应时间
            response_time = time.time() - start_time
            response.response_time = response_time
            
            return response
            
        except Exception as e:
            raise ExternalServiceError(
                message=f"LLM文本补全失败: {str(e)}",
                service_name="LLM",
                status_code=500
            )
    
    async def stream_chat_completion(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
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
        try:
            # 构建请求
            request = LLMRequest(
                messages=messages,
                model=model or self.config.default_model,
                temperature=temperature or self.config.temperature,
                max_tokens=max_tokens or self.config.max_tokens,
                provider=self.config.provider,
                stream=True,
                **kwargs
            )
            
            # 流式调用
            async for chunk in self.llm_core.stream_chat_completion(request):
                yield chunk
                
        except Exception as e:
            raise ExternalServiceError(
                message=f"LLM流式聊天补全失败: {str(e)}",
                service_name="LLM",
                status_code=500
            )
    
    async def analyze_emotion(self, text: str) -> Dict[str, Any]:
        """
        情绪分析
        
        Args:
            text: 要分析的文本
            
        Returns:
            情绪分析结果
        """
        try:
            # 构建情绪分析提示
            prompt = f"""
请分析以下文本的情绪状态，返回JSON格式的结果：

文本：{text}

请返回以下格式的JSON：
{{
    "emotion": "主要情绪（如：开心、难过、愤怒、焦虑、平静等）",
    "intensity": 情绪强度（0-10的数字）,
    "confidence": 分析置信度（0-1的数字）,
    "details": {{
        "positive_score": 积极情绪得分（0-1）,
        "negative_score": 消极情绪得分（0-1）,
        "neutral_score": 中性情绪得分（0-1）,
        "keywords": ["提取的关键词1", "关键词2"]
    }}
}}
"""
            
            messages = [
                ChatMessage(role="user", content=prompt)
            ]
            
            response = await self.chat_completion(
                messages=messages,
                temperature=0.3,
                max_tokens=500
            )
            
            # 解析响应
            import json
            try:
                result = json.loads(response.content)
                return result
            except json.JSONDecodeError:
                # 如果JSON解析失败，返回默认结果
                return {
                    "emotion": "neutral",
                    "intensity": 5.0,
                    "confidence": 0.5,
                    "details": {
                        "positive_score": 0.5,
                        "negative_score": 0.5,
                        "neutral_score": 0.5,
                        "keywords": []
                    }
                }
                
        except Exception as e:
            raise ExternalServiceError(
                message=f"情绪分析失败: {str(e)}",
                service_name="LLM",
                status_code=500
            )
    
    async def extract_memories(self, text: str, emotion: str) -> List[Dict[str, Any]]:
        """
        从文本中提取记忆
        
        Args:
            text: 输入文本
            emotion: 情绪信息
            
        Returns:
            提取的记忆列表
        """
        try:
            prompt = f"""
请从以下文本中提取重要的记忆信息，返回JSON格式的结果：

文本：{text}
情绪：{emotion}

请返回以下格式的JSON数组：
[
    {{
        "content": "记忆内容",
        "type": "记忆类型（如：personal, emotional, factual, preference）",
        "importance": 重要性评分（0-1的数字）,
        "keywords": ["关键词1", "关键词2"],
        "emotion": "相关情绪"
    }}
]

只提取真正重要和有价值的记忆，不要提取过于琐碎的信息。
"""
            
            messages = [
                ChatMessage(role="user", content=prompt)
            ]
            
            response = await self.chat_completion(
                messages=messages,
                temperature=0.3,
                max_tokens=800
            )
            
            # 解析响应
            import json
            try:
                memories = json.loads(response.content)
                if not isinstance(memories, list):
                    memories = [memories]
                return memories
            except json.JSONDecodeError:
                return []
                
        except Exception as e:
            raise ExternalServiceError(
                message=f"记忆提取失败: {str(e)}",
                service_name="LLM",
                status_code=500
            )
    
    async def generate_response(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None,
        personality: str = "温暖、共情、专业",
        **kwargs
    ) -> str:
        """
        生成回复
        
        Args:
            user_message: 用户消息
            context: 上下文信息
            personality: 机器人个性
            **kwargs: 其他参数
            
        Returns:
            生成的回复
        """
        try:
            # 构建系统提示
            system_prompt = f"""你是"心语"，一个专业的心理健康陪伴机器人。

个性特点：{personality}

你的职责：
1. 倾听用户的心声，给予温暖的支持
2. 提供专业的心理健康建议
3. 帮助用户管理情绪和压力
4. 鼓励用户积极面对生活

回复要求：
- 用温暖、共情的语气
- 提供具体可操作的建议
- 避免给出医疗诊断
- 鼓励用户寻求专业帮助（如需要）
- 保持回复简洁明了（200字以内）
"""

            # 添加上下文信息
            if context:
                context_info = []
                if context.get("memories"):
                    context_info.append(f"相关记忆：{context['memories']}")
                if context.get("emotion_trend"):
                    context_info.append(f"情绪趋势：{context['emotion_trend']}")
                if context.get("user_profile"):
                    context_info.append(f"用户画像：{context['user_profile']}")
                
                if context_info:
                    system_prompt += f"\n\n当前上下文：\n" + "\n".join(context_info)

            messages = [
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=user_message)
            ]
            
            response = await self.chat_completion(
                messages=messages,
                temperature=0.7,
                max_tokens=500,
                **kwargs
            )
            
            return response.content
            
        except Exception as e:
            raise ExternalServiceError(
                message=f"回复生成失败: {str(e)}",
                service_name="LLM",
                status_code=500
            )
    
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
            
            start_time = time.time()
            response = await self.chat_completion(
                messages=messages,
                max_tokens=10,
                temperature=0.1
            )
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "provider": self.config.provider.value,
                "model": self.config.default_model,
                "response_time": response_time,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "provider": self.config.provider.value,
                "timestamp": datetime.now().isoformat()
            }
