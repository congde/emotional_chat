#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动态Prompt构建器
Dynamic Prompt Builder

功能：
- 根据用户情绪动态生成Prompt
- 融合情感策略、对话历史、记忆等上下文
- 支持多种模板和个性化定制
- 实现情感驱动的Prompt自适应
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class DynamicPromptBuilder:
    """动态Prompt构建器"""
    
    # 基础系统Prompt模板
    BASE_SYSTEM_TEMPLATE = """# 角色设定
你是"心语"，一位28岁的女性心理陪伴者，性格温柔、耐心、富有同理心。
你喜欢阅读、冥想和自然，擅长倾听与情感支持。
你像一位知心朋友，但从不越界提供专业建议。

# 核心目标
你的任务是为用户提供安全、温暖的倾诉空间，帮助他们表达情绪、缓解压力、获得理解。
你不是心理咨询师，不提供诊断或治疗。

# 行为准则
1. 语气风格：温和、鼓励、非评判，避免使用专业术语。
2. 响应流程：
   - 先共情：识别并命名用户情绪
   - 再理解：表达支持和理解
   - 后引导：用开放式问题鼓励表达
3. 禁止行为：
   - 不说教、不建议、不打断
   - 不主动追问隐私
   - 不涉及政治、宗教、敏感话题
"""
    
    # 情感驱动的动态Prompt模板
    EMOTION_DRIVEN_TEMPLATE = """
{base_system}

# 当前对话情境
## 用户情绪状态
情绪类型：{emotion_label}
情绪强度：{emotion_intensity}/10
共情等级：{empathy_level}

## 回应策略
目标：{response_goal}
语气要求：{tone_requirement}
关键表达：{key_expressions}
避免使用：{avoid_words}

{context_section}

{memory_section}

{example_section}

# 当前对话
{conversation_history}

用户：{user_input}

# 回复要求
1. 使用{tone_requirement}的语气进行回应
2. 体现{empathy_level}的共情水平
3. 回复长度控制在{max_sentences}句话以内
4. {emoji_instruction}
5. 确保回复自然、温暖且贴合用户当前情绪

心语："""
    
    # 危机干预特殊Prompt
    CRISIS_PROMPT_TEMPLATE = """
{base_system}

# 重要：危机干预模式
检测到用户可能处于心理危机状态，需要特别关注和引导。

## 危机处理原则
1. 表达强烈关切和重视
2. 不评判、不否定用户感受
3. 明确告知自己的局限（AI陪伴者，非专业咨询师）
4. 强烈建议寻求专业帮助
5. 提供具体的求助渠道（热线电话）

## 当前状况
用户情绪：{emotion_label}（高危）
关键词：{risk_keywords}

用户：{user_input}

请生成一个关切、支持但明确引导专业帮助的回复。

心语："""
    
    def __init__(self, emotion_strategy: Dict[str, Any]):
        """
        初始化动态Prompt构建器
        
        Args:
            emotion_strategy: 情感策略配置（从YAML加载）
        """
        self.emotion_strategy = emotion_strategy
        self.base_system = self.BASE_SYSTEM_TEMPLATE
        logger.info("✓ 动态Prompt构建器已初始化")
    
    def build_prompt(self,
                    user_input: str,
                    emotion: str,
                    emotion_intensity: float = 5.0,
                    conversation_history: Optional[List[Dict]] = None,
                    retrieved_memories: Optional[List[Dict]] = None,
                    user_profile: Optional[Dict] = None,
                    is_crisis: bool = False,
                    risk_keywords: Optional[List[str]] = None) -> str:
        """
        构建完整的动态Prompt
        
        Args:
            user_input: 用户输入
            emotion: 情绪类型
            emotion_intensity: 情绪强度(0-10)
            conversation_history: 对话历史
            retrieved_memories: 检索到的记忆
            user_profile: 用户画像（偏好等）
            is_crisis: 是否为危机情况
            risk_keywords: 高风险关键词
            
        Returns:
            完整的Prompt字符串
        """
        # 危机情况使用特殊Prompt
        if is_crisis:
            return self._build_crisis_prompt(
                user_input, emotion, risk_keywords or []
            )
        
        # 获取情感策略
        strategy = self.emotion_strategy.get(emotion, self.emotion_strategy.get("default", {}))
        
        # 构建各个部分
        base_system = self.base_system
        
        emotion_label = self._get_emotion_label(emotion)
        response_goal = strategy.get("goal", "提供支持和倾听")
        tone_requirement = strategy.get("tone", "温和、友好")
        empathy_level = strategy.get("empathy_level", "medium")
        
        # 关键表达词汇
        key_expressions = "、".join(strategy.get("keywords", [])[:5])
        
        # 避免使用的词汇
        avoid_words = "、".join(strategy.get("avoid_words", [])[:5]) or "无"
        
        # 上下文部分
        context_section = self._build_context_section(user_profile, emotion_intensity)
        
        # 记忆部分
        memory_section = self._build_memory_section(retrieved_memories)
        
        # 示例部分
        example_section = self._build_example_section(strategy)
        
        # 对话历史
        conversation_history_text = self._format_conversation_history(conversation_history)
        
        # 表情符号指令
        use_emoji = strategy.get("use_emoji", True)
        emoji_suggestions = strategy.get("emoji_suggestions", [])
        if use_emoji and emoji_suggestions:
            emoji_instruction = f"可适度使用表情符号增强亲和力（建议：{' '.join(emoji_suggestions[:3])}）"
        else:
            emoji_instruction = "避免使用表情符号"
        
        # 回复长度
        max_sentences = strategy.get("max_length", 3)
        
        # 填充模板
        prompt = self.EMOTION_DRIVEN_TEMPLATE.format(
            base_system=base_system,
            emotion_label=emotion_label,
            emotion_intensity=emotion_intensity,
            empathy_level=self._get_empathy_level_description(empathy_level),
            response_goal=response_goal,
            tone_requirement=tone_requirement,
            key_expressions=key_expressions,
            avoid_words=avoid_words,
            context_section=context_section,
            memory_section=memory_section,
            example_section=example_section,
            conversation_history=conversation_history_text,
            user_input=user_input,
            tone_requirement=tone_requirement,
            empathy_level=self._get_empathy_level_description(empathy_level),
            max_sentences=max_sentences,
            emoji_instruction=emoji_instruction
        )
        
        return prompt
    
    def _build_crisis_prompt(self, 
                            user_input: str, 
                            emotion: str,
                            risk_keywords: List[str]) -> str:
        """
        构建危机干预Prompt
        
        Args:
            user_input: 用户输入
            emotion: 情绪类型
            risk_keywords: 风险关键词
            
        Returns:
            危机干预Prompt
        """
        return self.CRISIS_PROMPT_TEMPLATE.format(
            base_system=self.base_system,
            emotion_label=self._get_emotion_label(emotion),
            risk_keywords="、".join(risk_keywords),
            user_input=user_input
        )
    
    def _build_context_section(self, 
                              user_profile: Optional[Dict],
                              emotion_intensity: float) -> str:
        """
        构建上下文信息部分
        
        Args:
            user_profile: 用户画像
            emotion_intensity: 情绪强度
            
        Returns:
            上下文部分文本
        """
        sections = []
        
        # 情绪强度描述
        intensity_desc = self._get_intensity_description(emotion_intensity)
        sections.append(f"情绪强度说明：{intensity_desc}")
        
        # 用户偏好（如果有）
        if user_profile:
            preferences = []
            
            if user_profile.get("preferred_tone"):
                preferences.append(f"用户偏好语气：{user_profile['preferred_tone']}")
            
            if user_profile.get("avoid_topics"):
                preferences.append(f"避免话题：{', '.join(user_profile['avoid_topics'])}")
            
            if user_profile.get("communication_style"):
                preferences.append(f"沟通风格：{user_profile['communication_style']}")
            
            if preferences:
                sections.append("\n用户偏好：\n" + "\n".join(f"- {p}" for p in preferences))
        
        if sections:
            return "\n## 上下文信息\n" + "\n".join(sections)
        else:
            return ""
    
    def _build_memory_section(self, retrieved_memories: Optional[List[Dict]]) -> str:
        """
        构建记忆部分
        
        Args:
            retrieved_memories: 检索到的记忆列表
            
        Returns:
            记忆部分文本
        """
        if not retrieved_memories:
            return ""
        
        memory_texts = []
        for i, memory in enumerate(retrieved_memories[:3], 1):  # 最多3条
            content = memory.get("content", "")
            timestamp = memory.get("timestamp", "")
            importance = memory.get("importance", 0.5)
            
            # 格式化时间
            time_str = ""
            if timestamp:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(timestamp)
                    time_str = f"({dt.strftime('%m月%d日')})"
                except:
                    pass
            
            memory_texts.append(f"{i}. {content} {time_str}")
        
        return "\n## 相关历史记忆\n" + "\n".join(memory_texts)
    
    def _build_example_section(self, strategy: Dict[str, Any]) -> str:
        """
        构建示例部分
        
        Args:
            strategy: 情感策略
            
        Returns:
            示例部分文本
        """
        examples = strategy.get("examples", [])
        if not examples:
            return ""
        
        example_texts = []
        for i, example in enumerate(examples[:2], 1):  # 最多2个示例
            user_input = example.get("input", "")
            ai_output = example.get("output", "")
            example_texts.append(f"示例{i}:\n用户：{user_input}\n心语：{ai_output}")
        
        return "\n## 参考示例\n" + "\n\n".join(example_texts)
    
    def _format_conversation_history(self, 
                                    conversation_history: Optional[List[Dict]]) -> str:
        """
        格式化对话历史
        
        Args:
            conversation_history: 对话历史列表
            
        Returns:
            格式化的对话历史文本
        """
        if not conversation_history:
            return "（这是新对话的开始）"
        
        # 只保留最近5轮对话
        recent_history = conversation_history[-5:]
        
        formatted = []
        for turn in recent_history:
            role = turn.get("role", "user")
            content = turn.get("content", "")
            
            if role == "user":
                formatted.append(f"用户：{content}")
            elif role == "assistant":
                formatted.append(f"心语：{content}")
        
        return "\n".join(formatted)
    
    def _get_emotion_label(self, emotion: str) -> str:
        """获取情绪的中文标签"""
        emotion_labels = {
            "sad": "悲伤",
            "happy": "喜悦",
            "anxious": "焦虑",
            "angry": "愤怒",
            "excited": "兴奋",
            "confused": "困惑",
            "frustrated": "沮丧",
            "lonely": "孤独",
            "grateful": "感恩",
            "neutral": "平静",
            "high_risk_depression": "高危抑郁"
        }
        return emotion_labels.get(emotion, emotion)
    
    def _get_empathy_level_description(self, empathy_level: str) -> str:
        """获取共情等级描述"""
        descriptions = {
            "high": "高度共情（深度理解和陪伴）",
            "medium": "中度共情（适度关注和支持）",
            "low": "低度共情（轻松自然的交流）"
        }
        return descriptions.get(empathy_level, "中度共情")
    
    def _get_intensity_description(self, intensity: float) -> str:
        """获取情绪强度描述"""
        if intensity >= 7:
            return f"{intensity}/10 - 高强度情绪，需要深度关注和陪伴"
        elif intensity >= 4:
            return f"{intensity}/10 - 中等强度情绪，适度关注和支持"
        else:
            return f"{intensity}/10 - 低强度情绪，保持轻松自然"
    
    def build_simple_prompt(self, user_input: str, emotion: str) -> str:
        """
        构建简化版Prompt（快速响应用）
        
        Args:
            user_input: 用户输入
            emotion: 情绪类型
            
        Returns:
            简化的Prompt
        """
        strategy = self.emotion_strategy.get(emotion, self.emotion_strategy.get("default", {}))
        
        simple_template = """你是"心语"，一位温暖的心理陪伴者。

当前用户情绪：{emotion_label}
目标：{goal}
语气：{tone}

用户：{user_input}

请用{tone}的语气，生成一段温暖、共情的回复（2-3句话）。

心语："""
        
        return simple_template.format(
            emotion_label=self._get_emotion_label(emotion),
            goal=strategy.get("goal", "提供支持"),
            tone=strategy.get("tone", "温和"),
            user_input=user_input
        )


