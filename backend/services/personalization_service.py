#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
个性化服务
处理用户个性化配置的获取和应用
"""

import json
import logging
from typing import Dict, Optional, Any
from sqlalchemy.orm import Session

from backend.database import UserPersonalization
from backend.services.prompt_composer import PromptComposer

logger = logging.getLogger(__name__)


class PersonalizationService:
    """
    个性化服务
    负责获取用户配置并生成个性化Prompt
    """
    
    def __init__(self):
        """初始化个性化服务"""
        self._cache = {}  # 简单的内存缓存
    
    def get_user_config(self, user_id: str, db: Session) -> Dict[str, Any]:
        """
        获取用户个性化配置
        
        Args:
            user_id: 用户ID
            db: 数据库会话
        
        Returns:
            用户配置字典
        """
        # 检查缓存
        if user_id in self._cache:
            return self._cache[user_id]
        
        try:
            # 从数据库获取配置
            config_db = db.query(UserPersonalization).filter(
                UserPersonalization.user_id == user_id
            ).first()
            
            if config_db:
                # 转换为字典
                config = self._db_to_dict(config_db)
            else:
                # 使用默认配置
                config = self._get_default_config(user_id)
            
            # 缓存配置
            self._cache[user_id] = config
            
            return config
            
        except Exception as e:
            logger.error(f"获取用户配置失败: {e}")
            return self._get_default_config(user_id)
    
    def _db_to_dict(self, config_db: UserPersonalization) -> Dict[str, Any]:
        """将数据库记录转换为配置字典"""
        return {
            "user_id": config_db.user_id,
            "role": config_db.role,
            "role_name": config_db.role_name,
            "role_background": config_db.role_background,
            "personality": config_db.personality,
            "core_principles": json.loads(config_db.core_principles) if config_db.core_principles else [],
            "forbidden_behaviors": json.loads(config_db.forbidden_behaviors) if config_db.forbidden_behaviors else [],
            "tone": config_db.tone,
            "style": config_db.style,
            "formality": config_db.formality,
            "enthusiasm": config_db.enthusiasm,
            "empathy_level": config_db.empathy_level,
            "humor_level": config_db.humor_level,
            "response_length": config_db.response_length,
            "use_emoji": config_db.use_emoji,
            "preferred_topics": json.loads(config_db.preferred_topics) if config_db.preferred_topics else [],
            "avoided_topics": json.loads(config_db.avoided_topics) if config_db.avoided_topics else [],
            "communication_preferences": json.loads(config_db.communication_preferences) if config_db.communication_preferences else {},
            "learning_mode": config_db.learning_mode,
            "safety_level": config_db.safety_level,
            "context_window": config_db.context_window,
            "situational_roles": json.loads(config_db.situational_roles) if config_db.situational_roles else {},
            "active_role": config_db.active_role
        }
    
    def _get_default_config(self, user_id: str) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "user_id": user_id,
            "role": "温暖倾听者",
            "role_name": "心语",
            "role_background": "我是一个专注于情感支持的AI伙伴，我的使命是倾听你的心声，理解你的感受。",
            "personality": "温暖耐心",
            "core_principles": ["永远不评判用户", "倾听优先于建议", "共情是第一要务"],
            "forbidden_behaviors": [],
            "tone": "温和",
            "style": "简洁",
            "formality": 0.3,
            "enthusiasm": 0.5,
            "empathy_level": 0.8,
            "humor_level": 0.3,
            "response_length": "medium",
            "use_emoji": False,
            "preferred_topics": [],
            "avoided_topics": [],
            "communication_preferences": {},
            "learning_mode": True,
            "safety_level": "standard",
            "context_window": 10,
            "situational_roles": {},
            "active_role": "default"
        }
    
    def create_prompt_composer(
        self,
        user_id: str,
        db: Session
    ) -> PromptComposer:
        """
        为用户创建Prompt组合器
        
        Args:
            user_id: 用户ID
            db: 数据库会话
        
        Returns:
            PromptComposer实例
        """
        config = self.get_user_config(user_id, db)
        return PromptComposer(config)
    
    def generate_personalized_prompt(
        self,
        user_id: str,
        context: str,
        emotion_state: Optional[Dict] = None,
        db: Session = None
    ) -> str:
        """
        生成个性化Prompt
        
        Args:
            user_id: 用户ID
            context: 对话上下文
            emotion_state: 情绪状态
            db: 数据库会话
        
        Returns:
            个性化Prompt文本
        """
        if not db:
            # 如果没有提供db会话，返回基础prompt
            logger.warning("未提供数据库会话，使用默认配置")
            config = self._get_default_config(user_id)
            composer = PromptComposer(config)
        else:
            composer = self.create_prompt_composer(user_id, db)
        
        return composer.compose(context=context, emotion_state=emotion_state)
    
    def clear_cache(self, user_id: Optional[str] = None):
        """
        清除缓存
        
        Args:
            user_id: 如果提供，只清除该用户的缓存；否则清除所有
        """
        if user_id:
            self._cache.pop(user_id, None)
        else:
            self._cache.clear()
    
    def update_config_in_cache(self, user_id: str, config: Dict[str, Any]):
        """
        更新缓存中的配置
        
        Args:
            user_id: 用户ID
            config: 新配置
        """
        self._cache[user_id] = config


# 全局实例（单例模式）
_global_service = None


def get_personalization_service() -> PersonalizationService:
    """
    获取全局个性化服务实例
    
    Returns:
        PersonalizationService实例
    """
    global _global_service
    if _global_service is None:
        _global_service = PersonalizationService()
    return _global_service


# 测试代码
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    service = PersonalizationService()
    
    # 测试默认配置
    print("=" * 60)
    print("测试1: 获取默认配置")
    print("=" * 60)
    default_config = service._get_default_config("test_user")
    print(json.dumps(default_config, ensure_ascii=False, indent=2))
    
    # 测试Prompt生成（不需要数据库）
    print("\n" + "=" * 60)
    print("测试2: 生成默认Prompt")
    print("=" * 60)
    composer = PromptComposer(default_config)
    prompt = composer.compose(
        context="用户说：今天心情不太好",
        emotion_state={
            "emotion": "sad",
            "intensity": 6.5
        }
    )
    print(prompt)











