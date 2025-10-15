#!/usr/bin/env python3
"""
聊天服务层
处理所有与聊天相关的业务逻辑
"""

from typing import Dict, Optional, Any
from backend.simple_langchain_engine import SimpleEmotionalChatEngine
from backend.services.memory_service import MemoryService
from backend.services.context_service import ContextService
from backend.models import ChatRequest, ChatResponse
from backend.database import DatabaseManager
import uuid
from datetime import datetime


class ChatService:
    """聊天服务 - 统一的聊天接口"""
    
    def __init__(
        self,
        memory_service: Optional[MemoryService] = None,
        context_service: Optional[ContextService] = None
    ):
        """初始化聊天服务"""
        self.chat_engine = SimpleEmotionalChatEngine()
        self.memory_service = memory_service or MemoryService()
        self.context_service = context_service or ContextService(memory_service=self.memory_service)
    
    async def chat(
        self,
        request: ChatRequest,
        use_memory_system: bool = True
    ) -> ChatResponse:
        """
        处理聊天请求（支持记忆系统）
        
        Args:
            request: 聊天请求
            use_memory_system: 是否启用记忆系统
            
        Returns:
            聊天响应
        """
        # 生成会话ID（如果没有）
        if not request.session_id:
            request.session_id = str(uuid.uuid4())
        
        # 如果启用记忆系统
        if use_memory_system:
            return await self._chat_with_memory(request)
        else:
            # 使用原有引擎（无记忆）
            return self.chat_engine.chat(request)
    
    async def _chat_with_memory(self, request: ChatRequest) -> ChatResponse:
        """使用记忆系统的聊天"""
        user_id = request.user_id or "anonymous"
        session_id = request.session_id
        message = request.message
        
        # 1. 分析情绪
        emotion_result = self.chat_engine.emotion_analyzer.analyze_emotion(message)
        emotion = emotion_result.get("emotion", "neutral")
        emotion_intensity = emotion_result.get("intensity", 5.0)
        
        # 2. 构建上下文（包含记忆）
        context = await self.context_service.build_context(
            user_id=user_id,
            session_id=session_id,
            current_message=message,
            emotion=emotion,
            emotion_intensity=emotion_intensity
        )
        
        # 3. 生成回复（使用增强的上下文）
        # 这里可以选择使用原引擎或增强的prompt
        response = self.chat_engine.chat(request)
        
        # 4. 处理并存储记忆
        await self.memory_service.process_and_store_memories(
            session_id=session_id,
            user_id=user_id,
            user_message=message,
            bot_response=response.response,
            emotion=emotion,
            emotion_intensity=emotion_intensity
        )
        
        # 5. 添加上下文信息到响应
        response.context = {
            "memories_count": len(context.get("memories", {}).get("all", [])),
            "emotion_trend": context.get("emotion_context", {}).get("trend", {}).get("trend"),
            "has_profile": bool(context.get("user_profile", {}).get("summary"))
        }
        
        return response
    
    async def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """
        获取会话摘要
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话摘要
        """
        return self.chat_engine.get_session_summary(session_id)
    
    async def get_session_history(
        self,
        session_id: str,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        获取会话历史
        
        Args:
            session_id: 会话ID
            limit: 限制数量
            
        Returns:
            会话历史
        """
        try:
            with DatabaseManager() as db:
                messages = db.get_session_messages(session_id, limit)
                
                if not messages:
                    return {
                        "session_id": session_id,
                        "messages": [],
                        "total": 0
                    }
                
                return {
                    "session_id": session_id,
                    "messages": [
                        {
                            "id": msg.id,
                            "role": msg.role,
                            "content": msg.content,
                            "emotion": msg.emotion,
                            "emotion_intensity": msg.emotion_intensity,
                            "timestamp": msg.created_at.isoformat() if msg.created_at else None
                        }
                        for msg in messages
                    ],
                    "total": len(messages)
                }
        except Exception as e:
            print(f"获取会话历史失败: {e}")
            return {
                "session_id": session_id,
                "messages": [],
                "total": 0,
                "error": str(e)
            }
    
    async def get_user_sessions(
        self,
        user_id: str,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        获取用户的所有会话
        
        Args:
            user_id: 用户ID
            limit: 限制数量
            
        Returns:
            会话列表
        """
        try:
            with DatabaseManager() as db:
                from backend.database import ChatMessage
                
                sessions = db.get_user_sessions(user_id, limit)
                
                session_list = []
                for session in sessions:
                    # 获取会话的第一条消息作为标题
                    first_message = db.db.query(ChatMessage)\
                        .filter(ChatMessage.session_id == session.session_id)\
                        .filter(ChatMessage.role == 'user')\
                        .order_by(ChatMessage.created_at.asc())\
                        .first()
                    
                    title = first_message.content[:30] + "..." if first_message and len(first_message.content) > 30 else (first_message.content if first_message else "新对话")
                    
                    session_list.append({
                        "session_id": session.session_id,
                        "title": title,
                        "created_at": session.created_at.isoformat() if session.created_at else None,
                        "updated_at": session.updated_at.isoformat() if session.updated_at else None
                    })
                
                return {
                    "user_id": user_id,
                    "sessions": session_list,
                    "total": len(session_list)
                }
        except Exception as e:
            print(f"获取用户会话列表失败: {e}")
            return {
                "user_id": user_id,
                "sessions": [],
                "total": 0,
                "error": str(e)
            }
    
    async def delete_session(self, session_id: str) -> bool:
        """
        删除会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            是否成功
        """
        try:
            with DatabaseManager() as db:
                return db.delete_session(session_id)
        except Exception as e:
            print(f"删除会话失败: {e}")
            return False
    
    async def get_user_emotion_trends(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """
        获取用户情绪趋势
        
        Args:
            user_id: 用户ID
            days: 天数
            
        Returns:
            情绪趋势
        """
        return self.chat_engine.get_user_emotion_trends(user_id)

