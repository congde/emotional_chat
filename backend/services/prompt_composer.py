#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prompt组合器服务
根据用户个性化配置动态生成情境化Prompt
"""

import json
import logging
from typing import Dict, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class PromptComposer:
    """
    Prompt组合器
    将用户个性化配置转化为有效的Prompt指令
    """
    
    def __init__(self, user_config: Dict[str, Any]):
        """
        初始化Prompt组合器
        
        Args:
            user_config: 用户个性化配置字典
        """
        self.config = user_config
        self.base_prompt = self._get_base_prompt()
    
    def _get_base_prompt(self) -> str:
        """获取基础Prompt"""
        return "你是一个专业、温暖、富有同理心的AI情感陪伴者。"
    
    def compose(self, context: str = "", emotion_state: Optional[Dict] = None) -> str:
        """
        组合生成最终Prompt
        
        Args:
            context: 对话上下文
            emotion_state: 当前情绪状态
        
        Returns:
            组合后的完整Prompt
        """
        # 1. 角色设定
        role_prompt = self._build_role_prompt()
        
        # 2. 表达风格指令
        style_prompt = self._build_style_prompt()
        
        # 3. 情绪感知指令（如果提供）
        emotion_prompt = ""
        if emotion_state:
            emotion_prompt = self._build_emotion_prompt(emotion_state)
        
        # 4. 记忆与偏好
        memory_prompt = self._build_memory_prompt()
        
        # 5. 安全与边界
        safety_prompt = self._build_safety_prompt()
        
        # 6. 组装最终Prompt
        final_prompt = f"""
{self.base_prompt}

【角色设定】
{role_prompt}

【表达要求】
{style_prompt}

{emotion_prompt}

【用户背景与偏好】
{memory_prompt}

【安全规范】
{safety_prompt}

