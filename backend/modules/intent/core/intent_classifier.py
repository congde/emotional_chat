"""
意图分类器 - 混合式意图识别（规则+模型）
Intent Classifier with hybrid approach (rule-based + ML)
"""

from typing import Dict, Optional, List
import logging

from ..models.intent_models import IntentType, IntentResult
from .rule_engine import RuleBasedIntentEngine

logger = logging.getLogger(__name__)


class MLIntentClassifier:
    """
    机器学习意图分类器（基于BERT）
    
    注意：这里提供了接口框架，实际的BERT模型需要单独训练
    可以使用 transformers 库的 AutoModelForSequenceClassification
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        初始化ML分类器
        
        Args:
            model_path: 预训练模型路径（可选）
        """
        self.model_path = model_path or "intent_bert_model"
        self.labels = [
            IntentType.EMOTION,
            IntentType.ADVICE,
            IntentType.CHAT,
            IntentType.FUNCTION,
            IntentType.CRISIS,
            IntentType.CONVERSATION
        ]
        
        # 模型加载（如果有训练好的模型）
        self.model = None
        self.tokenizer = None
        self._load_model()
    
    def _load_model(self):
        """加载预训练模型"""
        try:
            # 这里可以集成真实的BERT模型
            # from transformers import AutoTokenizer, AutoModelForSequenceClassification
            # self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            # self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
            logger.info("ML模型加载成功（当前为模拟模式）")
        except Exception as e:
            logger.warning(f"ML模型加载失败，将使用模拟预测: {e}")
    
    def classify(self, text: str) -> IntentResult:
        """
        使用机器学习模型分类意图
        
        Args:
            text: 输入文本
            
        Returns:
            意图识别结果
        """
        # 如果有真实模型，使用模型预测
        if self.model is not None and self.tokenizer is not None:
            return self._predict_with_model(text)
        else:
            # 使用启发式规则模拟（简化版）
            return self._heuristic_classify(text)
    
    def _predict_with_model(self, text: str) -> IntentResult:
        """
        使用训练好的BERT模型进行预测
        
        Args:
            text: 输入文本
            
        Returns:
            意图识别结果
        """
        # TODO: 实现真实的模型推理
        # inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
        # with torch.no_grad():
        #     logits = self.model(**inputs).logits
        # probs = torch.softmax(logits, dim=1)[0]
        # pred = torch.argmax(probs).item()
        # 
        # return IntentResult(
        #     intent=self.labels[pred],
        #     confidence=probs[pred].item(),
        #     source="model"
        # )
        pass
    
    def _heuristic_classify(self, text: str) -> IntentResult:
        """
        启发式分类（当无可用模型时的备选方案）
        
        Args:
            text: 输入文本
            
        Returns:
            意图识别结果
        """
        text_lower = text.lower()
        
        # 简单的启发式规则
        if any(word in text_lower for word in ["怎么办", "建议", "如何", "怎样"]):
            return IntentResult(
                intent=IntentType.ADVICE,
                confidence=0.75,
                source="model",
                metadata={"method": "heuristic"}
            )
        elif any(word in text_lower for word in ["提醒", "记得", "别忘"]):
            return IntentResult(
                intent=IntentType.FUNCTION,
                confidence=0.70,
                source="model",
                metadata={"method": "heuristic"}
            )
        elif any(word in text_lower for word in ["难过", "伤心", "焦虑", "压抑", "生气"]):
            return IntentResult(
                intent=IntentType.EMOTION,
                confidence=0.80,
                source="model",
                metadata={"method": "heuristic"}
            )
        elif any(word in text_lower for word in ["你好", "早上好", "hi", "在吗"]):
            return IntentResult(
                intent=IntentType.CHAT,
                confidence=0.85,
                source="model",
                metadata={"method": "heuristic"}
            )
        else:
            # 默认为普通对话
            return IntentResult(
                intent=IntentType.CONVERSATION,
                confidence=0.60,
                source="model",
                metadata={"method": "heuristic"}
            )


class IntentClassifier:
    """
    混合式意图分类器
    整合规则引擎和机器学习模型
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        初始化意图分类器
        
        Args:
            model_path: ML模型路径（可选）
        """
        self.rule_engine = RuleBasedIntentEngine()
        self.ml_classifier = MLIntentClassifier(model_path)
        logger.info("意图分类器初始化完成（混合模式：规则+模型）")
    
    def detect_intent(self, text: str) -> IntentResult:
        """
        检测用户意图（融合策略）
        
        策略：
        1. 优先使用规则引擎检测危机情况（安全第一）
        2. 如果规则引擎有高置信度匹配，使用规则结果
        3. 否则使用ML模型进行预测
        
        Args:
            text: 输入文本
            
        Returns:
            意图识别结果
        """
        if not text or not text.strip():
            return IntentResult(
                intent=IntentType.CONVERSATION,
                confidence=0.5,
                source="default",
                metadata={"reason": "empty_input"}
            )
        
        # 1. 优先检查危机关键词（安全第一）
        rule_result = self.rule_engine.detect_intent(text)
        if rule_result and rule_result.intent == IntentType.CRISIS:
            logger.warning(f"检测到危机意图：{text[:50]}...")
            return rule_result
        
        # 2. 如果规则引擎有高置信度匹配（>0.85），使用规则结果
        if rule_result and rule_result.confidence > 0.85:
            return rule_result
        
        # 3. 使用ML模型预测
        ml_result = self.ml_classifier.classify(text)
        
        # 4. 如果规则和模型都有结果，进行融合
        if rule_result:
            # 如果规则和模型预测一致，提高置信度
            if rule_result.intent == ml_result.intent:
                ml_result.confidence = min(ml_result.confidence + 0.1, 1.0)
                ml_result.metadata = ml_result.metadata or {}
                ml_result.metadata["rule_confirmed"] = True
            else:
                # 如果不一致，记录次要意图
                ml_result.secondary_intents = {
                    rule_result.intent: rule_result.confidence
                }
        
        return ml_result
    
    def batch_detect(self, texts: List[str]) -> List[IntentResult]:
        """
        批量检测意图
        
        Args:
            texts: 文本列表
            
        Returns:
            意图结果列表
        """
        return [self.detect_intent(text) for text in texts]

