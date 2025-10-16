#!/usr/bin/env python3
"""
装饰器模块
包含各种实用的装饰器
"""

import time
import asyncio
import functools
import logging
from typing import Any, Callable, Dict, Optional, Union, List
from collections import defaultdict
from datetime import datetime, timedelta
import hashlib
import json

from ..exceptions import RateLimitError, ValidationError


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """重试装饰器"""
    def decorator(func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                last_exception = None
                current_delay = delay
                
                for attempt in range(max_attempts):
                    try:
                        return await func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        if attempt == max_attempts - 1:
                            raise e
                        
                        logging.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                            f"Retrying in {current_delay} seconds..."
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                
                raise last_exception
            
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                last_exception = None
                current_delay = delay
                
                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        if attempt == max_attempts - 1:
                            raise e
                        
                        logging.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                            f"Retrying in {current_delay} seconds..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                
                raise last_exception
            
            return sync_wrapper
    
    return decorator


class RateLimiter:
    """速率限制器"""
    
    def __init__(self):
        self._requests: Dict[str, List[datetime]] = {}
        self._lock = asyncio.Lock()
    
    async def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        time_window: timedelta
    ) -> bool:
        """检查速率限制"""
        async with self._lock:
            now = datetime.now()
            cutoff = now - time_window
            
            # 清理过期记录
            if key in self._requests:
                self._requests[key] = [
                    req_time for req_time in self._requests[key]
                    if req_time > cutoff
                ]
            else:
                self._requests[key] = []
            
            # 检查是否超过限制
            if len(self._requests[key]) >= max_requests:
                return False
            
            # 记录当前请求
            self._requests[key].append(now)
            return True


_global_rate_limiter = RateLimiter()


def rate_limit(
    max_requests: int = 60,
    time_window: int = 60,
    key_func: Optional[Callable] = None
):
    """速率限制装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成限制键
            if key_func:
                limit_key = key_func(*args, **kwargs)
            else:
                # 默认使用函数名
                limit_key = f"{func.__name__}:global"
            
            # 检查速率限制
            allowed = await _global_rate_limiter.check_rate_limit(
                key=limit_key,
                max_requests=max_requests,
                time_window=timedelta(seconds=time_window)
            )
            
            if not allowed:
                retry_after = time_window
                raise RateLimitError(
                    message=f"Rate limit exceeded for {func.__name__}",
                    retry_after=retry_after
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


class CacheManager:
    """缓存管理器"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        async with self._lock:
            if key in self._cache:
                cache_item = self._cache[key]
                if cache_item["expires_at"] > datetime.now():
                    return cache_item["value"]
                else:
                    # 过期，删除
                    del self._cache[key]
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 300):
        """设置缓存"""
        async with self._lock:
            expires_at = datetime.now() + timedelta(seconds=ttl)
            self._cache[key] = {
                "value": value,
                "expires_at": expires_at
            }
    
    async def delete(self, key: str):
        """删除缓存"""
        async with self._lock:
            self._cache.pop(key, None)


_global_cache = CacheManager()


def cache(ttl: int = 300, key_func: Optional[Callable] = None):
    """缓存装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # 默认生成键
                key_data = f"{func.__name__}:{str(args)}:{str(kwargs)}"
                cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # 尝试从缓存获取
            cached_result = await _global_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            await _global_cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


def validate_input(
    max_length: Optional[int] = None,
    min_length: Optional[int] = None,
    allowed_chars: Optional[str] = None,
    forbidden_words: Optional[List[str]] = None
):
    """输入验证装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 查找字符串参数
            for arg in args:
                if isinstance(arg, str):
                    _validate_string(arg, max_length, min_length, allowed_chars, forbidden_words)
            
            for key, value in kwargs.items():
                if isinstance(value, str):
                    _validate_string(value, max_length, min_length, allowed_chars, forbidden_words)
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def _validate_string(
    text: str,
    max_length: Optional[int],
    min_length: Optional[int],
    allowed_chars: Optional[str],
    forbidden_words: Optional[List[str]]
):
    """验证字符串"""
    if min_length and len(text) < min_length:
        raise ValidationError(f"Text too short. Minimum length: {min_length}")
    
    if max_length and len(text) > max_length:
        raise ValidationError(f"Text too long. Maximum length: {max_length}")
    
    if allowed_chars:
        if not all(c in allowed_chars for c in text):
            raise ValidationError(f"Text contains invalid characters. Allowed: {allowed_chars}")
    
    if forbidden_words:
        text_lower = text.lower()
        for word in forbidden_words:
            if word.lower() in text_lower:
                raise ValidationError(f"Forbidden word detected: {word}")


