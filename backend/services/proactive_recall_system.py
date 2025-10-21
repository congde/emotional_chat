#!/usr/bin/env python3
"""
主动回忆系统
实现文档中提到的主动关怀和情感追踪功能
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from backend.database import DatabaseManager, ChatMessage, MemoryItem
from backend.services.enhanced_memory_manager import EnhancedMemoryManager
from sqlalchemy import and_, func


class EmotionTracker:
    """情感追踪器 - 追踪用户情绪变化"""
    
    def __init__(self):
        """初始化情感追踪器"""
        pass
    
    async def track_emotion_changes(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """
        追踪用户情绪变化
        
        Args:
            user_id: 用户ID
            days: 追踪天数
            
        Returns:
            情绪变化数据
        """
        try:
            with DatabaseManager() as db:
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                
                # 获取时间范围内的用户消息
                messages = db.db.query(ChatMessage).filter(
                    ChatMessage.user_id == user_id,
                    ChatMessage.role == 'user',
                    ChatMessage.created_at >= cutoff_date
                ).order_by(ChatMessage.created_at).all()
                
                if not messages:
                    return {
                        "trend": "无数据",
                        "current_state": "未知",
                        "changes": []
                    }
                
                # 分析情绪变化
                emotion_timeline = []
                for msg in messages:
                    if msg.emotion:
                        emotion_timeline.append({
                            "timestamp": msg.created_at.isoformat(),
                            "emotion": msg.emotion,
                            "intensity": msg.emotion_intensity or 5.0
                        })
                
                # 检测显著变化点
                changes = self._detect_emotion_changes(emotion_timeline)
                
                # 判断总体趋势
                trend = self._calculate_trend(emotion_timeline)
                
                # 当前状态
                current_state = emotion_timeline[-1]["emotion"] if emotion_timeline else "未知"
                
                return {
                    "trend": trend,
                    "current_state": current_state,
                    "changes": changes,
                    "timeline": emotion_timeline[-10:]  # 最近10条
                }
                
        except Exception as e:
            print(f"追踪情绪变化失败: {e}")
            return {
                "trend": "未知",
                "current_state": "未知",
                "changes": []
            }
    
    def _detect_emotion_changes(self, timeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        检测显著的情绪变化点
        
        Args:
            timeline: 情绪时间线
            
        Returns:
            变化点列表
        """
        changes = []
        
        # 定义负面和正面情绪
        negative_emotions = ["sad", "angry", "anxious", "worried", "depressed"]
        positive_emotions = ["happy", "excited", "grateful", "peaceful"]
        
        for i in range(1, len(timeline)):
            prev = timeline[i-1]
            curr = timeline[i]
            
            # 检测从负面到正面的转变
            if prev["emotion"] in negative_emotions and curr["emotion"] in positive_emotions:
                changes.append({
                    "type": "改善",
                    "from": prev["emotion"],
                    "to": curr["emotion"],
                    "timestamp": curr["timestamp"]
                })
            
            # 检测从正面到负面的转变
            elif prev["emotion"] in positive_emotions and curr["emotion"] in negative_emotions:
                changes.append({
                    "type": "恶化",
                    "from": prev["emotion"],
                    "to": curr["emotion"],
                    "timestamp": curr["timestamp"]
                })
            
            # 检测强度显著变化（>3分）
            elif abs(curr["intensity"] - prev["intensity"]) > 3:
                changes.append({
                    "type": "波动",
                    "intensity_change": curr["intensity"] - prev["intensity"],
                    "timestamp": curr["timestamp"]
                })
        
        return changes[-5:]  # 返回最近5个变化点
    
    def _calculate_trend(self, timeline: List[Dict[str, Any]]) -> str:
        """
        计算总体情绪趋势
        
        Args:
            timeline: 情绪时间线
            
        Returns:
            趋势描述
        """
        if len(timeline) < 3:
            return "数据不足"
        
        # 分为前半和后半
        mid = len(timeline) // 2
        early = timeline[:mid]
        late = timeline[mid:]
        
        # 计算平均强度
        early_avg = sum(e["intensity"] for e in early) / len(early)
        late_avg = sum(e["intensity"] for e in late) / len(late)
        
        if late_avg > early_avg + 1.5:
            return "情绪波动增强"
        elif late_avg < early_avg - 1.5:
            return "情绪趋于平稳"
        else:
            return "情绪稳定"


class ProactiveRecallSystem:
    """主动回忆系统 - 实现AI的主动关怀"""
    
    def __init__(self):
        """初始化主动回忆系统"""
        self.memory_manager = EnhancedMemoryManager()
        self.emotion_tracker = EmotionTracker()
    
    async def should_trigger_proactive_recall(self, 
                                             user_id: str,
                                             current_message: str,
                                             emotion: Optional[str] = None) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        判断是否应该触发主动回忆
        
        Args:
            user_id: 用户ID
            current_message: 当前消息
            emotion: 当前情绪
            
        Returns:
            (是否触发, 回忆内容)
        """
        # 1. 检查是否是闲聊场景（适合主动回忆）
        casual_keywords = ["天气", "今天", "最近", "怎么样", "不错", "还好"]
        is_casual = any(keyword in current_message for keyword in casual_keywords)
        
        if not is_casual:
            return False, None
        
        # 2. 检查是否有未跟进的重要记忆
        unfollow_memory = await self._find_unfollow_memory(user_id)
        if unfollow_memory:
            return True, {
                "type": "unfollow_memory",
                "memory": unfollow_memory,
                "prompt": self._generate_followup_prompt(unfollow_memory)
            }
        
        # 3. 检查情绪变化（如果上次是负面情绪，主动关心）
        emotion_change = await self._check_emotion_change(user_id)
        if emotion_change:
            return True, {
                "type": "emotion_check",
                "change": emotion_change,
                "prompt": self._generate_emotion_check_prompt(emotion_change)
            }
        
        # 4. 检查长期未互动用户（超过7天）
        days_since_last = await self._days_since_last_interaction(user_id)
        if days_since_last > 7:
            return True, {
                "type": "long_absence",
                "days": days_since_last,
                "prompt": f"好久不见了！距离我们上次聊天已经过去{days_since_last}天了。最近过得怎么样？"
            }
        
        return False, None
    
    async def _find_unfollow_memory(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        查找未跟进的重要记忆
        
        Args:
            user_id: 用户ID
            
        Returns:
            未跟进的记忆
        """
        try:
            with DatabaseManager() as db:
                # 查找重要且最近未被访问的记忆
                cutoff_date = datetime.utcnow() - timedelta(days=7)
                
                memory = db.db.query(MemoryItem).filter(
                    MemoryItem.user_id == user_id,
                    MemoryItem.is_active == True,
                    MemoryItem.importance > 0.7,
                    MemoryItem.memory_type.in_(["commitment", "event", "concern"]),
                    and_(
                        MemoryItem.created_at < cutoff_date,
                        (MemoryItem.last_accessed == None) | (MemoryItem.last_accessed < cutoff_date)
                    )
                ).order_by(MemoryItem.importance.desc()).first()
                
                if memory:
                    return {
                        "id": memory.memory_id,
                        "type": memory.memory_type,
                        "content": memory.summary or memory.content[:100],
                        "days_ago": (datetime.utcnow() - memory.created_at).days
                    }
                
        except Exception as e:
            print(f"查找未跟进记忆失败: {e}")
        
        return None
    
    async def _check_emotion_change(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        检查最近的情绪变化
        
        Args:
            user_id: 用户ID
            
        Returns:
            情绪变化信息
        """
        try:
            with DatabaseManager() as db:
                # 获取最近的两次用户消息
                recent_messages = db.db.query(ChatMessage).filter(
                    ChatMessage.user_id == user_id,
                    ChatMessage.role == 'user'
                ).order_by(ChatMessage.created_at.desc()).limit(2).all()
                
                if len(recent_messages) < 2:
                    return None
                
                current = recent_messages[0]
                previous = recent_messages[1]
                
                # 检查是否从负面情绪恢复
                negative_emotions = ["sad", "angry", "anxious", "worried", "depressed"]
                
                if previous.emotion in negative_emotions and \
                   current.emotion not in negative_emotions and \
                   (datetime.utcnow() - previous.created_at).days >= 1:
                    
                    return {
                        "previous_emotion": previous.emotion,
                        "previous_content": previous.content[:50],
                        "days_ago": (datetime.utcnow() - previous.created_at).days
                    }
                
        except Exception as e:
            print(f"检查情绪变化失败: {e}")
        
        return None
    
    async def _days_since_last_interaction(self, user_id: str) -> int:
        """
        计算距离上次互动的天数
        
        Args:
            user_id: 用户ID
            
        Returns:
            天数
        """
        try:
            with DatabaseManager() as db:
                last_message = db.db.query(ChatMessage).filter(
                    ChatMessage.user_id == user_id
                ).order_by(ChatMessage.created_at.desc()).first()
                
                if last_message:
                    return (datetime.utcnow() - last_message.created_at).days
                
        except Exception as e:
            print(f"计算互动间隔失败: {e}")
        
        return 0
    
    def _generate_followup_prompt(self, memory: Dict[str, Any]) -> str:
        """
        生成跟进提示
        
        Args:
            memory: 记忆信息
            
        Returns:
            提示文本
        """
        days = memory.get("days_ago", 0)
        content = memory.get("content", "")
        memory_type = memory.get("type", "")
        
        if memory_type == "commitment":
            return f"记得你{days}天前提到的：{content}。这件事进展如何了？"
        elif memory_type == "event":
            return f"{days}天前你说起：{content}。现在情况怎么样了？"
        elif memory_type == "concern":
            return f"你之前一直关心的：{content}。最近有什么新的想法吗？"
        else:
            return f"还记得{days}天前我们聊到的：{content}。想和我分享最新的情况吗？"
    
    def _generate_emotion_check_prompt(self, change: Dict[str, Any]) -> str:
        """
        生成情绪关怀提示
        
        Args:
            change: 情绪变化信息
            
        Returns:
            提示文本
        """
        days = change.get("days_ago", 0)
        prev_content = change.get("previous_content", "")
        
        return f"你{days}天前说：{prev_content}。我一直记得你当时的情绪。现在感觉好些了吗？"
    
    async def generate_proactive_response(self,
                                        user_id: str,
                                        current_message: str,
                                        emotion: Optional[str] = None) -> Optional[str]:
        """
        生成主动回应（在适当的时候）
        
        Args:
            user_id: 用户ID
            current_message: 当前消息
            emotion: 当前情绪
            
        Returns:
            主动回应文本（如果需要）
        """
        should_recall, recall_content = await self.should_trigger_proactive_recall(
            user_id, current_message, emotion
        )
        
        if should_recall and recall_content:
            return recall_content.get("prompt", "")
        
        return None
    
    async def get_emotion_trend_insight(self, user_id: str) -> str:
        """
        获取情绪趋势洞察（用于Prompt增强）
        
        Args:
            user_id: 用户ID
            
        Returns:
            洞察文本
        """
        trend_data = await self.emotion_tracker.track_emotion_changes(user_id, days=7)
        
        parts = []
        parts.append(f"情绪趋势: {trend_data.get('trend', '未知')}")
        parts.append(f"当前状态: {trend_data.get('current_state', '未知')}")
        
        changes = trend_data.get("changes", [])
        if changes:
            recent_change = changes[-1]
            if recent_change.get("type") == "改善":
                parts.append("（最近有改善迹象）")
            elif recent_change.get("type") == "恶化":
                parts.append("（需要更多关注）")
        
        return "；".join(parts)

