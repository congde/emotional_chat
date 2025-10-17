#!/usr/bin/env python3
"""
上下文组装器
整合用户画像、长期记忆、对话历史，生成完整的上下文
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from backend.memory_manager import MemoryManager
from backend.database import DatabaseManager


class UserProfile:
    """用户画像数据结构"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.name = None
        self.age = None
        self.gender = None
        self.personality_traits = []  # 性格特征
        self.interests = []  # 兴趣爱好
        self.concerns = []  # 长期关注的问题
        self.communication_style = "默认"  # 沟通风格偏好
        self.emotional_baseline = "稳定"  # 情绪基线
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "personality_traits": self.personality_traits,
            "interests": self.interests,
            "concerns": self.concerns,
            "communication_style": self.communication_style,
            "emotional_baseline": self.emotional_baseline,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }
    
    def to_summary(self) -> str:
        """生成简短摘要（用于prompt）"""
        summary_parts = []
        
        if self.name:
            summary_parts.append(f"姓名：{self.name}")
        if self.age:
            summary_parts.append(f"年龄：{self.age}岁")
        if self.gender:
            summary_parts.append(f"性别：{self.gender}")
        if self.personality_traits:
            summary_parts.append(f"性格：{', '.join(self.personality_traits[:3])}")
        if self.interests:
            summary_parts.append(f"兴趣：{', '.join(self.interests[:3])}")
        if self.concerns:
            summary_parts.append(f"关注：{', '.join(self.concerns[:3])}")
        if self.emotional_baseline != "稳定":
            summary_parts.append(f"情绪状态：{self.emotional_baseline}")
        
        return "；".join(summary_parts) if summary_parts else "暂无用户画像信息"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        """从字典创建"""
        profile = cls(data.get("user_id", "unknown"))
        profile.name = data.get("name")
        profile.age = data.get("age")
        profile.gender = data.get("gender")
        profile.personality_traits = data.get("personality_traits", [])
        profile.interests = data.get("interests", [])
        profile.concerns = data.get("concerns", [])
        profile.communication_style = data.get("communication_style", "默认")
        profile.emotional_baseline = data.get("emotional_baseline", "稳定")
        
        created_at = data.get("created_at")
        if created_at:
            profile.created_at = datetime.fromisoformat(created_at) if isinstance(created_at, str) else created_at
        
        updated_at = data.get("updated_at")
        if updated_at:
            profile.updated_at = datetime.fromisoformat(updated_at) if isinstance(updated_at, str) else updated_at
        
        return profile


