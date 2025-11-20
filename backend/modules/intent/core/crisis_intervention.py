#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
危机干预模块 - 精简版（课程展示用）
Crisis Intervention Module - Core Version

功能：
- 检测高风险情绪（自残、抑郁重度等）
- 触发预设的危机干预话术
- 引导用户寻求专业帮助

注意：此版本为精简版，仅保留核心逻辑。
完整版本（包含详细日志、多级风险评估、动态话术生成等）请参考：
https://github.com/your-repo/emotional_chat/blob/main/backend/modules/intent/core/crisis_intervention_full.py
"""

import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class CrisisIntervention:
    """危机干预处理器 - 核心版"""
    
    # 高风险关键词（核心部分）
    HIGH_RISK_KEYWORDS = [
        "不想活了", "自杀", "自残", "结束生命", "离开这个世界",
        "重度抑郁", "绝望", "没有希望", "活着没意思"
    ]
    
    # 危机干预热线（核心部分）
    CRISIS_HOTLINES = [
        {"name": "希望24热线", "number": "400-161-9995"},
        {"name": "北京心理危机干预中心", "number": "010-82951332"},
        {"name": "生命热线", "number": "400-821-1215"}
    ]
    
    def __init__(self, emotion_strategy: Optional[Dict] = None):
        """
        初始化危机干预处理器
        
        Args:
            emotion_strategy: 情感策略配置（可选）
        """
        self.emotion_strategy = emotion_strategy or {}
        logger.info("✓ 危机干预模块已初始化（精简版）")
    
    def is_crisis_situation(self, 
                           user_emotion: str,
                           user_input: str = "",
                           metadata: Optional[Dict] = None) -> bool:
        """
        判断是否为危机情况（核心逻辑）
        
        Args:
            user_emotion: 用户情绪类型
            user_input: 用户输入文本
            metadata: 元数据（可能包含风险标记）
            
        Returns:
            是否为危机情况
        """
        # 1. 情绪类型判断
        if user_emotion == "high_risk_depression":
            return True
        
        # 2. 元数据标记判断
        if metadata and metadata.get("requires_crisis_intervention"):
            return True
        
        # 3. 高风险关键词检测
        if user_input:
            user_input_lower = user_input.lower()
            for keyword in self.HIGH_RISK_KEYWORDS:
                if keyword in user_input_lower:
                    logger.warning(f"⚠️ 检测到高风险关键词: {keyword}")
                    return True
        
        return False
    
    def generate_crisis_response(self, 
                                user_input: str = "",
                                user_emotion: str = "high_risk_depression") -> str:
        """
        生成危机干预回复（核心逻辑）
        
        Args:
            user_input: 用户输入（可选）
            user_emotion: 用户情绪
            
        Returns:
            危机干预回复文本
        """
        # 从策略配置获取预设回复
        crisis_strategy = self.emotion_strategy.get("high_risk_depression", {})
        fallback_response = crisis_strategy.get("fallback", "")
        
        if fallback_response:
            return fallback_response
        
        # 默认危机干预回复（核心模板）
        hotlines_text = "\n".join([
            f"- {hl['name']}：{hl['number']}" 
            for hl in self.CRISIS_HOTLINES
        ])
        
        response = f"""我非常关心你现在的情绪状态。你不是一个人，有很多人愿意帮助你。

建议你立即联系心理援助热线：
{hotlines_text}

我会一直在这里陪你。"""
        
        return response
    
    def get_crisis_hotlines(self) -> List[Dict[str, str]]:
        """
        获取危机干预热线列表
        
        Returns:
            热线列表
        """
        # 优先使用配置中的热线
        strategy_hotlines = self.emotion_strategy.get("high_risk_depression", {}).get("crisis_hotlines", [])
        return strategy_hotlines if strategy_hotlines else self.CRISIS_HOTLINES


# 便捷函数
def check_crisis(user_emotion: str, 
                user_input: str = "",
                metadata: Optional[Dict] = None) -> bool:
    """
    便捷函数：检查是否为危机情况
    
    Args:
        user_emotion: 用户情绪
        user_input: 用户输入
        metadata: 元数据
        
    Returns:
        是否为危机情况
    """
    intervention = CrisisIntervention()
    return intervention.is_crisis_situation(user_emotion, user_input, metadata)


def get_crisis_response(user_input: str = "",
                       user_emotion: str = "high_risk_depression",
                       emotion_strategy: Optional[Dict] = None) -> str:
    """
    便捷函数：获取危机干预回复
    
    Args:
        user_input: 用户输入
        user_emotion: 用户情绪
        emotion_strategy: 情感策略配置
        
    Returns:
        危机干预回复
    """
    intervention = CrisisIntervention(emotion_strategy)
    return intervention.generate_crisis_response(user_input, user_emotion)


# 测试代码
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 测试用例
    test_cases = [
        {
            "user_input": "我真的不想活了",
            "user_emotion": "sad",
            "expected_crisis": True
        },
        {
            "user_input": "今天心情不太好",
            "user_emotion": "sad",
            "expected_crisis": False
        },
        {
            "user_input": "",
            "user_emotion": "high_risk_depression",
            "expected_crisis": True
        }
    ]
    
    print("\n===== 危机干预测试（精简版）=====\n")
    
    intervention = CrisisIntervention()
    
    for i, test in enumerate(test_cases, 1):
        is_crisis = intervention.is_crisis_situation(
            user_emotion=test["user_emotion"],
            user_input=test["user_input"]
        )
        
        status = "✓" if is_crisis == test["expected_crisis"] else "✗"
        print(f"{status} 测试 {i}:")
        print(f"   输入: {test['user_input'] or '(空)'}")
        print(f"   情绪: {test['user_emotion']}")
        print(f"   判断: {'危机' if is_crisis else '非危机'}")
        
        if is_crisis:
            response = intervention.generate_crisis_response(
                test["user_input"],
                test["user_emotion"]
            )
            print(f"   回复: {response[:100]}...")
        print()