def log_execution(
    log_level: int = logging.INFO,
    include_args: bool = True,
    include_result: bool = True,
    logger: Optional[logging.Logger] = None
):
    """执行日志装饰器"""
    if logger is None:
        logger = logging.getLogger(__name__)
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            
            # 记录开始
            log_data = {
                "function": func.__name__,
                "started_at": datetime.now().isoformat()
            }
            
            if include_args:
                log_data["args"] = str(args)[:200]  # 限制长度
                log_data["kwargs"] = str(kwargs)[:200]
            
            logger.log(log_level, f"Function {func.__name__} started", extra=log_data)
            
            try:
                result = await func(*args, **kwargs)
                
                # 记录成功
                execution_time = time.time() - start_time
                log_data.update({
                    "execution_time": execution_time,
                    "status": "success"
                })
                
                if include_result:
                    log_data["result"] = str(result)[:200]
                
                logger.log(log_level, f"Function {func.__name__} completed", extra=log_data)
                
                return result
                
            except Exception as e:
                # 记录错误
                execution_time = time.time() - start_time
                log_data.update({
                    "execution_time": execution_time,
                    "status": "error",
                    "error": str(e)
                })
                
                logger.error(f"Function {func.__name__} failed", extra=log_data)
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            
            # 记录开始
            log_data = {
                "function": func.__name__,
                "started_at": datetime.now().isoformat()
            }
            
            if include_args:
                log_data["args"] = str(args)[:200]
                log_data["kwargs"] = str(kwargs)[:200]
            
            logger.log(log_level, f"Function {func.__name__} started", extra=log_data)
            
            try:
                result = func(*args, **kwargs)
                
                # 记录成功
                execution_time = time.time() - start_time
                log_data.update({
                    "execution_time": execution_time,
                    "status": "success"
                })
                
                if include_result:
                    log_data["result"] = str(result)[:200]
                
                logger.log(log_level, f"Function {func.__name__} completed", extra=log_data)
                
                return result
                
            except Exception as e:
                # 记录错误
                execution_time = time.time() - start_time
                log_data.update({
                    "execution_time": execution_time,
                    "status": "error",
                    "error": str(e)
                })
                
                logger.error(f"Function {func.__name__} failed", extra=log_data)
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


def timeout(seconds: float):
    """超时装饰器"""
    def decorator(func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                    return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
                except asyncio.TimeoutError:
                    raise TimeoutError(f"Function {func.__name__} timed out after {seconds} seconds")
            
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                # 对于同步函数，使用线程池
                import concurrent.futures
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(func, *args, **kwargs)
                    try:
                        return future.result(timeout=seconds)
                    except concurrent.futures.TimeoutError:
                        raise TimeoutError(f"Function {func.__name__} timed out after {seconds} seconds")
            
            return sync_wrapper
    
    return decorator


def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    expected_exception: type = Exception
):
    """熔断器装饰器"""
    class CircuitBreaker:
        def __init__(self):
            self.failure_count = 0
            self.last_failure_time = None
            self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        
        def can_execute(self) -> bool:
            if self.state == "CLOSED":
                return True
            elif self.state == "OPEN":
                if time.time() - self.last_failure_time > recovery_timeout:
                    self.state = "HALF_OPEN"
                    return True
                return False
            else:  # HALF_OPEN
                return True
        
        def on_success(self):
            self.failure_count = 0
            self.state = "CLOSED"
        
        def on_failure(self):
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= failure_threshold:
                self.state = "OPEN"
    
    breaker = CircuitBreaker()
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not breaker.can_execute():
                raise Exception(f"Circuit breaker is OPEN for {func.__name__}")
            
            try:
                result = await func(*args, **kwargs)
                breaker.on_success()
                return result
            except expected_exception as e:
                breaker.on_failure()
                raise e
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not breaker.can_execute():
                raise Exception(f"Circuit breaker is OPEN for {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                breaker.on_success()
                return result
            except expected_exception as e:
                breaker.on_failure()
                raise e
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator
