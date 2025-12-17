#!/usr/bin/env python3
"""
A/B测试管理器
统一管理实验配置、分流、日志记录等
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from .group_assigner import GroupAssigner, get_group_assigner
from .event_logger import EventLogger, get_event_logger, EventType
from backend.logging_config import get_logger

logger = get_logger(__name__)


class ABTestConfig:
    """A/B测试配置"""
    
    def __init__(
        self,
        experiment_id: str,
        name: str,
        description: str,
        groups: List[str],
        weights: List[float],
        start_date: datetime,
        end_date: Optional[datetime] = None,
        enabled: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        初始化实验配置
        
        Args:
            experiment_id: 实验ID（唯一标识）
            name: 实验名称
            description: 实验描述
            groups: 实验组列表，如 ["A", "B"]
            weights: 各组权重，如 [0.5, 0.5]
            start_date: 开始时间
            end_date: 结束时间（可选）
            enabled: 是否启用
            metadata: 额外元数据
        """
        self.experiment_id = experiment_id
        self.name = name
        self.description = description
        self.groups = groups
        self.weights = weights
        self.start_date = start_date
        self.end_date = end_date
        self.enabled = enabled
        self.metadata = metadata or {}
        
        # 验证
        if len(groups) != len(weights):
            raise ValueError("groups和weights长度必须一致")
        if abs(sum(weights) - 1.0) > 0.01:
            raise ValueError("weights总和必须等于1.0")
    
    def is_active(self) -> bool:
        """检查实验是否处于活跃状态"""
        now = datetime.now()
        if not self.enabled:
            return False
        if now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "experiment_id": self.experiment_id,
            "name": self.name,
            "description": self.description,
            "groups": self.groups,
            "weights": self.weights,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "enabled": self.enabled,
            "metadata": self.metadata,
            "is_active": self.is_active()
        }


class ABTestManager:
    """
    A/B测试管理器
    
    统一管理多个实验，处理分流、日志记录等
    """
    
    def __init__(self, redis_client=None, event_logger: Optional[EventLogger] = None):
        """
        初始化A/B测试管理器
        
        Args:
            redis_client: Redis客户端（可选）
            event_logger: 事件日志记录器（可选）
        """
        self.group_assigner = get_group_assigner(redis_client)
        self.event_logger = event_logger or get_event_logger()
        self.experiments: Dict[str, ABTestConfig] = {}
    
    def register_experiment(self, config: ABTestConfig):
        """
        注册实验
        
        Args:
            config: 实验配置
        """
        self.experiments[config.experiment_id] = config
        logger.info(f"注册实验: {config.experiment_id} - {config.name}")
    
    def get_experiment(self, experiment_id: str) -> Optional[ABTestConfig]:
        """获取实验配置"""
        return self.experiments.get(experiment_id)
    
    def assign_user_to_group(
        self,
        user_id: str,
        experiment_id: str,
        force_group: Optional[str] = None
    ) -> Optional[str]:
        """
        为用户分配实验组
        
        Args:
            user_id: 用户ID
            experiment_id: 实验ID
            force_group: 强制分配到指定组（用于测试）
        
        Returns:
            分配的组名，如果实验不存在或未激活则返回None
        """
        config = self.get_experiment(experiment_id)
        if not config:
            logger.warning(f"实验不存在: {experiment_id}")
            return None
        
        if not config.is_active():
            logger.warning(f"实验未激活: {experiment_id}")
            return None
        
        if force_group:
            # 强制分配（用于测试）
            if force_group in config.groups:
                return force_group
            else:
                logger.warning(f"强制组 {force_group} 不在实验组列表中")
                return None
        
        # 正常分配
        group = self.group_assigner.assign_group(
            user_id=user_id,
            experiment_id=experiment_id,
            groups=config.groups,
            weights=config.weights
        )
        
        # 记录分组事件
        self.event_logger.log_event(
            user_id=user_id,
            experiment_id=experiment_id,
            group=group,
            event_type=EventType.SESSION_START,
            data={"action": "group_assigned"}
        )
        
        return group
    
    def log_response(
        self,
        user_id: str,
        experiment_id: str,
        session_id: str,
        user_message: str,
        bot_response: str,
        response_time: float,
        model_used: str,
        prompt_version: Optional[str] = None
    ):
        """
        记录响应事件
        
        Args:
            user_id: 用户ID
            experiment_id: 实验ID
            session_id: 会话ID
            user_message: 用户消息
            bot_response: 机器人回复
            response_time: 响应时间（秒）
            model_used: 使用的模型
            prompt_version: Prompt版本
        """
        # 获取用户所在组
        group = self.group_assigner.get_user_group(user_id, experiment_id)
        if not group:
            logger.warning(f"用户 {user_id} 未分配到实验 {experiment_id} 的任何组")
            return
        
        self.event_logger.log_response_received(
            user_id=user_id,
            experiment_id=experiment_id,
            group=group,
            session_id=session_id,
            user_message=user_message,
            bot_response=bot_response,
            response_time=response_time,
            model_used=model_used,
            prompt_version=prompt_version
        )
    
    def log_rating(
        self,
        user_id: str,
        experiment_id: str,
        session_id: str,
        rating: float,
        rating_type: str = "overall"
    ):
        """
        记录用户评分
        
        Args:
            user_id: 用户ID
            experiment_id: 实验ID
            session_id: 会话ID
            rating: 评分（1-5）
            rating_type: 评分类型
        """
        group = self.group_assigner.get_user_group(user_id, experiment_id)
        if not group:
            return
        
        self.event_logger.log_user_rating(
            user_id=user_id,
            experiment_id=experiment_id,
            group=group,
            session_id=session_id,
            rating=rating,
            rating_type=rating_type
        )
    
    def get_active_experiments(self) -> List[ABTestConfig]:
        """获取所有活跃的实验"""
        return [config for config in self.experiments.values() if config.is_active()]
    
    def list_experiments(self) -> List[Dict[str, Any]]:
        """列出所有实验"""
        return [config.to_dict() for config in self.experiments.values()]


# 全局实例（可选）
_global_manager: Optional[ABTestManager] = None


def get_ab_test_manager(redis_client=None) -> ABTestManager:
    """
    获取全局A/B测试管理器实例
    
    Args:
        redis_client: Redis客户端
    
    Returns:
        ABTestManager实例
    """
    global _global_manager
    if _global_manager is None:
        _global_manager = ABTestManager(redis_client)
    return _global_manager

