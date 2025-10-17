"""
规则引擎 - 基于关键词的快速意图识别
Rule-Based Intent Engine for fast pattern matching
"""

import re
from typing import Dict, List, Optional, Tuple
from ..models.intent_models import IntentType, IntentResult


class RuleBasedIntentEngine:
    """基于规则的意图识别引擎"""
    
    # 意图关键词规则表
    INTENT_RULES: Dict[IntentType, List[str]] = {
        IntentType.CRISIS: [
            "不想活", "自杀", "结束生命", "撑不下去", "想死",
            "自残", "割腕", "跳楼", "了结", "没有意义",
            "活着很累", "不想继续", "解脱"
        ],
        IntentType.ADVICE: [
            "怎么办", "建议", "怎么处理", "你觉得", "该如何",
            "怎样才能", "有什么办法", "能不能给", "帮我想想",
            "有没有好的", "应该怎么", "请问"
        ],
        IntentType.FUNCTION: [
            "提醒我", "记得", "别忘了", "设置闹钟", "定时",
            "记录", "保存", "提醒", "备忘", "日程",
            "帮我记", "创建提醒", "添加事项"
        ],
        IntentType.CHAT: [
            "你好", "早上好", "晚上好", "hi", "hello",
            "在吗", "你是谁", "你叫什么", "天气",
            "谢谢", "再见", "拜拜", "哈哈", "😊"
        ],
        IntentType.EMOTION: [
            "好难过", "很伤心", "很焦虑", "好压抑", "很生气",
            "委屈", "郁闷", "烦躁", "孤独", "失落",
            "心情不好", "不开心", "很累", "疲惫"
        ],
    }
    
    # 危机关键词的权重更高
    CRISIS_PATTERNS = [
        r"(不想|不要|别).*活",
        r"自杀|轻生",
        r"结束.*生命",
        r"撑不.*下去",
    ]
    
    def __init__(self):
        """初始化规则引擎"""
        # 编译正则表达式以提高性能
        self.crisis_regex = [re.compile(pattern) for pattern in self.CRISIS_PATTERNS]
    
    def detect_intent(self, text: str) -> Optional[IntentResult]:
        """
        使用规则检测意图
        
        Args:
            text: 输入文本
            
        Returns:
            IntentResult 或 None（无匹配规则时）
        """
        text = text.lower().strip()
        
        # 优先检查危机关键词（安全第一）
        if self._check_crisis(text):
            return IntentResult(
                intent=IntentType.CRISIS,
                confidence=1.0,
                source="rule",
                metadata={
                    "priority": "highest",
                    "action_required": "immediate_intervention"
                }
            )
        
        # 检查其他意图
        for intent, keywords in self.INTENT_RULES.items():
            if intent == IntentType.CRISIS:
                continue  # 已经检查过
            
            matched_keywords = [kw for kw in keywords if kw in text]
            if matched_keywords:
                # 计算置信度（根据匹配关键词数量）
                confidence = min(0.8 + len(matched_keywords) * 0.1, 1.0)
                
                return IntentResult(
                    intent=intent,
                    confidence=confidence,
                    source="rule",
                    metadata={
                        "matched_keywords": matched_keywords
                    }
                )
        
        # 无规则匹配
        return None
    
    def _check_crisis(self, text: str) -> bool:
        """
        检查是否包含危机关键词
        
        Args:
            text: 输入文本（已转小写）
            
        Returns:
            是否为危机情况
        """
        # 关键词匹配
        crisis_keywords = self.INTENT_RULES.get(IntentType.CRISIS, [])
        for keyword in crisis_keywords:
            if keyword in text:
                return True
        
        # 正则表达式匹配（更复杂的模式）
        for regex in self.crisis_regex:
            if regex.search(text):
                return True
        
        return False
    
    def get_matched_keywords(self, text: str, intent: IntentType) -> List[str]:
        """
        获取文本中匹配的关键词
        
        Args:
            text: 输入文本
            intent: 意图类型
            
        Returns:
            匹配的关键词列表
        """
        text = text.lower()
        keywords = self.INTENT_RULES.get(intent, [])
        return [kw for kw in keywords if kw in text]