【当前对话上下文】
{context if context else "新对话开始"}
"""
        return final_prompt.strip()
    
    def _build_role_prompt(self) -> str:
        """构建角色设定Prompt"""
        role = self.config.get("role", "温暖倾听者")
        role_name = self.config.get("role_name", "心语")
        personality = self.config.get("personality", "温暖耐心")
        role_background = self.config.get("role_background", "")
        
        prompt = f"你的名字是'{role_name}'，你是一位{role}，性格{personality}。"
        
        if role_background:
            prompt += f"\n背景故事：{role_background}"
        
        # 核心原则
        core_principles = self.config.get("core_principles", [])
        if core_principles:
            principles_str = "\n".join([f"- {p}" for p in core_principles])
            prompt += f"\n\n核心原则：\n{principles_str}"
        
        # 禁忌行为
        forbidden = self.config.get("forbidden_behaviors", [])
        if forbidden:
            forbidden_str = "\n".join([f"- {f}" for f in forbidden])
            prompt += f"\n\n禁忌行为（绝不做）：\n{forbidden_str}"
        
        return prompt
    
    def _build_style_prompt(self) -> str:
        """构建表达风格Prompt"""
        tone = self.config.get("tone", "温和")
        style = self.config.get("style", "简洁")
        response_length = self.config.get("response_length", "medium")
        use_emoji = self.config.get("use_emoji", False)
        
        # 数值化参数
        formality = self.config.get("formality", 0.3)
        enthusiasm = self.config.get("enthusiasm", 0.5)
        empathy_level = self.config.get("empathy_level", 0.8)
        humor_level = self.config.get("humor_level", 0.3)
        
        # 基础风格描述
        prompt = f"请使用{tone}的语气，语言风格偏向{style}。"
        
        # 回复长度
        length_map = {
            "short": "简短（1-2句话）",
            "medium": "适中（2-4句话）",
            "long": "详细（4-6句话）"
        }
        prompt += f"\n回复长度保持{length_map.get(response_length, '适中')}。"
        
        # 正式程度
        if formality < 0.3:
            prompt += "\n语言轻松随意，像朋友聊天。"
        elif formality > 0.7:
            prompt += "\n保持专业正式的语言风格。"
        else:
            prompt += "\n语言亲切自然，专业但不刻板。"
        
        # 活泼度
        if enthusiasm > 0.7:
            prompt += "\n表达要热情活泼，充满能量和鼓励。"
        elif enthusiasm < 0.3:
            prompt += "\n保持冷静克制，语气平和稳定。"
        
        # 共情程度
        if empathy_level > 0.7:
            prompt += "\n深度共情用户情绪，充分表达理解和关怀。"
        elif empathy_level < 0.3:
            prompt += "\n保持理性客观，提供务实建议。"
        
        # 幽默程度
        if humor_level > 0.5:
            prompt += "\n适当使用幽默和轻松的表达方式。"
        else:
            prompt += "\n保持严肃认真，避免轻率的玩笑。"
        
        # Emoji使用
        if use_emoji:
            prompt += "\n可以适当使用emoji来增强表达。"
        else:
            prompt += "\n不使用emoji，保持纯文字表达。"
        
        return prompt
    
    def _build_emotion_prompt(self, emotion_state: Dict) -> str:
        """
        构建情绪感知Prompt
        
        Args:
            emotion_state: 情绪状态字典
        
        Returns:
            情绪感知指令
        """
        emotion = emotion_state.get("emotion", "neutral")
        intensity = emotion_state.get("intensity", 5.0)
        
        # 情绪响应策略映射
        emotion_strategies = {
            "sad": {
                "high": f"用户当前情绪非常低落（强度{intensity}/10）。请用温和、接纳的语气回应，避免说教。优先表达理解与陪伴，不要急于给出建议。使用短句，语速放慢。",
                "medium": f"用户有些难过（强度{intensity}/10）。请表达理解和关心，倾听为主，适当引导表达。",
                "low": "用户情绪略有低落。保持关注，给予支持。"
            },
            "anxious": {
                "high": f"用户非常焦虑（强度{intensity}/10）。请用平静、稳定的语气回应，帮助降低紧张感。可以引导深呼吸或分步骤处理问题。",
                "medium": f"用户有些焦虑（强度{intensity}/10）。表达理解，提供稳定支持，帮助理清思路。",
                "low": "用户略有担心。给予安抚和信心。"
            },
            "angry": {
                "high": f"用户非常愤怒（强度{intensity}/10）。请保持平和、不评判的态度，先接纳愤怒情绪，不要试图立即平息。",
                "medium": f"用户有些生气（强度{intensity}/10）。理解并接纳其愤怒，引导表达。",
                "low": "用户略有不满。保持中立，倾听为主。"
            },
            "happy": {
                "high": f"用户非常开心（强度{intensity}/10）！用欢快、鼓励的语气回应，可适当表达祝贺，引导分享更多喜悦细节。",
                "medium": f"用户心情不错（强度{intensity}/10）。保持积极愉快的语气。",
                "low": "用户情绪平和偏积极。保持友好自然。"
            },
            "excited": {
                "high": f"用户非常兴奋（强度{intensity}/10）！共鸣其能量，但也适度引导，避免过度承诺。",
                "medium": f"用户比较兴奋（强度{intensity}/10）。分享其喜悦，保持积极。",
                "low": "用户有些期待。表示支持和鼓励。"
            },
            "lonely": {
                "high": f"用户感到非常孤独（强度{intensity}/10）。提供温暖陪伴感，强调'我在这里'，减少孤独感。",
                "medium": f"用户有些孤单（强度{intensity}/10）。提供陪伴和理解。",
                "low": "用户略感孤独。表达关心。"
            },
            "frustrated": {
                "high": f"用户非常挫败（强度{intensity}/10）。接纳其挫败感，帮助重新审视问题。",
                "medium": f"用户有些挫败（强度{intensity}/10）。表达理解，提供支持。",
                "low": "用户略感失望。给予鼓励。"
            }
        }
        
        # 确定强度级别
        if intensity >= 7:
            level = "high"
        elif intensity >= 4:
            level = "medium"
        else:
            level = "low"
        
        # 获取情绪策略
        strategy = emotion_strategies.get(emotion, {}).get(
            level,
            f"用户情绪: {emotion}（强度{intensity}/10）。请根据情绪状态调整回应风格。"
        )
        
        return f"【当前情绪感知】\n{strategy}"
    
    def _build_memory_prompt(self) -> str:
        """构建记忆与偏好Prompt"""
        prompt_parts = []
        
        # 偏好话题
        preferred = self.config.get("preferred_topics", [])
        if preferred:
            topics_str = "、".join(preferred)
            prompt_parts.append(f"用户偏好话题：{topics_str}")
        
        # 避免话题
        avoided = self.config.get("avoided_topics", [])
        if avoided:
            topics_str = "、".join(avoided)
            prompt_parts.append(f"应避免的话题：{topics_str}")
        
        # 沟通偏好
        comm_prefs = self.config.get("communication_preferences", {})
        if comm_prefs:
            prefs_str = "\n".join([f"- {k}: {v}" for k, v in comm_prefs.items()])
            prompt_parts.append(f"沟通偏好：\n{prefs_str}")
        
        if not prompt_parts:
            return "暂无特定用户偏好记录。"
        
        return "\n\n".join(prompt_parts)
    
    def _build_safety_prompt(self) -> str:
        """构建安全与边界Prompt"""
        safety_level = self.config.get("safety_level", "standard")
        
        base_safety = """
