"""
意图识别服务
Intent Recognition Service
"""

from typing import Dict, Any, Optional
import logging

from ..core.intent_classifier import IntentClassifier
from ..core.input_processor import InputProcessor
from ..models.intent_models import IntentResult, IntentRequest

logger = logging.getLogger(__name__)


class IntentService:
    """
    意图识别服务
    整合输入处理、意图识别等功能
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        初始化意图识别服务
        
        Args:
            model_path: ML模型路径（可选）
        """
        self.input_processor = InputProcessor()
        self.intent_classifier = IntentClassifier(model_path)
        logger.info("意图识别服务初始化完成")
    
    def analyze(self, text: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        分析用户输入的意图
        
        Args:
            text: 用户输入文本
            user_id: 用户ID（可选）
            
        Returns:
            分析结果字典，包含：
            - processed: 预处理结果
            - intent: 意图识别结果
            - action_required: 是否需要特殊行动
            - suggestion: 建议的响应策略
        """
        # 1. 输入预处理
        processed = self.input_processor.preprocess(text)
        
        # 2. 如果输入被阻止，直接返回
        if processed["blocked"]:
            return {
                "success": False,
                "processed": processed,
                "intent": None,
                "action_required": False,
                "suggestion": "输入不合规，请修改后重试"
            }
        
        # 3. 意图识别
        intent_result = self.intent_classifier.detect_intent(processed["cleaned"])
        
        # 4. 生成响应建议
        suggestion = self._generate_suggestion(intent_result, processed)
        
        # 5. 判断是否需要特殊行动
        action_required = self._check_action_required(intent_result, processed)
        
        result = {
            "success": True,
            "processed": processed,
            "intent": intent_result.dict(),
            "action_required": action_required,
            "suggestion": suggestion
        }
        
        # 记录日志
        if action_required:
            logger.warning(
                f"用户 {user_id} 需要特殊关注 - 意图: {intent_result.intent}, "
                f"风险等级: {processed['risk_level']}"
            )
        
        return result
    
    def _generate_suggestion(
        self, 
        intent_result: IntentResult, 
        processed: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        根据意图生成响应建议
        
        Args:
            intent_result: 意图识别结果
            processed: 预处理结果
            
        Returns:
            响应建议字典
        """
        from ..models.intent_models import IntentType
        
        # 根据不同意图类型提供不同的响应策略
        suggestions = {
            IntentType.CRISIS: {
                "response_style": "专业、冷静、关怀",
                "priority": "highest",
                "actions": [
                    "提供专业求助热线",
                    "表达关心和支持",
                    "建议寻求专业帮助",
                    "不做价值判断"
                ],
                "avoid": ["说教", "轻视", "劝阻"],
                "prompt_hint": "危机干预模式：需要表现出深切关心，提供实际帮助资源"
            },
            IntentType.EMOTION: {
                "response_style": "共情、温暖、理解",
                "priority": "high",
                "actions": [
                    "积极倾听",
                    "情感验证",
                    "提供情绪宣泄空间",
                    "适当的安慰"
                ],
                "avoid": ["立即给建议", "否定感受"],
                "prompt_hint": "情感陪伴模式：重点在于理解和共情，而非解决问题"
            },
            IntentType.ADVICE: {
                "response_style": "建设性、实用、温和",
                "priority": "medium",
                "actions": [
                    "分析问题",
                    "提供多个选择",
                    "分享相关知识",
                    "鼓励自主决策"
                ],
                "avoid": ["强制建议", "过于复杂"],
                "prompt_hint": "建议提供模式：提供实用建议，但尊重用户选择"
            },
            IntentType.FUNCTION: {
                "response_style": "高效、明确、友好",
                "priority": "medium",
                "actions": [
                    "确认需求",
                    "执行功能",
                    "反馈结果"
                ],
                "avoid": ["冗长", "模糊"],
                "prompt_hint": "功能执行模式：快速准确地完成用户请求"
            },
            IntentType.CHAT: {
                "response_style": "轻松、友好、自然",
                "priority": "low",
                "actions": [
                    "保持对话",
                    "展现亲和力",
                    "适当幽默"
                ],
                "avoid": ["过于正式", "冷漠"],
                "prompt_hint": "闲聊模式：自然友好的日常交流"
            },
            IntentType.CONVERSATION: {
                "response_style": "平衡、自然、贴心",
                "priority": "medium",
                "actions": [
                    "理解上下文",
                    "延续话题",
                    "展现关心"
                ],
                "avoid": ["突兀", "生硬"],
                "prompt_hint": "普通对话模式：保持自然流畅的对话"
            }
        }
        
        return suggestions.get(
            intent_result.intent,
            suggestions[IntentType.CONVERSATION]
        )
    
    def _check_action_required(
        self, 
        intent_result: IntentResult, 
        processed: Dict[str, Any]
    ) -> bool:
        """
        判断是否需要特殊行动
        
        Args:
            intent_result: 意图识别结果
            processed: 预处理结果
            
        Returns:
            是否需要特殊行动
        """
        from ..models.intent_models import IntentType
        
        # 危机情况需要立即行动
        if intent_result.intent == IntentType.CRISIS:
            return True
        
        # 高风险输入需要特别关注
        if processed.get("risk_level") == "high":
            return True
        
        return False
    
    def build_prompt(self, user_context: Dict[str, Any]) -> str:
        """
        构建大模型的prompt
        
        Args:
            user_context: 用户上下文，包含情感和意图分析结果
            
        Returns:
            构建好的prompt字符串
        """
        # 提取情感和意图信息
        emotion = user_context.get("analysis", {}).get("emotion", {}).get("primary", "平静")
        intent_data = user_context.get("analysis", {}).get("intent", {})
        intent = intent_data.get("intent", "conversation")
        
        # 获取响应建议
        from ..models.intent_models import IntentType
        try:
            intent_type = IntentType(intent)
        except ValueError:
            intent_type = IntentType.CONVERSATION
        
        # 创建一个临时的IntentResult用于生成建议
        from ..models.intent_models import IntentResult
        intent_result = IntentResult(
            intent=intent_type,
            confidence=intent_data.get("confidence", 0.5),
            source=intent_data.get("source", "unknown")
        )
        
        suggestion = self._generate_suggestion(
            intent_result,
            {"risk_level": "low"}
        )
        
        # 构建prompt
        base_prompt = f"""
你是一位温暖、耐心的心理陪伴助手"心语"。请根据用户的情绪和意图，给予恰当的回应。

【用户状态分析】
- 当前情绪：{emotion}
- 主要意图：{intent}
- 响应风格：{suggestion.get('response_style', '温和、理解')}

【响应指导】
- 优先行动：{', '.join(suggestion.get('actions', [])[:3])}
- 避免：{', '.join(suggestion.get('avoid', []))}
- 提示：{suggestion.get('prompt_hint', '以用户为中心，提供支持和理解')}

【基本原则】
1. 用自然、口语化的方式回应，避免说教
2. 展现真诚的关心和理解
3. 尊重用户的感受和选择
4. 在必要时提供实用的建议或资源

请根据以上分析，给出温暖、恰当的回应。
"""
        
        return base_prompt.strip()

