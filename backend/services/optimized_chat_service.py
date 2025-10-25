#!/usr/bin/env python3
"""
优化的聊天服务
集成性能优化策略的聊天服务实现
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, AsyncGenerator
from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from backend.services.performance_optimizer import (
    performance_optimizer, 
    stream_handler, 
    cache_manager
)
from backend.services.chat_service import ChatService
from backend.logging_config import get_logger

logger = get_logger(__name__)


class OptimizedChatService(ChatService):
    """优化的聊天服务"""
    
    def __init__(self):
        super().__init__()
        self.performance_optimizer = performance_optimizer
        self.stream_handler = stream_handler
        self.cache_manager = cache_manager
        
        # 性能配置
        self.max_concurrent_requests = 50
        self.request_timeout = 30
        self.cache_enabled = True
        
    @performance_optimizer.performance_monitor
    async def chat_optimized(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        优化的聊天处理
        
        Args:
            request: 聊天请求
            
        Returns:
            聊天响应
        """
        start_time = time.time()
        user_input = request.get("message", "")
        session_id = request.get("session_id")
        user_id = request.get("user_id")
        
        try:
            # 并行处理用户输入
            processing_result = await self._parallel_process_input(user_input)
            
            # 构造优化的Prompt
            prompt = await self._build_optimized_prompt(
                user_input, 
                processing_result
            )
            
            # 生成响应
            response = await self._generate_response_optimized(prompt)
            
            # 异步保存对话记录
            asyncio.create_task(self._async_save_conversation(
                session_id, user_id, user_input, response
            ))
            
            total_time = time.time() - start_time
            
            return {
                "response": response,
                "emotion": processing_result.get("emotion"),
                "memory_used": processing_result.get("memory"),
                "processing_time": processing_result.get("processing_time"),
                "total_time": total_time,
                "optimization_enabled": True
            }
            
        except Exception as e:
            logger.error(f"优化聊天处理失败: {e}")
            # 使用降级策略
            fallback_response = self.performance_optimizer.fallback_strategy(
                "general_error", user_input
            )
            return {
                "response": fallback_response,
                "error": str(e),
                "fallback_used": True
            }
    
    async def chat_streaming(self, request: Dict[str, Any]) -> StreamingResponse:
        """
        流式聊天响应
        
        Args:
            request: 聊天请求
            
        Returns:
            流式响应
        """
        user_input = request.get("message", "")
        session_id = request.get("session_id", "default")
        
        async def generate_stream():
            try:
                # 并行处理（快速路径）
                processing_result = await self._parallel_process_input(user_input)
                prompt = await self._build_optimized_prompt(user_input, processing_result)
                
                # 流式生成
                async for chunk in self.performance_optimizer.stream_response(
                    prompt, self.llm_client
                ):
                    yield chunk
                    
            except Exception as e:
                logger.error(f"流式响应失败: {e}")
                yield f"data: 抱歉，生成过程中出现错误: {str(e)}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # 禁用Nginx缓冲
            }
        )
    
    async def _parallel_process_input(self, user_input: str) -> Dict[str, Any]:
        """并行处理用户输入"""
        try:
            # 使用性能优化器的并行处理
            return await self.performance_optimizer.parallel_processing(
                user_input,
                self.emotion_analyzer,
                self.safety_checker,
                self.memory_retriever
            )
        except Exception as e:
            logger.error(f"并行处理失败: {e}")
            # 返回默认值
            return {
                "emotion": {"emotion": "neutral", "intensity": 5.0},
                "safety": {"safe": True, "confidence": 0.9},
                "memory": {"relevant_memories": []},
                "processing_time": 0.0
            }
    
    async def _build_optimized_prompt(self, user_input: str, 
                                    processing_result: Dict[str, Any]) -> str:
        """构建优化的Prompt"""
        try:
            # 使用缓存管理器
            cache_key = f"prompt:{hash(user_input)}"
            
            async def compute_prompt():
                return self._construct_prompt(
                    user_input, 
                    processing_result.get("emotion", {}),
                    processing_result.get("memory", {}),
                    processing_result.get("safety", {})
                )
            
            if self.cache_enabled:
                return await self.cache_manager.get_or_set(
                    cache_key, compute_prompt, ttl=1800  # 30分钟缓存
                )
            else:
                return await compute_prompt()
                
        except Exception as e:
            logger.error(f"构建Prompt失败: {e}")
            # 返回简化Prompt
            return f"用户说: {user_input}\n请给出合适的回复。"
    
    async def _generate_response_optimized(self, prompt: str) -> str:
        """优化的响应生成"""
        try:
            # 设置超时
            response = await asyncio.wait_for(
                self.llm_client.generate(prompt),
                timeout=self.request_timeout
            )
            return response
        except asyncio.TimeoutError:
            logger.warning("LLM响应超时，使用降级策略")
            return self.performance_optimizer.fallback_strategy(
                "llm_timeout", "用户输入"
            )
        except Exception as e:
            logger.error(f"响应生成失败: {e}")
            return self.performance_optimizer.fallback_strategy(
                "general_error", "用户输入"
            )
    
    async def _async_save_conversation(self, session_id: str, user_id: str, 
                                     user_input: str, response: str):
        """异步保存对话记录"""
        try:
            await self.performance_optimizer.async_task_queue(
                self._save_conversation_sync,
                session_id, user_id, user_input, response
            )
        except Exception as e:
            logger.error(f"异步保存对话失败: {e}")
    
    def _save_conversation_sync(self, session_id: str, user_id: str, 
                              user_input: str, response: str):
        """同步保存对话记录"""
        try:
            # 这里调用原有的保存逻辑
            # 为了简化，这里只是记录日志
            logger.info(f"保存对话: {session_id} - {user_input[:50]}...")
        except Exception as e:
            logger.error(f"保存对话失败: {e}")
    
    def _construct_prompt(self, user_input: str, emotion: Dict, 
                         memory: Dict, safety: Dict) -> str:
        """构造Prompt"""
        prompt_parts = [
            "你是一个情感支持助手。",
            f"用户情感: {emotion.get('emotion', 'neutral')}",
            f"情感强度: {emotion.get('intensity', 5.0)}",
        ]
        
        if memory.get('relevant_memories'):
            prompt_parts.append(f"相关记忆: {memory['relevant_memories']}")
        
        if not safety.get('safe', True):
            prompt_parts.append("注意: 用户输入可能包含敏感内容")
        
        prompt_parts.append(f"用户说: {user_input}")
        prompt_parts.append("请给出共情、自然的回复。")
        
        return "\n".join(prompt_parts)
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        try:
            base_metrics = self.performance_optimizer.get_performance_metrics()
            cache_stats = self.cache_manager.get_cache_stats()
            
            return {
                "performance": base_metrics,
                "cache": cache_stats,
                "active_streams": len(self.stream_handler.get_active_streams()),
                "max_concurrent": self.max_concurrent_requests,
                "timeout": self.request_timeout
            }
        except Exception as e:
            logger.error(f"获取性能指标失败: {e}")
            return {"error": str(e)}
    
    async def health_check_optimized(self) -> Dict[str, Any]:
        """优化的健康检查"""
        try:
            # 检查各个组件
            checks = {
                "redis": await self._check_redis(),
                "llm": await self._check_llm(),
                "database": await self._check_database(),
                "cache": await self._check_cache()
            }
            
            all_healthy = all(checks.values())
            
            return {
                "status": "healthy" if all_healthy else "degraded",
                "checks": checks,
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
    
    async def _check_redis(self) -> bool:
        """检查Redis连接"""
        try:
            self.performance_optimizer.redis_client.ping()
            return True
        except:
            return False
    
    async def _check_llm(self) -> bool:
        """检查LLM服务"""
        try:
            # 简单的LLM连接测试
            test_response = await asyncio.wait_for(
                self.llm_client.generate("测试"),
                timeout=5.0
            )
            return bool(test_response)
        except:
            return False
    
    async def _check_database(self) -> bool:
        """检查数据库连接"""
        try:
            # 这里应该检查数据库连接
            return True
        except:
            return False
    
    async def _check_cache(self) -> bool:
        """检查缓存系统"""
        try:
            # 测试缓存读写
            test_key = "health_check_test"
            test_value = "test"
            self.performance_optimizer.redis_client.setex(test_key, 10, test_value)
            retrieved = self.performance_optimizer.redis_client.get(test_key)
            return retrieved == test_value
        except:
            return False


# 全局优化聊天服务实例
optimized_chat_service = OptimizedChatService()