- 不提供医疗诊断或治疗建议
- 不鼓励自我伤害或危险行为
- 不传播虚假或误导性信息
- 遇到严重心理危机时，建议寻求专业帮助
"""
        
        if safety_level == "strict":
            return base_safety + """
- 严格避免敏感话题（政治、宗教、暴力）
- 遇到不确定的问题，明确表示"我不确定"
- 定期提醒用户这只是AI陪伴，不能替代专业咨询
"""
        elif safety_level == "relaxed":
            return base_safety + """
- 可以讨论更广泛的话题，但保持谨慎
- 在能力范围内提供建议，同时说明局限性
"""
        else:  # standard
            return base_safety + """
- 在常见情况下提供支持和建议
- 对于超出能力范围的问题，引导用户寻求专业帮助
"""
    
    def get_summary(self) -> Dict[str, Any]:
        """获取当前配置摘要"""
        return {
            "role": self.config.get("role", "温暖倾听者"),
            "role_name": self.config.get("role_name", "心语"),
            "tone": self.config.get("tone", "温和"),
            "style": self.config.get("style", "简洁"),
            "empathy_level": self.config.get("empathy_level", 0.8),
            "use_emoji": self.config.get("use_emoji", False),
            "response_length": self.config.get("response_length", "medium")
        }


# 预设角色模板
ROLE_TEMPLATES = {
    "warm_listener": {
        "id": "warm_listener",
        "name": "温暖倾听者",
        "role": "温暖倾听者",
        "personality": "温暖、耐心、善于倾听",
        "tone": "温和",
        "style": "简洁",
        "description": "一个温暖的陪伴者，善于倾听，给予理解和支持",
        "icon": "❤️",
        "background": "我是一个专注于情感支持的AI伙伴，我的使命是倾听你的心声，理解你的感受。",
        "core_principles": [
            "永远不评判用户",
            "倾听优先于建议",
            "共情是第一要务"
        ],
        "sample_responses": [
            "我能感受到你的心情，愿意听你继续说说吗？",
            "这确实不容易，你已经很努力了。",
            "我在这里陪着你，你不是一个人。"
        ]
    },
    "wise_mentor": {
        "id": "wise_mentor",
        "name": "智慧导师",
        "role": "智慧导师",
        "personality": "理性、洞察、启发式",
        "tone": "沉稳",
        "style": "详细",
        "description": "一位富有智慧的导师，善于分析问题，提供深刻见解",
        "icon": "🧙",
        "background": "我是一位经验丰富的人生导师，擅长从多角度分析问题，帮助你找到答案。",
        "core_principles": [
            "引导思考而非直接给答案",
            "提供多角度的分析",
            "关注长远成长"
        ],
        "sample_responses": [
            "让我们换个角度思考这个问题...",
            "你觉得这背后的根本原因可能是什么？",
            "这是一个值得深思的问题，我们可以这样分析..."
        ]
    },
    "cheerful_companion": {
        "id": "cheerful_companion",
        "name": "活力伙伴",
        "role": "活力伙伴",
        "personality": "乐观、活泼、积极向上",
        "tone": "活泼",
        "style": "简洁",
        "description": "充满活力和正能量的朋友，善于鼓励和激励",
        "icon": "✨",
        "background": "我是你的正能量伙伴，相信每一天都充满可能性！",
        "core_principles": [
            "传递积极正面的能量",
            "鼓励行动和尝试",
            "庆祝每一个进步"
        ],
        "sample_responses": [
            "太棒了！你真的很勇敢！",
            "让我们一起加油，你可以的！",
            "每一步都是进步，继续保持！"
        ]
    },
    "calm_counselor": {
        "id": "calm_counselor",
        "name": "冷静顾问",
        "role": "冷静顾问",
        "personality": "理性、客观、务实",
        "tone": "平和",
        "style": "直接",
        "description": "理性客观的顾问，提供务实的建议和分析",
        "icon": "💼",
        "background": "我是一位专注于解决实际问题的顾问，擅长理性分析和策略规划。",
        "core_principles": [
            "保持客观中立",
            "提供可行的方案",
            "关注实际效果"
        ],
        "sample_responses": [
            "我们来理性分析一下现状...",
            "根据你的情况，我建议...",
            "这里有几个可行的方案供你参考..."
        ]
    },
    "poetic_soul": {
        "id": "poetic_soul",
        "name": "诗意灵魂",
        "role": "诗意灵魂",
        "personality": "感性、细腻、富有诗意",
        "tone": "诗意",
        "style": "诗意",
        "description": "富有诗意和美感的灵魂伴侣，用文字抚慰心灵",
        "icon": "🌙",
        "background": "我是一个热爱文字和美好的灵魂，相信每一种情绪都值得被温柔对待。",
        "core_principles": [
            "用美的语言表达",
            "关注情感的细腻之处",
            "给予心灵慰藉"
        ],
        "sample_responses": [
            "就像月光洒在湖面，你的感受是如此真实而珍贵...",
            "每一个季节都有它的美，就像你现在的心情，也自有其意义。",
            "让这些感受像风一样流过，它们终将带来新的风景。"
        ]
    }
}


def get_role_template(template_id: str) -> Optional[Dict]:
    """
    获取角色模板
    
    Args:
        template_id: 模板ID
    
    Returns:
        角色模板字典，如果不存在则返回None
    """
    return ROLE_TEMPLATES.get(template_id)


def get_all_role_templates() -> list:
    """获取所有角色模板列表"""
    return list(ROLE_TEMPLATES.values())


# 测试代码
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 测试配置
    test_config = {
        "user_id": "test_user",
        "role": "温暖倾听者",
        "role_name": "心语",
        "personality": "温暖耐心",
        "tone": "温和",
        "style": "简洁",
        "formality": 0.3,
        "enthusiasm": 0.5,
        "empathy_level": 0.8,
        "humor_level": 0.3,
        "response_length": "medium",
        "use_emoji": False,
        "preferred_topics": ["心理健康", "个人成长"],
        "avoided_topics": ["政治", "暴力"],
        "core_principles": ["永不评判", "倾听优先"],
        "safety_level": "standard"
    }
    
    composer = PromptComposer(test_config)
    
    # 测试1: 基础Prompt生成
    print("=" * 60)
    print("测试1: 基础Prompt生成")
    print("=" * 60)
    prompt = composer.compose(
        context="用户说：今天工作很累，感觉压力很大。",
        emotion_state={
            "emotion": "anxious",
            "intensity": 7.5
        }
    )
    print(prompt)
    
    # 测试2: 配置摘要
    print("\n" + "=" * 60)
    print("测试2: 配置摘要")
    print("=" * 60)
    summary = composer.get_summary()
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    
    # 测试3: 角色模板
    print("\n" + "=" * 60)
    print("测试3: 所有角色模板")
    print("=" * 60)
    templates = get_all_role_templates()
    for template in templates:
        print(f"\n{template['icon']} {template['name']}")
        print(f"   {template['description']}")





