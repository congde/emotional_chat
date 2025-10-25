#!/usr/bin/env python3
"""
性能优化配置
定义性能优化相关的配置参数
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path

class PerformanceConfig:
    """性能优化配置类"""
    
    # Redis配置
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    REDIS_MAX_CONNECTIONS = int(os.getenv("REDIS_MAX_CONNECTIONS", "100"))
    REDIS_RETRY_ON_TIMEOUT = True
    
    # 缓存配置
    CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_DEFAULT_TTL = int(os.getenv("CACHE_DEFAULT_TTL", "3600"))  # 1小时
    CACHE_EMOTION_TTL = int(os.getenv("CACHE_EMOTION_TTL", "1800"))  # 30分钟
    CACHE_MEMORY_TTL = int(os.getenv("CACHE_MEMORY_TTL", "3600"))  # 1小时
    CACHE_PROMPT_TTL = int(os.getenv("CACHE_PROMPT_TTL", "1800"))  # 30分钟
    
    # 并发配置
    MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "50"))
    THREAD_POOL_MAX_WORKERS = int(os.getenv("THREAD_POOL_MAX_WORKERS", "10"))
    ASYNC_TASK_QUEUE_SIZE = int(os.getenv("ASYNC_TASK_QUEUE_SIZE", "1000"))
    
    # 超时配置
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))  # 30秒
    LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "20"))  # 20秒
    VECTOR_SEARCH_TIMEOUT = int(os.getenv("VECTOR_SEARCH_TIMEOUT", "5"))  # 5秒
    DATABASE_TIMEOUT = int(os.getenv("DATABASE_TIMEOUT", "10"))  # 10秒
    
    # 流式响应配置
    STREAMING_ENABLED = os.getenv("STREAMING_ENABLED", "true").lower() == "true"
    STREAM_CHUNK_SIZE = int(os.getenv("STREAM_CHUNK_SIZE", "1024"))
    STREAM_BUFFER_SIZE = int(os.getenv("STREAM_BUFFER_SIZE", "8192"))
    
    # 性能监控配置
    METRICS_ENABLED = os.getenv("METRICS_ENABLED", "true").lower() == "true"
    METRICS_INTERVAL = int(os.getenv("METRICS_INTERVAL", "60"))  # 60秒
    HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", "30"))  # 30秒
    
    # 降级策略配置
    FALLBACK_ENABLED = os.getenv("FALLBACK_ENABLED", "true").lower() == "true"
    FALLBACK_RESPONSE_DELAY = int(os.getenv("FALLBACK_RESPONSE_DELAY", "1"))  # 1秒
    
    # 数据库连接池配置
    DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "20"))
    DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "30"))
    DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))  # 1小时
    
    # 向量数据库配置
    VECTOR_BATCH_SIZE = int(os.getenv("VECTOR_BATCH_SIZE", "100"))
    VECTOR_INDEX_TYPE = os.getenv("VECTOR_INDEX_TYPE", "HNSW")
    VECTOR_METRIC = os.getenv("VECTOR_METRIC", "cosine")
    
    # 日志配置
    PERFORMANCE_LOG_LEVEL = os.getenv("PERFORMANCE_LOG_LEVEL", "INFO")
    LOG_SLOW_QUERIES = os.getenv("LOG_SLOW_QUERIES", "true").lower() == "true"
    SLOW_QUERY_THRESHOLD = float(os.getenv("SLOW_QUERY_THRESHOLD", "1.0"))  # 1秒
    
    @classmethod
    def get_cache_config(cls) -> Dict[str, Any]:
        """获取缓存配置"""
        return {
            "enabled": cls.CACHE_ENABLED,
            "default_ttl": cls.CACHE_DEFAULT_TTL,
            "emotion_ttl": cls.CACHE_EMOTION_TTL,
            "memory_ttl": cls.CACHE_MEMORY_TTL,
            "prompt_ttl": cls.CACHE_PROMPT_TTL,
            "redis_url": cls.REDIS_URL,
            "max_connections": cls.REDIS_MAX_CONNECTIONS
        }
    
    @classmethod
    def get_concurrency_config(cls) -> Dict[str, Any]:
        """获取并发配置"""
        return {
            "max_concurrent_requests": cls.MAX_CONCURRENT_REQUESTS,
            "thread_pool_max_workers": cls.THREAD_POOL_MAX_WORKERS,
            "async_task_queue_size": cls.ASYNC_TASK_QUEUE_SIZE
        }
    
    @classmethod
    def get_timeout_config(cls) -> Dict[str, Any]:
        """获取超时配置"""
        return {
            "request_timeout": cls.REQUEST_TIMEOUT,
            "llm_timeout": cls.LLM_TIMEOUT,
            "vector_search_timeout": cls.VECTOR_SEARCH_TIMEOUT,
            "database_timeout": cls.DATABASE_TIMEOUT
        }
    
    @classmethod
    def get_streaming_config(cls) -> Dict[str, Any]:
        """获取流式配置"""
        return {
            "enabled": cls.STREAMING_ENABLED,
            "chunk_size": cls.STREAM_CHUNK_SIZE,
            "buffer_size": cls.STREAM_BUFFER_SIZE
        }
    
    @classmethod
    def get_monitoring_config(cls) -> Dict[str, Any]:
        """获取监控配置"""
        return {
            "metrics_enabled": cls.METRICS_ENABLED,
            "metrics_interval": cls.METRICS_INTERVAL,
            "health_check_interval": cls.HEALTH_CHECK_INTERVAL,
            "log_slow_queries": cls.LOG_SLOW_QUERIES,
            "slow_query_threshold": cls.SLOW_QUERY_THRESHOLD
        }
    
    @classmethod
    def get_database_config(cls) -> Dict[str, Any]:
        """获取数据库配置"""
        return {
            "pool_size": cls.DB_POOL_SIZE,
            "max_overflow": cls.DB_MAX_OVERFLOW,
            "pool_timeout": cls.DB_POOL_TIMEOUT,
            "pool_recycle": cls.DB_POOL_RECYCLE
        }
    
    @classmethod
    def get_vector_config(cls) -> Dict[str, Any]:
        """获取向量数据库配置"""
        return {
            "batch_size": cls.VECTOR_BATCH_SIZE,
            "index_type": cls.VECTOR_INDEX_TYPE,
            "metric": cls.VECTOR_METRIC
        }
    
    @classmethod
    def get_all_config(cls) -> Dict[str, Any]:
        """获取所有配置"""
        return {
            "cache": cls.get_cache_config(),
            "concurrency": cls.get_concurrency_config(),
            "timeout": cls.get_timeout_config(),
            "streaming": cls.get_streaming_config(),
            "monitoring": cls.get_monitoring_config(),
            "database": cls.get_database_config(),
            "vector": cls.get_vector_config(),
            "fallback": {
                "enabled": cls.FALLBACK_ENABLED,
                "response_delay": cls.FALLBACK_RESPONSE_DELAY
            }
        }
    
    @classmethod
    def validate_config(cls) -> bool:
        """验证配置有效性"""
        try:
            # 检查必要的配置
            assert cls.REDIS_URL, "Redis URL不能为空"
            assert cls.MAX_CONCURRENT_REQUESTS > 0, "最大并发请求数必须大于0"
            assert cls.THREAD_POOL_MAX_WORKERS > 0, "线程池最大工作线程数必须大于0"
            assert cls.REQUEST_TIMEOUT > 0, "请求超时时间必须大于0"
            assert cls.CACHE_DEFAULT_TTL > 0, "缓存默认TTL必须大于0"
            
            return True
        except AssertionError as e:
            print(f"配置验证失败: {e}")
            return False
        except Exception as e:
            print(f"配置验证出错: {e}")
            return False


# 全局配置实例
performance_config = PerformanceConfig()

# 验证配置
if not performance_config.validate_config():
    print("警告: 性能配置验证失败，使用默认配置")