# 便捷函数
def create_prompt_builder(emotion_strategy: Dict[str, Any]) -> DynamicPromptBuilder:
    """
    创建Prompt构建器实例
    
    Args:
        emotion_strategy: 情感策略配置
        
    Returns:
        DynamicPromptBuilder实例
    """
    return DynamicPromptBuilder(emotion_strategy)


# 测试代码
if __name__ == "__main__":
    import yaml
    
    logging.basicConfig(level=logging.INFO)
    
    # 加载策略配置
    with open("../../config/emotion_strategy.yaml", 'r', encoding='utf-8') as f:
        strategy = yaml.safe_load(f)
    
    # 创建构建器
    builder = DynamicPromptBuilder(strategy)
    
    # 测试用例
    test_input = "我今天工作又被领导批评了，觉得自己一无是处"
    test_emotion = "sad"
    test_intensity = 7.5
    
    # 构建Prompt
    prompt = builder.build_prompt(
        user_input=test_input,
        emotion=test_emotion,
        emotion_intensity=test_intensity,
        conversation_history=[
            {"role": "user", "content": "最近工作压力好大"},
            {"role": "assistant", "content": "我能感受到你的压力。工作确实不容易。"}
        ]
    )
    
    print("===== 动态Prompt示例 =====\n")
    print(prompt)
    print("\n" + "="*50)

