#!/usr/bin/env python3
"""
A/B测试分流模块
实现随机分流逻辑，确保用户被稳定分配到实验组
"""

import hashlib
import json
from typing import Dict, Optional, List
from datetime import datetime
from backend.logging_config import get_logger

logger = get_logger(__name__)


class GroupAssigner:
    """
    A/B测试分组分配器
    
    使用一致性哈希确保同一用户始终被分配到同一组
    支持多组实验（A/B/C/D...）
    """
    
    def __init__(self, redis_client=None):
        """
        初始化分组分配器
        
        Args:
            redis_client: Redis客户端（可选），用于持久化分组信息
        """
        self.redis_client = redis_client
        self._cache: Dict[str, str] = {}  # 内存缓存：user_id -> group
    
    def assign_group(
        self,
        user_id: str,
        experiment_id: str,
        groups: List[str] = None,
        weights: List[float] = None,
        use_redis: bool = True
    ) -> str:
        """
        为用户分配实验组
        
        Args:
            user_id: 用户ID
            experiment_id: 实验ID
            groups: 实验组列表，如 ["A", "B"] 或 ["control", "treatment"]
            weights: 各组权重，如 [0.5, 0.5] 表示50/50分流
            use_redis: 是否使用Redis持久化分组信息
        
        Returns:
            分配的组名，如 "A" 或 "B"
        """
        if groups is None:
            groups = ["A", "B"]
        
        if weights is None:
            # 默认均匀分配
            weights = [1.0 / len(groups)] * len(groups)
        
        if len(groups) != len(weights):
            raise ValueError("groups和weights长度必须一致")
        
        # 检查缓存
        cache_key = f"{experiment_id}:{user_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # 检查Redis（如果可用）
        if use_redis and self.redis_client:
            try:
                redis_key = f"ab_test:group:{experiment_id}:{user_id}"
                cached_group = self.redis_client.get(redis_key)
                if cached_group:
                    group = cached_group.decode('utf-8')
                    self._cache[cache_key] = group
                    return group
            except Exception as e:
                logger.warning(f"Redis读取失败，使用内存分配: {e}")
        
        # 使用一致性哈希分配
        group = self._hash_assign(user_id, experiment_id, groups, weights)
        
        # 更新缓存
        self._cache[cache_key] = group
        
        # 持久化到Redis（如果可用）
        if use_redis and self.redis_client:
            try:
                redis_key = f"ab_test:group:{experiment_id}:{user_id}"
                self.redis_client.set(redis_key, group, ex=86400 * 30)  # 30天过期
            except Exception as e:
                logger.warning(f"Redis写入失败: {e}")
        
        logger.info(f"用户 {user_id} 分配到实验 {experiment_id} 的 {group} 组")
        return group
    
    def _hash_assign(
        self,
        user_id: str,
        experiment_id: str,
        groups: List[str],
        weights: List[float]
    ) -> str:
        """
        使用一致性哈希进行分组分配
        
        Args:
            user_id: 用户ID
            experiment_id: 实验ID
            groups: 组列表
            weights: 权重列表
        
        Returns:
            分配的组名
        """
        # 使用用户ID和实验ID生成哈希值
        hash_input = f"{experiment_id}:{user_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        
        # 归一化到0-100范围
        hash_normalized = (hash_value % 10000) / 100.0
        
        # 根据权重分配
        cumulative = 0.0
        for i, (group, weight) in enumerate(zip(groups, weights)):
            cumulative += weight * 100
            if hash_normalized < cumulative:
                return group
        
        # 兜底：返回最后一组
        return groups[-1]
    
    def get_user_group(
        self,
        user_id: str,
        experiment_id: str,
        use_redis: bool = True
    ) -> Optional[str]:
        """
        获取用户已分配的组（不进行新分配）
        
        Args:
            user_id: 用户ID
            experiment_id: 实验ID
            use_redis: 是否从Redis读取
        
        Returns:
            组名，如果未分配则返回None
        """
        cache_key = f"{experiment_id}:{user_id}"
        
        # 检查内存缓存
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # 检查Redis
        if use_redis and self.redis_client:
            try:
                redis_key = f"ab_test:group:{experiment_id}:{user_id}"
                cached_group = self.redis_client.get(redis_key)
                if cached_group:
                    group = cached_group.decode('utf-8')
                    self._cache[cache_key] = group
                    return group
            except Exception as e:
                logger.warning(f"Redis读取失败: {e}")
        
        return None
    
    def clear_cache(self, user_id: str = None, experiment_id: str = None):
        """
        清除缓存
        
        Args:
            user_id: 用户ID（可选），如果提供则只清除该用户的缓存
            experiment_id: 实验ID（可选），如果提供则只清除该实验的缓存
        """
        if user_id and experiment_id:
            cache_key = f"{experiment_id}:{user_id}"
            self._cache.pop(cache_key, None)
            if self.redis_client:
                try:
                    redis_key = f"ab_test:group:{experiment_id}:{user_id}"
                    self.redis_client.delete(redis_key)
                except Exception as e:
                    logger.warning(f"Redis删除失败: {e}")
        else:
            # 清除所有缓存
            self._cache.clear()
            logger.info("已清除所有分组缓存")


# 全局实例（可选）
_global_assigner: Optional[GroupAssigner] = None


def get_group_assigner(redis_client=None) -> GroupAssigner:
    """
    获取全局分组分配器实例
    
    Args:
        redis_client: Redis客户端
    
    Returns:
        GroupAssigner实例
    """
    global _global_assigner
    if _global_assigner is None:
        _global_assigner = GroupAssigner(redis_client)
    return _global_assigner

