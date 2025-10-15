#!/usr/bin/env python3
"""
上下文服务层
负责组装和管理对话上下文
"""

from typing import Dict, List, Optional, Any
from backend.context_assembler import ContextAssembler, UserProfile
from backend.services.memory_service import MemoryService
from backend.database import DatabaseManager


class ContextService:
    """上下文服务 - 管理对话上下文"""
    
    def __init__(self, memory_service: Optional[MemoryService] = None):
        """初始化上下文服务"""
        self.assembler = ContextAssembler()
        self.memory_service = memory_service or MemoryService()
    
    async def build_context(
        self,
        user_id: str,
        session_id: str,
        current_message: str,
        emotion: Optional[str] = None,
        emotion_intensity: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        构建完整的对话上下文
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            current_message: 当前用户消息
            emotion: 当前情绪
            emotion_intensity: 情绪强度
            
        Returns:
            完整的上下文数据
        """
        # 获取对话历史
        chat_history = await self._get_chat_history(session_id)
        
        # 组装上下文
        context = self.assembler.assemble_context(
            user_id=user_id,
            session_id=session_id,
            current_message=current_message,
            chat_history=chat_history,
            emotion=emotion,
            emotion_intensity=emotion_intensity
        )
        
        return context
    
    async def build_prompt(
        self,
        context: Dict[str, Any],
        system_prompt: str
    ) -> str:
        """
        根据上下文构建完整的prompt
        
        Args:
            context: 上下文数据
            system_prompt: 系统prompt
            
        Returns:
            完整的prompt文本
        """
        return self.assembler.build_prompt_context(context, system_prompt)
    
    async def _get_chat_history(self, session_id: str, limit: int = 10) -> List[Dict[str, str]]:
        """获取对话历史"""
        try:
            with DatabaseManager() as db:
                messages = db.get_session_messages(session_id, limit=limit)
                
                return [
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "emotion": msg.emotion,
                        "timestamp": msg.created_at.isoformat() if msg.created_at else None
                    }
                    for msg in reversed(messages)  # 按时间正序
                ]
        except Exception as e:
            print(f"获取对话历史失败: {e}")
            return []
    
    async def get_user_profile(self, user_id: str) -> UserProfile:
        """
        获取用户画像
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户画像对象
        """
        return self.assembler.get_user_profile(user_id)
    
    async def update_user_profile(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> UserProfile:
        """
        更新用户画像
        
        Args:
            user_id: 用户ID
            updates: 更新的字段
            
        Returns:
            更新后的用户画像
        """
        return self.assembler.update_user_profile(user_id, updates)
    
    async def get_context_summary(self, context: Dict[str, Any]) -> str:
        """
        获取上下文摘要
        
        Args:
            context: 上下文数据
            
        Returns:
            摘要文本
        """
        return self.assembler.generate_context_summary(context)

