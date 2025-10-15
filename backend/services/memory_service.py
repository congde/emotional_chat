#!/usr/bin/env python3
"""
记忆服务层
处理所有与记忆相关的业务逻辑
"""

from typing import Dict, List, Optional, Any
from backend.memory_manager import MemoryManager
from backend.memory_extractor import MemoryExtractor
from backend.database import DatabaseManager, MemoryItem
from datetime import datetime
import json


class MemoryService:
    """记忆服务 - 统一的记忆管理接口"""
    
    def __init__(self):
        """初始化记忆服务"""
        self.memory_manager = MemoryManager()
        self.extractor = MemoryExtractor()
    
    async def process_and_store_memories(
        self, 
        session_id: str, 
        user_id: str,
        user_message: str,
        bot_response: str,
        emotion: Optional[str] = None,
        emotion_intensity: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        处理对话并存储记忆
        
        Args:
            session_id: 会话ID
            user_id: 用户ID
            user_message: 用户消息
            bot_response: 机器人回复
            emotion: 情绪
            emotion_intensity: 情绪强度
            
        Returns:
            存储的记忆列表
        """
        # 处理对话，提取并存储记忆
        memories = self.memory_manager.process_conversation(
            session_id=session_id,
            user_id=user_id,
            user_message=user_message,
            bot_response=bot_response,
            emotion=emotion,
            emotion_intensity=emotion_intensity
        )
        
        # 同步到关系数据库
        if memories:
            self._sync_memories_to_db(memories)
        
        return memories
    
    def _sync_memories_to_db(self, memories: List[Dict[str, Any]]):
        """将记忆同步到关系数据库"""
        try:
            with DatabaseManager() as db:
                for memory in memories:
                    # 检查是否已存在
                    existing = db.db.query(MemoryItem).filter(
                        MemoryItem.memory_id == memory.get("id")
                    ).first()
                    
                    if not existing:
                        # 创建新记忆条目
                        memory_item = MemoryItem(
                            memory_id=memory.get("id"),
                            user_id=memory.get("user_id"),
                            session_id=memory.get("session_id"),
                            content=memory.get("content", ""),
                            summary=memory.get("summary", ""),
                            memory_type=memory.get("type", "other"),
                            emotion=memory.get("emotion"),
                            emotion_intensity=memory.get("intensity"),
                            importance=memory.get("importance", 0.5),
                            extraction_method=memory.get("extraction_method", "unknown"),
                            keywords=json.dumps([], ensure_ascii=False)
                        )
                        db.db.add(memory_item)
                
                db.db.commit()
        except Exception as e:
            print(f"同步记忆到数据库失败: {e}")
    
    async def retrieve_memories(
        self,
        user_id: str,
        query: str,
        n_results: int = 3,
        days_limit: int = 7
    ) -> List[Dict[str, Any]]:
        """
        检索相关记忆
        
        Args:
            user_id: 用户ID
            query: 查询文本
            n_results: 返回数量
            days_limit: 时间限制（天数）
            
        Returns:
            相关记忆列表
        """
        memories = self.memory_manager.retrieve_memories(
            user_id=user_id,
            query=query,
            n_results=n_results,
            days_limit=days_limit
        )
        
        # 更新访问统计
        if memories:
            self._update_access_stats(memories)
        
        return memories
    
    def _update_access_stats(self, memories: List[Dict[str, Any]]):
        """更新记忆的访问统计"""
        try:
            with DatabaseManager() as db:
                for memory in memories:
                    memory_id = memory.get("id")
                    memory_item = db.db.query(MemoryItem).filter(
                        MemoryItem.memory_id == memory_id
                    ).first()
                    
                    if memory_item:
                        memory_item.access_count += 1
                        memory_item.last_accessed = datetime.utcnow()
                
                db.db.commit()
        except Exception as e:
            print(f"更新访问统计失败: {e}")
    
    async def get_emotion_trend(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """
        获取用户情绪趋势
        
        Args:
            user_id: 用户ID
            days: 统计天数
            
        Returns:
            情绪趋势数据
        """
        return self.memory_manager.get_user_emotion_trend(user_id, days)
    
    async def get_important_memories(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        获取用户最重要的记忆
        
        Args:
            user_id: 用户ID
            limit: 返回数量
            
        Returns:
            重要记忆列表
        """
        return self.memory_manager.get_important_memories(user_id, limit)
    
    async def delete_memory(self, user_id: str, memory_id: str) -> bool:
        """
        删除指定记忆
        
        Args:
            user_id: 用户ID
            memory_id: 记忆ID
            
        Returns:
            是否删除成功
        """
        # 从向量数据库删除
        success = self.memory_manager.delete_memory(user_id, memory_id)
        
        # 从关系数据库软删除
        if success:
            try:
                with DatabaseManager() as db:
                    memory_item = db.db.query(MemoryItem).filter(
                        MemoryItem.memory_id == memory_id,
                        MemoryItem.user_id == user_id
                    ).first()
                    
                    if memory_item:
                        memory_item.is_active = False
                        db.db.commit()
            except Exception as e:
                print(f"从数据库删除记忆失败: {e}")
        
        return success
    
    async def get_user_memories_list(
        self,
        user_id: str,
        memory_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        获取用户记忆列表（用于管理界面）
        
        Args:
            user_id: 用户ID
            memory_type: 记忆类型过滤
            limit: 返回数量
            
        Returns:
            记忆列表
        """
        try:
            with DatabaseManager() as db:
                query = db.db.query(MemoryItem).filter(
                    MemoryItem.user_id == user_id,
                    MemoryItem.is_active == True
                )
                
                if memory_type:
                    query = query.filter(MemoryItem.memory_type == memory_type)
                
                memories = query.order_by(
                    MemoryItem.importance.desc(),
                    MemoryItem.created_at.desc()
                ).limit(limit).all()
                
                return [
                    {
                        "id": m.memory_id,
                        "type": m.memory_type,
                        "summary": m.summary,
                        "content": m.content,
                        "emotion": m.emotion,
                        "intensity": m.emotion_intensity,
                        "importance": m.importance,
                        "access_count": m.access_count,
                        "created_at": m.created_at.isoformat() if m.created_at else None,
                        "last_accessed": m.last_accessed.isoformat() if m.last_accessed else None
                    }
                    for m in memories
                ]
        except Exception as e:
            print(f"获取记忆列表失败: {e}")
            return []
    
    async def get_memory_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户记忆统计信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            统计数据
        """
        try:
            with DatabaseManager() as db:
                from sqlalchemy import func
                
                # 总记忆数
                total_count = db.db.query(func.count(MemoryItem.id)).filter(
                    MemoryItem.user_id == user_id,
                    MemoryItem.is_active == True
                ).scalar()
                
                # 按类型统计
                type_stats = db.db.query(
                    MemoryItem.memory_type,
                    func.count(MemoryItem.id).label('count')
                ).filter(
                    MemoryItem.user_id == user_id,
                    MemoryItem.is_active == True
                ).group_by(MemoryItem.memory_type).all()
                
                # 平均重要性
                avg_importance = db.db.query(func.avg(MemoryItem.importance)).filter(
                    MemoryItem.user_id == user_id,
                    MemoryItem.is_active == True
                ).scalar()
                
                return {
                    "total_count": total_count or 0,
                    "avg_importance": float(avg_importance) if avg_importance else 0,
                    "by_type": [
                        {"type": t.memory_type, "count": t.count}
                        for t in type_stats
                    ]
                }
        except Exception as e:
            print(f"获取记忆统计失败: {e}")
            return {"total_count": 0, "avg_importance": 0, "by_type": []}

