"""
意图识别数据模型
Intent Recognition Data Models
"""

from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class IntentType(str, Enum):
    """用户意图类型枚举"""
    EMOTION = "emotion"          # 情感表达（倾诉、抱怨）
    ADVICE = "advice"            # 寻求建议
    CONVERSATION = "conversation"  # 普通对话
    FUNCTION = "function"        # 功能请求（提醒、记录）
    CRISIS = "crisis"            # 危机干预（自杀、自残）
    CHAT = "chat"                # 闲聊（打招呼、寒暄）


class IntentResult(BaseModel):
    """意图识别结果"""
    intent: IntentType = Field(..., description="识别的意图类型")
    confidence: float = Field(..., ge=0.0, le=1.0, description="置信度（0-1）")
    source: str = Field(..., description="识别来源：rule（规则）或 model（模型）")
    secondary_intents: Optional[Dict[IntentType, float]] = Field(
        default=None, 
        description="次要意图及其置信度"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="额外的元数据信息"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "intent": "advice",
                "confidence": 0.92,
                "source": "model",
                "secondary_intents": {
                    "emotion": 0.65
                },
                "metadata": {
                    "keywords": ["怎么办", "建议"]
                }
            }
        }


class IntentRequest(BaseModel):
    """意图识别请求"""
    text: str = Field(..., min_length=1, description="待识别的文本")
    user_id: Optional[str] = Field(default=None, description="用户ID")
    session_id: Optional[str] = Field(default=None, description="会话ID")
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="上下文信息"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text": "我最近总是睡不着，该怎么办？",
                "user_id": "user_123",
                "session_id": "session_456"
            }
        }

