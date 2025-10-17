"""
输入预处理器 - 文本清洗和安全过滤
Input Processor for text cleaning and safety filtering
"""

import re
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class InputProcessor:
    """输入预处理器"""
    
    # 高风险词汇（需要特别注意）
    HIGH_RISK_KEYWORDS = [
        "自杀", "自残", "割腕", "跳楼", "服药", "了结",
        "不想活", "想死", "结束生命"
    ]
    
    # 敏感词汇（需要过滤或替换）
    SENSITIVE_WORDS = [
        # 这里可以添加需要过滤的敏感词
    ]
    
    def __init__(self):
        """初始化输入处理器"""
        pass
    
    def preprocess(self, text: str) -> Dict[str, any]:
        """
        预处理输入文本
        
        Args:
            text: 原始输入文本
            
        Returns:
            处理结果字典，包含：
            - raw: 原始文本
            - cleaned: 清洗后的文本
            - blocked: 是否被阻止
            - risk_level: 风险等级（low/medium/high）
            - warnings: 警告信息列表
        """
        result = {
            "raw": text,
            "cleaned": text,
            "blocked": False,
            "risk_level": "low",
            "warnings": []
        }
        
        # 1. 基本清洗
        cleaned = self._basic_clean(text)
        result["cleaned"] = cleaned
        
        # 2. 检查空输入
        if not cleaned.strip():
            result["blocked"] = True
            result["warnings"].append("输入为空")
            return result
        
        # 3. 长度检查
        if len(cleaned) > 2000:
            result["warnings"].append("输入文本过长，已截断")
            result["cleaned"] = cleaned[:2000]
        
        # 4. 高风险检测
        risk_detected = self._check_high_risk(cleaned)
        if risk_detected:
            result["risk_level"] = "high"
            result["warnings"].append("检测到高风险内容")
            logger.warning(f"高风险输入检测: {cleaned[:50]}...")
        
        # 5. 敏感词过滤
        result["cleaned"] = self._filter_sensitive_words(result["cleaned"])
        
        return result
    
    def _basic_clean(self, text: str) -> str:
        """
        基本文本清洗
        
        Args:
            text: 原始文本
            
        Returns:
            清洗后的文本
        """
        # 去除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 去除特殊控制字符
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        # 统一标点符号
        text = text.replace('…', '...')
        
        # 去除首尾空白
        text = text.strip()
        
        return text
    
    def _check_high_risk(self, text: str) -> bool:
        """
        检查是否包含高风险关键词
        
        Args:
            text: 文本
            
        Returns:
            是否为高风险
        """
        text_lower = text.lower()
        for keyword in self.HIGH_RISK_KEYWORDS:
            if keyword in text_lower:
                return True
        return False
    
    def _filter_sensitive_words(self, text: str) -> str:
        """
        过滤敏感词
        
        Args:
            text: 文本
            
        Returns:
            过滤后的文本
        """
        # 这里可以实现敏感词替换逻辑
        # 例如：将敏感词替换为 ***
        for word in self.SENSITIVE_WORDS:
            if word in text:
                text = text.replace(word, "*" * len(word))
        
        return text
    
    def validate_input(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        验证输入是否合规
        
        Args:
            text: 输入文本
            
        Returns:
            (是否合规, 错误信息)
        """
        if not text or not text.strip():
            return False, "输入不能为空"
        
        if len(text) > 5000:
            return False, "输入文本过长（最大5000字符）"
        
        # 检查是否只包含特殊字符
        if re.match(r'^[\W_]+$', text):
            return False, "输入内容无效"
        
        return True, None

