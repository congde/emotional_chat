#!/usr/bin/env python3
"""
用户画像构建器
实现文档中提到的动态用户画像和对话脉络功能
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import Counter
import json
from backend.database import DatabaseManager, UserProfileDB, ChatMessage, MemoryItem
from sqlalchemy import func, and_


class ConversationGraph:
    """对话脉络图谱 - 记录关键事件之间的因果关系"""
    
    def __init__(self):
        """初始化对话图谱"""
        self.nodes = {}  # {node_id: {type, content, timestamp}}
        self.edges = []  # [(from_id, to_id, relation_type)]
    
    def add_node(self, node_id: str, node_type: str, content: str, timestamp: str):
        """添加节点"""
        self.nodes[node_id] = {
            "type": node_type,
            "content": content,
            "timestamp": timestamp
        }
    
    def add_edge(self, from_id: str, to_id: str, relation_type: str):
        """添加边（关系）"""
        self.edges.append((from_id, to_id, relation_type))
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "nodes": self.nodes,
            "edges": self.edges
        }


class UserProfileBuilder:
    """用户画像构建器 - 动态构建和更新用户画像"""
    
    def __init__(self):
        """初始化用户画像构建器"""
        pass
    
    async def build_profile(self, user_id: str, force_rebuild: bool = False) -> Dict[str, Any]:
        """
        构建或更新用户画像
        
        Args:
            user_id: 用户ID
            force_rebuild: 是否强制重建
            
        Returns:
            用户画像字典
        """
        try:
            with DatabaseManager() as db:
                # 检查是否已有画像
                profile_db = db.db.query(UserProfileDB).filter(
                    UserProfileDB.user_id == user_id
                ).first()
                
                if profile_db and not force_rebuild:
                    # 如果最近更新过（24小时内），直接返回
                    if profile_db.updated_at and \
                       (datetime.utcnow() - profile_db.updated_at).total_seconds() < 86400:
                        return self._profile_db_to_dict(profile_db)
                
                # 否则，重新分析构建
                profile_data = await self._analyze_user_data(user_id, db)
                
                # 更新或创建数据库记录
                if profile_db:
                    self._update_profile_db(profile_db, profile_data)
                else:
                    profile_db = self._create_profile_db(user_id, profile_data)
                    db.db.add(profile_db)
                
                db.db.commit()
                
                return self._profile_db_to_dict(profile_db)
                
        except Exception as e:
            print(f"构建用户画像失败: {e}")
            import traceback
            traceback.print_exc()
            return self._get_default_profile(user_id)
    
    async def _analyze_user_data(self, user_id: str, db: DatabaseManager) -> Dict[str, Any]:
        """
        分析用户数据，提取画像特征
        
        Args:
            user_id: 用户ID
            db: 数据库管理器
            
        Returns:
            画像数据字典
        """
        # 1. 获取用户的所有消息（最近30天）
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        messages = db.db.query(ChatMessage).filter(
            ChatMessage.user_id == user_id,
            ChatMessage.role == 'user',
            ChatMessage.created_at >= cutoff_date
        ).all()
        
        # 2. 获取用户的所有记忆
        memories = db.db.query(MemoryItem).filter(
            MemoryItem.user_id == user_id,
            MemoryItem.is_active == True
        ).all()
        
        # 3. 分析核心关注点
        core_concerns = self._extract_core_concerns(memories)
        
        # 4. 分析情绪趋势
        emotional_trend = self._analyze_emotional_trend(messages)
        
        # 5. 分析沟通偏好
        communication_style = self._analyze_communication_style(messages)
        
        # 6. 提取重要事件
        important_events = self._extract_important_events(memories)
        
        # 7. 统计信息
        total_sessions = db.db.query(func.count(func.distinct(ChatMessage.session_id))).filter(
            ChatMessage.user_id == user_id
        ).scalar() or 0
        
        total_messages = len(messages)
        
        # 计算平均情绪强度
        emotion_intensities = [m.emotion_intensity for m in messages if m.emotion_intensity]
        avg_emotion_intensity = sum(emotion_intensities) / len(emotion_intensities) if emotion_intensities else 5.0
        
        return {
            "core_concerns": core_concerns,
            "emotional_trend": emotional_trend,
            "communication_style": communication_style,
            "important_events": important_events,
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "avg_emotion_intensity": avg_emotion_intensity
        }
    
    def _extract_core_concerns(self, memories: List[MemoryItem]) -> List[str]:
        """
        提取核心关注点
        
        Args:
            memories: 记忆列表
            
        Returns:
            关注点列表
        """
        # 统计concern类型的记忆
        concerns = []
        for memory in memories:
            if memory.memory_type == "concern":
                concerns.append(memory.summary or memory.content[:50])
        
        # 返回前5个
        return concerns[:5]
    
    def _analyze_emotional_trend(self, messages: List[ChatMessage]) -> str:
        """
        分析情绪趋势
        
        Args:
            messages: 消息列表
            
        Returns:
            趋势描述
        """
        if len(messages) < 5:
            return "数据不足"
        
        # 按时间排序
        sorted_messages = sorted(messages, key=lambda m: m.created_at)
        
        # 分为前半部分和后半部分
        mid = len(sorted_messages) // 2
        early_messages = sorted_messages[:mid]
        late_messages = sorted_messages[mid:]
        
        # 计算平均情绪强度
        early_intensities = [m.emotion_intensity for m in early_messages if m.emotion_intensity]
        late_intensities = [m.emotion_intensity for m in late_messages if m.emotion_intensity]
        
        if not early_intensities or not late_intensities:
            return "稳定"
        
        early_avg = sum(early_intensities) / len(early_intensities)
        late_avg = sum(late_intensities) / len(late_intensities)
        
        # 统计主要情绪
        early_emotions = [m.emotion for m in early_messages if m.emotion]
        late_emotions = [m.emotion for m in late_messages if m.emotion]
        
        early_emotion = Counter(early_emotions).most_common(1)[0][0] if early_emotions else "neutral"
        late_emotion = Counter(late_emotions).most_common(1)[0][0] if late_emotions else "neutral"
        
        # 生成趋势描述
        if late_avg > early_avg + 1.5:
            intensity_trend = "情绪波动增强"
        elif late_avg < early_avg - 1.5:
            intensity_trend = "情绪趋于平稳"
        else:
            intensity_trend = "情绪稳定"
        
        if early_emotion != late_emotion:
            emotion_trend = f"{early_emotion} → {late_emotion}"
        else:
            emotion_trend = f"持续{early_emotion}"
        
        return f"{emotion_trend}，{intensity_trend}"
    
    def _analyze_communication_style(self, messages: List[ChatMessage]) -> str:
        """
        分析沟通风格
        
        Args:
            messages: 消息列表
            
        Returns:
            沟通风格描述
        """
        if not messages:
            return "默认"
        
        # 计算平均消息长度
        avg_length = sum(len(m.content) for m in messages) / len(messages)
        
        # 统计问句数量
        question_count = sum(1 for m in messages if '?' in m.content or '吗' in m.content or '呢' in m.content)
        question_ratio = question_count / len(messages)
        
        # 统计情绪词使用频率
        emotion_keywords = ['开心', '难过', '焦虑', '担心', '害怕', '愤怒', '高兴', '痛苦']
        emotion_word_count = sum(
            1 for m in messages 
            for keyword in emotion_keywords 
            if keyword in m.content
        )
        emotion_ratio = emotion_word_count / len(messages)
        
        # 判断风格
        if avg_length > 100:
            length_style = "详细表达型"
        elif avg_length > 50:
            length_style = "适度表达型"
        else:
            length_style = "简洁表达型"
        
        if question_ratio > 0.5:
            interaction_style = "主动求助型"
        elif emotion_ratio > 0.6:
            interaction_style = "情感倾诉型"
        else:
            interaction_style = "理性交流型"
        
        return f"{length_style}，{interaction_style}"
    
    def _extract_important_events(self, memories: List[MemoryItem]) -> List[Dict[str, Any]]:
        """
        提取重要事件
        
        Args:
            memories: 记忆列表
            
        Returns:
            事件列表
        """
        events = []
        
        for memory in memories:
            if memory.memory_type == "event" and memory.importance > 0.6:
                events.append({
                    "date": memory.created_at.strftime("%Y-%m-%d") if memory.created_at else "",
                    "event": memory.summary or memory.content[:50],
                    "importance": memory.importance
                })
        
        # 按重要性排序，取前5个
        events.sort(key=lambda x: x["importance"], reverse=True)
        return events[:5]
    
    def _create_profile_db(self, user_id: str, profile_data: Dict[str, Any]) -> UserProfileDB:
        """创建数据库记录"""
        return UserProfileDB(
            user_id=user_id,
            personality_traits=json.dumps([], ensure_ascii=False),
            interests=json.dumps([], ensure_ascii=False),
            concerns=json.dumps(profile_data.get("core_concerns", []), ensure_ascii=False),
            communication_style=profile_data.get("communication_style", "默认"),
            emotional_baseline=profile_data.get("emotional_trend", "稳定"),
            total_sessions=profile_data.get("total_sessions", 0),
            total_messages=profile_data.get("total_messages", 0),
            avg_emotion_intensity=profile_data.get("avg_emotion_intensity", 5.0)
        )
    
    def _update_profile_db(self, profile_db: UserProfileDB, profile_data: Dict[str, Any]):
        """更新数据库记录"""
        profile_db.concerns = json.dumps(profile_data.get("core_concerns", []), ensure_ascii=False)
        profile_db.communication_style = profile_data.get("communication_style", "默认")
        profile_db.emotional_baseline = profile_data.get("emotional_trend", "稳定")
        profile_db.total_sessions = profile_data.get("total_sessions", 0)
        profile_db.total_messages = profile_data.get("total_messages", 0)
        profile_db.avg_emotion_intensity = profile_data.get("avg_emotion_intensity", 5.0)
        profile_db.updated_at = datetime.utcnow()
    
    def _profile_db_to_dict(self, profile_db: UserProfileDB) -> Dict[str, Any]:
        """将数据库记录转为字典"""
        try:
            concerns = json.loads(profile_db.concerns) if profile_db.concerns else []
        except:
            concerns = []
        
        return {
            "user_id": profile_db.user_id,
            "core_concerns": concerns,
            "emotional_trend": profile_db.emotional_baseline,
            "communication_style": profile_db.communication_style,
            "total_sessions": profile_db.total_sessions,
            "total_messages": profile_db.total_messages,
            "avg_emotion_intensity": profile_db.avg_emotion_intensity,
            "updated_at": profile_db.updated_at.isoformat() if profile_db.updated_at else None
        }
    
    def _get_default_profile(self, user_id: str) -> Dict[str, Any]:
        """获取默认画像"""
        return {
            "user_id": user_id,
            "core_concerns": [],
            "emotional_trend": "未知",
            "communication_style": "默认",
            "total_sessions": 0,
            "total_messages": 0,
            "avg_emotion_intensity": 5.0,
            "updated_at": None
        }
    
    async def build_conversation_graph(self, user_id: str) -> Dict[str, Any]:
        """
        构建对话脉络图谱
        
        Args:
            user_id: 用户ID
            
        Returns:
            图谱字典
        """
        try:
            with DatabaseManager() as db:
                # 获取用户的重要记忆
                memories = db.db.query(MemoryItem).filter(
                    MemoryItem.user_id == user_id,
                    MemoryItem.is_active == True,
                    MemoryItem.importance > 0.6
                ).order_by(MemoryItem.created_at).all()
                
                # 构建图谱
                graph = ConversationGraph()
                
                # 添加节点
                for memory in memories:
                    graph.add_node(
                        node_id=memory.memory_id,
                        node_type=memory.memory_type,
                        content=memory.summary or memory.content[:50],
                        timestamp=memory.created_at.isoformat() if memory.created_at else ""
                    )
                
                # 简单的因果关系推断（基于时间和类型）
                # 例如：concern -> event -> relationship
                for i, current_memory in enumerate(memories[:-1]):
                    next_memory = memories[i + 1]
                    
                    # 判断关系类型
                    if current_memory.memory_type == "concern" and next_memory.memory_type == "event":
                        graph.add_edge(current_memory.memory_id, next_memory.memory_id, "导致")
                    elif current_memory.memory_type == "event" and next_memory.memory_type == "concern":
                        graph.add_edge(current_memory.memory_id, next_memory.memory_id, "加剧")
                    elif current_memory.memory_type == "event" and next_memory.memory_type == "relationship":
                        graph.add_edge(current_memory.memory_id, next_memory.memory_id, "影响")
                
                return graph.to_dict()
                
        except Exception as e:
            print(f"构建对话图谱失败: {e}")
            return {"nodes": {}, "edges": []}
    
    async def generate_profile_summary(self, user_id: str) -> str:
        """
        生成用户画像摘要（用于Prompt注入）
        
        Args:
            user_id: 用户ID
            
        Returns:
            摘要文本
        """
        profile = await self.build_profile(user_id)
        
        # 构建摘要文本
        summary_parts = []
        
        # 关注点
        if profile.get("core_concerns"):
            concerns_str = "、".join(profile["core_concerns"][:3])
            summary_parts.append(f"核心关注：{concerns_str}")
        
        # 情绪趋势
        if profile.get("emotional_trend"):
            summary_parts.append(f"情绪趋势：{profile['emotional_trend']}")
        
        # 沟通风格
        if profile.get("communication_style"):
            summary_parts.append(f"沟通风格：{profile['communication_style']}")
        
        # 互动次数
        if profile.get("total_messages", 0) > 0:
            summary_parts.append(f"已互动{profile['total_messages']}次")
        
        if not summary_parts:
            return "新用户，尚无画像数据"
        
        return "；".join(summary_parts)