class ContextAssembler:
    """上下文组装器 - 整合所有上下文信息"""
    
    def __init__(self):
        """初始化上下文组装器"""
        self.memory_manager = MemoryManager()
        self.user_profiles = {}  # 缓存用户画像
    
    def assemble_context(self, user_id: str, session_id: str, 
                        current_message: str,
                        chat_history: Optional[List[Dict[str, str]]] = None,
                        emotion: Optional[str] = None,
                        emotion_intensity: Optional[float] = None) -> Dict[str, Any]:
        """
        组装完整上下文
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            current_message: 当前用户消息
            chat_history: 对话历史
            emotion: 当前情绪
            emotion_intensity: 情绪强度
            
        Returns:
            完整的上下文数据
        """
        # 1. 获取用户画像
        profile = self.get_user_profile(user_id)
        
        # 2. 检索相关记忆
        memories = self._retrieve_relevant_memories(
            user_id, current_message, emotion, emotion_intensity
        )
        
        # 3. 获取情绪趋势
        emotion_trend = self.memory_manager.get_user_emotion_trend(user_id, days=7)
        
        # 4. 处理对话历史（只保留最近的几轮）
        recent_history = self._process_chat_history(chat_history or [], max_turns=5)
        
        # 5. 组装上下文
        context = {
            "user_profile": {
                "summary": profile.to_summary(),
                "full": profile.to_dict()
            },
            "memories": {
                "recent_events": [m for m in memories if m["type"] == "event"],
                "concerns": [m for m in memories if m["type"] == "concern"],
                "relationships": [m for m in memories if m["type"] == "relationship"],
                "commitments": [m for m in memories if m["type"] == "commitment"],
                "all": memories
            },
            "emotion_context": {
                "current_emotion": emotion or "未知",
                "current_intensity": emotion_intensity or 5.0,
                "trend": emotion_trend
            },
            "chat_history": recent_history,
            "current_message": current_message,
            "metadata": {
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        return context
    
    def build_prompt_context(self, context: Dict[str, Any], 
                           system_prompt: str) -> str:
        """
        根据上下文构建完整的prompt
        
        Args:
            context: 组装的上下文数据
            system_prompt: 系统prompt模板
            
        Returns:
            完整的prompt文本
        """
        # 构建用户画像部分
        profile_section = f"【用户画像】\n{context['user_profile']['summary']}\n"
        
        # 构建记忆部分
        memory_section = "【近期记忆】\n"
        memories = context["memories"]["all"]
        
        if not memories:
            memory_section += "暂无相关记忆\n"
        else:
            for i, mem in enumerate(memories[:3], 1):  # 最多显示3条
                memory_section += f"{i}. [{mem['type']}] {mem['content'][:60]}...\n"
                memory_section += f"   (情绪: {mem['emotion']}, 强度: {mem['intensity']:.1f}, 重要性: {mem['importance']:.2f})\n"
        
        # 构建情绪趋势部分
        emotion_section = "【情绪状态】\n"
        emotion_section += f"当前情绪: {context['emotion_context']['current_emotion']}\n"
        emotion_section += f"情绪强度: {context['emotion_context']['current_intensity']:.1f}/10\n"
        
        trend_data = context['emotion_context']['trend']
        if trend_data.get('emotions'):
            top_emotions = trend_data['emotions'][:3]
            emotion_list = ', '.join([f"{e['emotion']}({e['count']}次)" for e in top_emotions])
            emotion_section += f"近期情绪: {emotion_list}\n"
            emotion_section += f"趋势: {trend_data['trend']}\n"
        
        # 构建对话历史部分
        history_section = "【当前对话】\n"
        for msg in context["chat_history"]:
            role_name = "用户" if msg["role"] == "user" else "心语"
            history_section += f"{role_name}: {msg['content']}\n"
        
        # 当前消息
        current_section = f"\n用户: {context['current_message']}\n"
        
        # 组装完整prompt
        full_prompt = f"""【AI角色】{system_prompt}

{profile_section}
{memory_section}
{emotion_section}
{history_section}
{current_section}

请基于以上信息，用共情、支持性的语气回复用户。注意：
1. 如果记忆中有相关的重要事件，要适当提及
2. 关注用户的情绪变化趋势
3. 保持温暖、耐心的陪伴者角色
4. 回复控制在3-4句话，口语化表达
"""
        
        return full_prompt
    
    def _retrieve_relevant_memories(self, user_id: str, query: str, 
                                   emotion: Optional[str] = None,
                                   intensity: Optional[float] = None) -> List[Dict[str, Any]]:
        """检索相关记忆"""
        # 优先检索高情绪强度的事件
        if intensity and intensity >= 7.0:
            # 情绪强烈时，检索更多相关记忆
            return self.memory_manager.retrieve_memories(
                user_id=user_id,
                query=query,
                n_results=5,
                days_limit=14,  # 扩大时间范围
                min_importance=0.4
            )
        else:
            # 正常检索
            return self.memory_manager.retrieve_memories(
                user_id=user_id,
                query=query,
                n_results=3,
                days_limit=7,
                min_importance=0.5
            )
    
    def _process_chat_history(self, history: List[Dict[str, str]], 
                             max_turns: int = 5) -> List[Dict[str, str]]:
        """处理对话历史，只保留最近的几轮"""
        # 按时间倒序排列，取最新的
        recent = history[-max_turns*2:] if len(history) > max_turns*2 else history
        return recent
    
    def get_user_profile(self, user_id: str) -> UserProfile:
        """
        获取用户画像
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户画像对象
        """
        # 先从缓存获取
        if user_id in self.user_profiles:
            return self.user_profiles[user_id]
        
        # 从数据库加载（这里简化处理，实际应该从数据库读取）
        profile = self._load_profile_from_storage(user_id)
        
        # 缓存
        self.user_profiles[user_id] = profile
        
        return profile
    
    def _load_profile_from_storage(self, user_id: str) -> UserProfile:
        """从存储加载用户画像"""
        # TODO: 从数据库或文件系统加载
        # 这里先返回一个默认画像
        profile = UserProfile(user_id)
        
        # 可以从向量数据库的记忆中推断用户画像
        important_memories = self.memory_manager.get_important_memories(user_id, limit=10)
        
        # 提取兴趣和关注点
        for mem in important_memories:
            if mem["type"] == "preference":
                # 提取兴趣
                content = mem.get("content", "")
                # 简单提取（实际应该用NLP）
                profile.interests.append(content[:20])
            elif mem["type"] == "concern":
                # 提取关注点
                content = mem.get("content", "")
                profile.concerns.append(content[:20])
        
        # 去重
        profile.interests = list(set(profile.interests))[:5]
        profile.concerns = list(set(profile.concerns))[:5]
        
        # 根据情绪趋势设置情绪基线
        trend = self.memory_manager.get_user_emotion_trend(user_id, days=14)
        if trend.get("trend"):
            if "波动" in trend["trend"]:
                profile.emotional_baseline = "波动较大"
            elif "平稳" in trend["trend"]:
                profile.emotional_baseline = "较为平稳"
        
        return profile
    
    def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> UserProfile:
        """
        更新用户画像
        
        Args:
            user_id: 用户ID
            updates: 更新的字段
            
        Returns:
            更新后的用户画像
        """
        profile = self.get_user_profile(user_id)
        
        # 更新字段
        for key, value in updates.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        profile.updated_at = datetime.now()
        
        # 保存到存储
        self._save_profile_to_storage(profile)
        
        # 更新缓存
        self.user_profiles[user_id] = profile
        
        return profile
    
    def _save_profile_to_storage(self, profile: UserProfile):
        """保存用户画像到存储"""
        # TODO: 保存到数据库或文件系统
        # 这里先简单输出日志
        print(f"保存用户画像: {profile.user_id}")
        
        # 可以保存到文件
        try:
            import os
            profiles_dir = "/home/workSpace/emotional_chat/user_profiles"
            os.makedirs(profiles_dir, exist_ok=True)
            
            profile_file = os.path.join(profiles_dir, f"{profile.user_id}.json")
            with open(profile_file, 'w', encoding='utf-8') as f:
                json.dump(profile.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存用户画像失败: {e}")
    
    def generate_context_summary(self, context: Dict[str, Any]) -> str:
        """
        生成上下文摘要（用于日志和调试）
        
        Args:
            context: 上下文数据
            
        Returns:
            摘要文本
        """
        summary = []
        
        summary.append("=== 上下文摘要 ===")
        summary.append(f"用户: {context['metadata']['user_id']}")
        summary.append(f"会话: {context['metadata']['session_id']}")
        summary.append(f"\n用户画像: {context['user_profile']['summary']}")
        
        memories = context['memories']['all']
        summary.append(f"\n相关记忆: {len(memories)}条")
        for mem in memories[:2]:
            summary.append(f"  - [{mem['type']}] {mem['content'][:40]}...")
        
        summary.append(f"\n当前情绪: {context['emotion_context']['current_emotion']} "
                      f"(强度: {context['emotion_context']['current_intensity']:.1f})")
        
        trend = context['emotion_context']['trend']
        if trend.get('trend'):
            summary.append(f"情绪趋势: {trend['trend']}")
        
        summary.append(f"\n对话轮数: {len(context['chat_history'])//2}")
        
        return "\n".join(summary)

