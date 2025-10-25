#!/usr/bin/env python3
"""
性能优化服务
实现并行处理、缓存机制、流式响应等性能优化策略
"""

import asyncio
import hashlib
import json
import time
from typing import Dict, List, Optional, Any, AsyncGenerator
from concurrent.futures import ThreadPoolExecutor
import redis
from functools import wraps
import logging

from backend.logging_config import get_logger

logger = get_logger(__name__)


class PerformanceOptimizer:
    """性能优化器"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """
        初始化性能优化器
        
        Args:
            redis_url: Redis连接URL
        """
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
        self.cache_ttl = 3600  # 缓存1小时
        
    def cache_key(self, prefix: str, content: str) -> str:
        """生成缓存键"""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        return f"{prefix}:{content_hash}"
    
    async def parallel_processing(self, user_input: str, 
                                emotion_analyzer, 
                                safety_checker, 
                                memory_retriever) -> Dict[str, Any]:
        """
        并行处理用户输入
        
        Args:
            user_input: 用户输入
            emotion_analyzer: 情感分析器
            safety_checker: 安全检查器
            memory_retriever: 记忆检索器
            
        Returns:
            处理结果字典
        """
        start_time = time.time()
        
        # 并行执行三个独立任务
        loop = asyncio.get_event_loop()
        
        # 检查缓存
        emotion_cache_key = self.cache_key("emotion", user_input)
        safety_cache_key = self.cache_key("safety", user_input)
        memory_cache_key = self.cache_key("memory", user_input)
        
        # 并行获取缓存和计算
        emotion_task = self._get_or_compute(
            emotion_cache_key, 
            lambda: loop.run_in_executor(self.thread_pool, emotion_analyzer.analyze, user_input)
        )
        safety_task = self._get_or_compute(
            safety_cache_key,
            lambda: loop.run_in_executor(self.thread_pool, safety_checker.check, user_input)
        )
        memory_task = self._get_or_compute(
            memory_cache_key,
            lambda: loop.run_in_executor(self.thread_pool, memory_retriever.retrieve, user_input)
        )
        
        # 等待所有任务完成
        emotion_result, safety_result, memory_result = await asyncio.gather(
            emotion_task, safety_task, memory_task
        )
        
        processing_time = time.time() - start_time
        
        return {
            "emotion": emotion_result,
            "safety": safety_result,
            "memory": memory_result,
            "processing_time": processing_time,
            "parallel_optimization": True
        }
    
    async def _get_or_compute(self, cache_key: str, compute_func) -> Any:
        """获取缓存或计算新值"""
        try:
            # 尝试从缓存获取
            cached = self.redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # 缓存未命中，执行计算
            result = await compute_func()
            
            # 缓存结果
            self.redis_client.setex(cache_key, self.cache_ttl, json.dumps(result))
            
            return result
        except Exception as e:
            logger.error(f"缓存操作失败: {e}")
            # 缓存失败时直接计算
            return await compute_func()
    
    async def stream_response(self, prompt: str, llm_client) -> AsyncGenerator[str, None]:
        """
        流式响应生成器
        
        Args:
            prompt: 输入提示
            llm_client: LLM客户端
            
        Yields:
            流式响应块
        """
        try:
            # 使用流式API
            async for chunk in llm_client.stream(prompt):
                if chunk:
                    yield f"data: {chunk}\n\n"
                    await asyncio.sleep(0.01)  # 控制输出速度
            
            # 发送结束信号
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            logger.error(f"流式响应失败: {e}")
            yield f"data: 抱歉，生成过程中出现错误: {str(e)}\n\n"
    
    def fallback_strategy(self, error_type: str, user_input: str) -> str:
        """
        降级策略
        
        Args:
            error_type: 错误类型
            user_input: 用户输入
            
        Returns:
            降级响应
        """
        fallback_responses = {
            "llm_timeout": "抱歉，我现在有点忙，请稍后再试。",
            "memory_timeout": "让我用最近的信息来帮助你。",
            "vector_error": "我会记住你的话，稍后给你更好的回复。",
            "general_error": "我遇到了一些技术问题，但我会尽力帮助你。"
        }
        
        return fallback_responses.get(error_type, fallback_responses["general_error"])
    
    async def async_task_queue(self, task_func, *args, **kwargs):
        """
        异步任务队列
        
        Args:
            task_func: 任务函数
            *args: 位置参数
            **kwargs: 关键字参数
        """
        try:
            # 在后台执行非关键任务
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(self.thread_pool, task_func, *args, **kwargs)
        except Exception as e:
            logger.error(f"异步任务执行失败: {e}")
    
    def performance_monitor(self, func):
        """
        性能监控装饰器
        
        Args:
            func: 被装饰的函数
        """
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # 记录性能指标
                logger.info(f"函数 {func.__name__} 执行时间: {execution_time:.3f}s")
                
                # 如果执行时间过长，记录警告
                if execution_time > 3.0:
                    logger.warning(f"函数 {func.__name__} 执行时间过长: {execution_time:.3f}s")
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"函数 {func.__name__} 执行失败，耗时: {execution_time:.3f}s, 错误: {e}")
                raise
        
        return wrapper
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        try:
            # Redis性能指标
            redis_info = self.redis_client.info()
            
            return {
                "redis_connected_clients": redis_info.get("connected_clients", 0),
                "redis_used_memory": redis_info.get("used_memory_human", "0B"),
                "redis_hit_rate": self._calculate_hit_rate(),
                "thread_pool_active": self.thread_pool._threads,
                "cache_ttl": self.cache_ttl
            }
        except Exception as e:
            logger.error(f"获取性能指标失败: {e}")
            return {"error": str(e)}
    
    def _calculate_hit_rate(self) -> float:
        """计算缓存命中率"""
        try:
            info = self.redis_client.info()
            hits = info.get("keyspace_hits", 0)
            misses = info.get("keyspace_misses", 0)
            total = hits + misses
            return (hits / total * 100) if total > 0 else 0.0
        except:
            return 0.0


class StreamingResponseHandler:
    """流式响应处理器"""
    
    def __init__(self):
        self.active_streams = {}
    
    async def create_stream(self, stream_id: str, generator_func):
        """创建流式响应"""
        self.active_streams[stream_id] = {
            "created_at": time.time(),
            "status": "active"
        }
        
        try:
            async for chunk in generator_func():
                yield chunk
        finally:
            # 清理流
            if stream_id in self.active_streams:
                del self.active_streams[stream_id]
    
    def get_active_streams(self) -> Dict[str, Any]:
        """获取活跃流信息"""
        current_time = time.time()
        active_streams = {}
        
        for stream_id, info in self.active_streams.items():
            if current_time - info["created_at"] < 300:  # 5分钟超时
                active_streams[stream_id] = info
            else:
                # 清理超时流
                del self.active_streams[stream_id]
        
        return active_streams


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.default_ttl = 3600
    
    async def get_or_set(self, key: str, compute_func, ttl: int = None) -> Any:
        """获取或设置缓存"""
        ttl = ttl or self.default_ttl
        
        # 尝试获取缓存
        cached = self.redis.get(key)
        if cached:
            return json.loads(cached)
        
        # 计算新值
        result = await compute_func()
        
        # 设置缓存
        self.redis.setex(key, ttl, json.dumps(result))
        
        return result
    
    def invalidate_pattern(self, pattern: str):
        """按模式清除缓存"""
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        info = self.redis.info()
        return {
            "total_keys": self.redis.dbsize(),
            "memory_usage": info.get("used_memory_human", "0B"),
            "hit_rate": self._calculate_hit_rate(info)
        }
    
    def _calculate_hit_rate(self, info: Dict) -> float:
        """计算命中率"""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0.0


# 全局性能优化器实例
performance_optimizer = PerformanceOptimizer()
stream_handler = StreamingResponseHandler()
cache_manager = CacheManager(performance_optimizer.redis_client)
