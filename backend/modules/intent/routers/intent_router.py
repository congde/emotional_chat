"""
意图识别API路由
Intent Recognition API Router
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional, List
import logging

from ..models.intent_models import IntentRequest, IntentResult, IntentType
from ..services.intent_service import IntentService

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(
    prefix="/intent",
    tags=["intent", "意图识别"],
    responses={404: {"description": "Not found"}},
)

# 全局意图服务实例
_intent_service: Optional[IntentService] = None


def get_intent_service() -> IntentService:
    """获取意图服务实例（依赖注入）"""
    global _intent_service
    if _intent_service is None:
        _intent_service = IntentService()
    return _intent_service


@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_intent(
    request: IntentRequest,
    intent_service: IntentService = Depends(get_intent_service)
):
    """
    分析用户输入的意图
    
    Args:
        request: 意图识别请求
        intent_service: 意图服务实例
        
    Returns:
        意图分析结果
        
    Example:
        ```json
        {
            "text": "我最近总是睡不着，该怎么办？",
            "user_id": "user_123"
        }
        ```
    """
    try:
        result = intent_service.analyze(
            text=request.text,
            user_id=request.user_id
        )
        
        return {
            "code": 200,
            "message": "意图识别成功",
            "data": result
        }
    
    except Exception as e:
        logger.error(f"意图识别失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"意图识别失败: {str(e)}"
        )


@router.post("/detect", response_model=IntentResult)
async def detect_intent(
    text: str,
    intent_service: IntentService = Depends(get_intent_service)
):
    """
    快速检测意图（仅返回意图类型）
    
    Args:
        text: 输入文本
        intent_service: 意图服务实例
        
    Returns:
        意图识别结果
    """
    try:
        result = intent_service.intent_classifier.detect_intent(text)
        return result
    
    except Exception as e:
        logger.error(f"意图检测失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"意图检测失败: {str(e)}"
        )


@router.post("/build_prompt")
async def build_prompt(
    user_context: Dict[str, Any],
    intent_service: IntentService = Depends(get_intent_service)
):
    """
    根据用户上下文构建大模型prompt
    
    Args:
        user_context: 用户上下文（包含情感和意图分析）
        intent_service: 意图服务实例
        
    Returns:
        构建好的prompt
        
    Example:
        ```json
        {
            "analysis": {
                "emotion": {"primary": "焦虑"},
                "intent": {
                    "intent": "advice",
                    "confidence": 0.85,
                    "source": "model"
                }
            }
        }
        ```
    """
    try:
        prompt = intent_service.build_prompt(user_context)
        return {
            "code": 200,
            "message": "Prompt构建成功",
            "data": {
                "prompt": prompt
            }
        }
    
    except Exception as e:
        logger.error(f"Prompt构建失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Prompt构建失败: {str(e)}"
        )


@router.get("/types")
async def get_intent_types():
    """
    获取所有支持的意图类型
    
    Returns:
        意图类型列表及说明
    """
    intent_types = {
        "emotion": {
            "name": "情感表达",
            "description": "用户表达情绪，需要倾听和共情",
            "examples": ["我好难过", "今天心情不好", "感到很焦虑"]
        },
        "advice": {
            "name": "寻求建议",
            "description": "用户寻求建议或解决方案",
            "examples": ["怎么办？", "你有什么建议吗？", "该如何处理？"]
        },
        "conversation": {
            "name": "普通对话",
            "description": "日常交流对话",
            "examples": ["今天天气不错", "我在看书", "刚吃完饭"]
        },
        "function": {
            "name": "功能请求",
            "description": "请求执行特定功能（提醒、记录等）",
            "examples": ["提醒我吃药", "记录今天的心情", "设置闹钟"]
        },
        "crisis": {
            "name": "危机干预",
            "description": "紧急情况，需要立即关注",
            "examples": ["不想活了", "很想自杀", "撑不下去了"]
        },
        "chat": {
            "name": "闲聊",
            "description": "打招呼、寒暄等轻松对话",
            "examples": ["你好", "在吗", "晚上好"]
        }
    }
    
    return {
        "code": 200,
        "message": "获取意图类型成功",
        "data": {
            "total": len(intent_types),
            "intent_types": intent_types
        }
    }


@router.get("/status")
async def get_status(
    intent_service: IntentService = Depends(get_intent_service)
):
    """
    获取意图识别服务状态
    
    Returns:
        服务状态信息
    """
    return {
        "code": 200,
        "message": "服务运行正常",
        "data": {
            "status": "running",
            "mode": "hybrid",
            "components": {
                "rule_engine": "enabled",
                "ml_classifier": "enabled",
                "input_processor": "enabled"
            },
            "supported_intents": [intent.value for intent in IntentType]
        }
    }


@router.post("/batch")
async def batch_analyze(
    texts: List[str],
    intent_service: IntentService = Depends(get_intent_service)
):
    """
    批量分析意图
    
    Args:
        texts: 文本列表
        intent_service: 意图服务实例
        
    Returns:
        批量意图分析结果
    """
    try:
        results = []
        for text in texts:
            result = intent_service.analyze(text)
            results.append(result)
        
        return {
            "code": 200,
            "message": f"批量分析完成（共{len(texts)}条）",
            "data": {
                "total": len(texts),
                "results": results
            }
        }
    
    except Exception as e:
        logger.error(f"批量意图分析失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"批量意图分析失败: {str(e)}"
        )

