#!/usr/bin/env python3
"""
增强版上下文组装器
实现文档中提到的智能上下文管理功能
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from backend.services.enhanced_memory_manager import EnhancedMemoryManager
from backend.services.user_profile_builder import UserProfileBuilder


class EnhancedContextAssembler:
    """增强版上下文组装器 - 智能管理对话上下文"""
    
    def __init__(self):
        """初始化上下文组装器"""
        self.memory_manager = EnhancedMemoryManager()
        self.profile_builder = UserProfileBuilder()
    
    async def assemble_context(self,
                              user_id: str,
                              session_id: str,
                              current_message: str,
                              chat_history: List[Dict[str, Any]],
                              emotion: Optional[str] = None,
                              emotion_intensity: Optional[float] = None) -> Dict[str, Any]:
        """
        组装完整的对话上下文
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            current_message: 当前消息
            chat_history: 对话历史
            emotion: 当前情绪
            emotion_intensity: 情绪强度
            
        Returns:
            完整的上下文数据
        """
        # 1. 识别重要对话轮次
        important_markers = self._identify_important_turns(chat_history)
        
        # 2. 获取短期记忆（裁剪后的对话历史）
        short_term_context = self.memory_manager.get_short_term_context(
            chat_history, 
            important_markers
        )
        
        # 3. 检索长期记忆（向量检索）
        long_term_memories = await self.memory_manager.retrieve_memories(
            user_id=user_id,
            query=current_message,
            n_results=5,
            days_limit=30,
            enable_decay=True
        )
        
        # 4. 获取用户画像
        user_profile = await self.profile_builder.build_profile(user_id)
        profile_summary = await self.profile_builder.generate_profile_summary(user_id)
        
        # 5. 获取对话脉络图谱
        conversation_graph = await self.profile_builder.build_conversation_graph(user_id)
        
        # 6. 组装上下文
        context = {
            "user_id": user_id,
            "session_id": session_id,
            "current_message": current_message,
            "current_emotion": {
                "emotion": emotion,
                "intensity": emotion_intensity
            },
            "short_term_memory": {
                "messages": short_term_context,
                "count": len(short_term_context),
                "important_turns": important_markers
            },
            "long_term_memory": {
                "memories": long_term_memories,
                "count": len(long_term_memories)
            },
            "user_profile": {
                "summary": profile_summary,
                "details": user_profile
            },
            "conversation_graph": conversation_graph,
            "timestamp": datetime.now().isoformat()
        }
        
        return context
    
    def _identify_important_turns(self, chat_history: List[Dict[str, Any]]) -> List[int]:
        """
        识别重要的对话轮次
        
        Args:
            chat_history: 对话历史
            
        Returns:
            重要轮次的索引列表
        """
        important_markers = []
        
        for i, msg in enumerate(chat_history):
            if msg.get("role") != "user":
                continue
            
            # 构造消息对象
            message_obj = {
                "content": msg.get("content", ""),
                "emotion_intensity": msg.get("emotion_intensity", 5.0)
            }
            
            # 使用短期记忆管理器的判断逻辑
            if self.memory_manager.short_term.mark_important_turn(message_obj):
                important_markers.append(i)
        
        return important_markers
    
    def build_prompt_context(self, context: Dict[str, Any], system_prompt: str) -> str:
        """
        根据上下文构建完整的Prompt
        
        Args:
            context: 上下文数据
            system_prompt: 系统Prompt
            
        Returns:
            完整的Prompt文本
        """
        prompt_parts = [system_prompt, "\n"]
        
        # 1. 用户画像部分
        if context.get("user_profile", {}).get("summary"):
            prompt_parts.append("【用户画像】")
            prompt_parts.append(context["user_profile"]["summary"])
            prompt_parts.append("\n")
        
        # 2. 长期记忆部分
        long_term_memories = context.get("long_term_memory", {}).get("memories", [])
        if long_term_memories:
            prompt_parts.append("【历史记忆】")
            for i, memory in enumerate(long_term_memories[:3], 1):
                days_ago = memory.get("days_ago", 0)
                time_desc = f"{days_ago}天前" if days_ago > 0 else "今天"
                prompt_parts.append(f"{i}. {time_desc}: {memory.get('content', '')[:100]}")
            prompt_parts.append("\n")
        
        # 3. 短期对话历史
        short_term_messages = context.get("short_term_memory", {}).get("messages", [])
        if short_term_messages:
            prompt_parts.append("【最近对话】")
            for msg in short_term_messages[-5:]:  # 最近5轮
                role = "用户" if msg.get("role") == "user" else "助手"
                content = msg.get("content", "")[:200]  # 限制长度
                prompt_parts.append(f"{role}: {content}")
            prompt_parts.append("\n")
        
        # 4. 当前消息和情绪
        prompt_parts.append("【当前状态】")
        current_emotion = context.get("current_emotion", {})
        if current_emotion.get("emotion"):
            prompt_parts.append(f"用户情绪: {current_emotion['emotion']} (强度: {current_emotion.get('intensity', 5.0):.1f}/10)")
        
        prompt_parts.append(f"用户消息: {context.get('current_message', '')}")
        prompt_parts.append("\n")
        
        # 5. 回应要求
        prompt_parts.append("【回应要求】")
        prompt_parts.append("- 回应要体现对过往经历的记忆")
        prompt_parts.append("- 语气要符合用户偏好")
        prompt_parts.append("- 避免重复已讨论过的建议")
        prompt_parts.append("- 保持温暖、共情的态度")
        
        return "\n".join(prompt_parts)
    
    def generate_context_summary(self, context: Dict[str, Any]) -> str:
        """
        生成上下文摘要
        
        Args:
            context: 上下文数据
            
        Returns:
            摘要文本
        """
        summary_parts = []
        
        # 用户画像
        if context.get("user_profile", {}).get("summary"):
            summary_parts.append(f"用户画像: {context['user_profile']['summary']}")
        
        # 记忆数量
        short_term_count = context.get("short_term_memory", {}).get("count", 0)
        long_term_count = context.get("long_term_memory", {}).get("count", 0)
        summary_parts.append(f"上下文: {short_term_count}轮对话, {long_term_count}条记忆")
        
        # 当前情绪
        current_emotion = context.get("current_emotion", {})
        if current_emotion.get("emotion"):
            summary_parts.append(f"情绪: {current_emotion['emotion']}")
        
        return " | ".join(summary_parts)

