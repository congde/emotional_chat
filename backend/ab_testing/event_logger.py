#!/usr/bin/env python3
"""
A/B测试事件日志模块
记录实验过程中的关键事件，用于后续数据分析
"""

import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
from backend.logging_config import get_logger

logger = get_logger(__name__)


class EventType(Enum):
    """事件类型枚举"""
    SESSION_START = "session_start"  # 会话开始
    PROMPT_SENT = "prompt_sent"  # 发送Prompt
    RESPONSE_RECEIVED = "response_received"  # 收到响应
    USER_RATING_SUBMITTED = "user_rating_submitted"  # 用户评分
    SESSION_END = "session_end"  # 会话结束
    CONVERSATION_INTERRUPTED = "conversation_interrupted"  # 对话中断
    FEEDBACK_SUBMITTED = "feedback_submitted"  # 反馈提交


class EventLogger:
    """
    A/B测试事件日志记录器
    
    记录实验过程中的关键事件，支持多种存储后端（文件、数据库、Redis）
    """
    
    def __init__(self, storage_backend: str = "file", **kwargs):
        """
        初始化事件日志记录器
        
        Args:
            storage_backend: 存储后端类型，可选 "file", "database", "redis"
            **kwargs: 存储后端特定配置
                - file: file_path (日志文件路径)
                - database: db_session (数据库会话)
                - redis: redis_client (Redis客户端)
        """
        self.storage_backend = storage_backend
        self.config = kwargs
        
        if storage_backend == "file":
            self.file_path = kwargs.get("file_path", "logs/ab_test_events.jsonl")
            # 确保目录存在
            import os
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        elif storage_backend == "database":
            self.db_session = kwargs.get("db_session")
        elif storage_backend == "redis":
            self.redis_client = kwargs.get("redis_client")
        else:
            raise ValueError(f"不支持的存储后端: {storage_backend}")
    
    def log_event(
        self,
        user_id: str,
        experiment_id: str,
        group: str,
        event_type: EventType,
        data: Dict[str, Any],
        timestamp: Optional[float] = None
    ):
        """
        记录事件
        
        Args:
            user_id: 用户ID
            experiment_id: 实验ID
            group: 实验组（A/B/C等）
            event_type: 事件类型
            data: 事件数据
            timestamp: 时间戳（可选，默认使用当前时间）
        """
        if timestamp is None:
            timestamp = time.time()
        
        event_entry = {
            "user_id": user_id,
            "experiment_id": experiment_id,
            "group": group,
            "event": event_type.value,
            "timestamp": timestamp,
            "datetime": datetime.fromtimestamp(timestamp).isoformat(),
            "data": data
        }
        
        try:
            if self.storage_backend == "file":
                self._log_to_file(event_entry)
            elif self.storage_backend == "database":
                self._log_to_database(event_entry)
            elif self.storage_backend == "redis":
                self._log_to_redis(event_entry)
        except Exception as e:
            logger.error(f"记录事件失败: {e}", exc_info=True)
    
    def _log_to_file(self, event_entry: Dict[str, Any]):
        """记录到文件（JSONL格式）"""
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event_entry, ensure_ascii=False) + "\n")
    
    def _log_to_database(self, event_entry: Dict[str, Any]):
        """记录到数据库"""
        # 这里需要根据实际的数据库模型实现
        # 假设有一个ABTestEvent表
        from backend.database import ABTestEvent
        if self.db_session:
            event = ABTestEvent(
                user_id=event_entry["user_id"],
                experiment_id=event_entry["experiment_id"],
                group=event_entry["group"],
                event_type=event_entry["event"],
                event_data=json.dumps(event_entry["data"], ensure_ascii=False),
                timestamp=datetime.fromtimestamp(event_entry["timestamp"])
            )
            self.db_session.add(event)
            self.db_session.commit()
    
    def _log_to_redis(self, event_entry: Dict[str, Any]):
        """记录到Redis（作为队列）"""
        if self.redis_client:
            key = f"ab_test:events:{event_entry['experiment_id']}"
            self.redis_client.lpush(key, json.dumps(event_entry, ensure_ascii=False))
            # 限制队列长度，避免内存溢出
            self.redis_client.ltrim(key, 0, 10000)
    
    def log_session_start(
        self,
        user_id: str,
        experiment_id: str,
        group: str,
        session_id: str,
        **kwargs
    ):
        """记录会话开始"""
        self.log_event(
            user_id=user_id,
            experiment_id=experiment_id,
            group=group,
            event_type=EventType.SESSION_START,
            data={
                "session_id": session_id,
                **kwargs
            }
        )
    
    def log_response_received(
        self,
        user_id: str,
        experiment_id: str,
        group: str,
        session_id: str,
        user_message: str,
        bot_response: str,
        response_time: float,
        model_used: str,
        prompt_version: Optional[str] = None,
        **kwargs
    ):
        """记录收到响应"""
        self.log_event(
            user_id=user_id,
            experiment_id=experiment_id,
            group=group,
            event_type=EventType.RESPONSE_RECEIVED,
            data={
                "session_id": session_id,
                "user_message": user_message,
                "bot_response": bot_response,
                "response_time": response_time,
                "model_used": model_used,
                "prompt_version": prompt_version,
                **kwargs
            }
        )
    
    def log_user_rating(
        self,
        user_id: str,
        experiment_id: str,
        group: str,
        session_id: str,
        rating: float,
        rating_type: str = "overall",  # overall, empathy, naturalness, safety
        **kwargs
    ):
        """记录用户评分"""
        self.log_event(
            user_id=user_id,
            experiment_id=experiment_id,
            group=group,
            event_type=EventType.USER_RATING_SUBMITTED,
            data={
                "session_id": session_id,
                "rating": rating,
                "rating_type": rating_type,
                **kwargs
            }
        )
    
    def log_conversation_interrupted(
        self,
        user_id: str,
        experiment_id: str,
        group: str,
        session_id: str,
        last_message_count: int,
        **kwargs
    ):
        """记录对话中断（用户不再回复）"""
        self.log_event(
            user_id=user_id,
            experiment_id=experiment_id,
            group=group,
            event_type=EventType.CONVERSATION_INTERRUPTED,
            data={
                "session_id": session_id,
                "last_message_count": last_message_count,
                **kwargs
            }
        )
    
    def log_session_end(
        self,
        user_id: str,
        experiment_id: str,
        group: str,
        session_id: str,
        total_messages: int,
        total_duration: float,
        **kwargs
    ):
        """记录会话结束"""
        self.log_event(
            user_id=user_id,
            experiment_id=experiment_id,
            group=group,
            event_type=EventType.SESSION_END,
            data={
                "session_id": session_id,
                "total_messages": total_messages,
                "total_duration": total_duration,
                **kwargs
            }
        )


# 全局实例（可选）
_global_logger: Optional[EventLogger] = None


def get_event_logger(**kwargs) -> EventLogger:
    """
    获取全局事件日志记录器实例
    
    Args:
        **kwargs: 初始化参数
    
    Returns:
        EventLogger实例
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = EventLogger(**kwargs)
    return _global_logger

