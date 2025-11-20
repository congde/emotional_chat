#!/usr/bin/env python3
"""
增强版聊天路由
提供增强版多轮对话API
"""

from fastapi import APIRouter, HTTPException
from typing import Optional
from backend.models import ChatRequest, ChatResponse
from backend.services.enhanced_chat_service import EnhancedChatService
from backend.logging_config import get_logger

router = APIRouter(prefix="/enhanced-chat", tags=["增强版聊天"])
logger = get_logger(__name__)

# 初始化增强版服务
enhanced_chat_service = EnhancedChatService(
    use_rag=True,
    use_intent=True,
    use_enhanced_processor=True,
    enable_proactive_recall=True
)


@router.post("/", response_model=ChatResponse)
async def enhanced_chat(request: ChatRequest):
    """
    增强版聊天接口
    
    功能包括：
    - 短期记忆滑动窗口 + 关键轮次保留
    - 长期记忆向量检索 + 时间衰减
    - 动态用户画像构建
    - 主动回忆与情感追踪
    """
    try:
        response = await enhanced_chat_service.chat(request)
        return response
    except Exception as e:
        logger.error(f"增强版聊天接口错误: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/history")
async def get_session_history(session_id: str, limit: int = 20):
    """获取会话历史"""
    try:
        history = await enhanced_chat_service.get_session_history(session_id, limit)
        # 如果没有消息，返回空列表而不是404
        # 这样前端可以正常处理空会话的情况
        if not history.get("messages"):
            return {
                "session_id": session_id,
                "messages": []
            }
        return history
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取会话历史错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/sessions")
async def get_user_sessions(user_id: str, limit: int = 50):
    """获取用户的所有会话列表"""
    try:
        sessions = await enhanced_chat_service.get_user_sessions(user_id, limit)
        return sessions
    except Exception as e:
        logger.error(f"获取用户会话列表错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    try:
        success = await enhanced_chat_service.delete_session(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        return {
            "message": "会话删除成功",
            "session_id": session_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除会话错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/profile")
async def get_user_profile(user_id: str):
    """
    获取用户画像
    
    返回：
    - 核心关注点
    - 情绪趋势
    - 沟通风格
    - 统计信息
    """
    try:
        profile = await enhanced_chat_service.get_user_profile(user_id)
        return profile
    except Exception as e:
        logger.error(f"获取用户画像错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/memories")
async def get_user_memories(user_id: str, limit: int = 10):
    """
    获取用户重要记忆
    
    返回：
    - 记忆内容
    - 重要性评分
    - 访问统计
    - 时间信息
    """
    try:
        memories = await enhanced_chat_service.get_user_memories(user_id, limit)
        return {
            "user_id": user_id,
            "memories": memories,
            "total": len(memories)
        }
    except Exception as e:
        logger.error(f"获取用户记忆错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/emotion-insights")
async def get_emotion_insights(user_id: str):
    """
    获取用户情绪洞察
    
    返回：
    - 情绪趋势（最近7天）
    - 当前状态
    - 显著变化点
    - 情绪时间线
    """
    try:
        insights = await enhanced_chat_service.get_emotion_insights(user_id)
        return insights
    except Exception as e:
        logger.error(f"获取情绪洞察错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/status")
async def get_system_status():
    """
    获取系统状态
    
    返回增强版聊天系统的功能启用状态
    """
    return {
        "version": "enhanced_v1.0",
        "features": {
            "enhanced_memory": {
                "enabled": True,
                "description": "短期滑动窗口 + 长期向量检索 + 时间衰减"
            },
            "user_profile": {
                "enabled": True,
                "description": "动态用户画像构建"
            },
            "proactive_recall": {
                "enabled": enhanced_chat_service.proactive_recall is not None,
                "description": "主动回忆与情感追踪"
            },
            "rag": {
                "enabled": enhanced_chat_service.rag_enabled,
                "description": "RAG知识库增强"
            },
            "intent_recognition": {
                "enabled": enhanced_chat_service.intent_enabled,
                "description": "意图识别系统"
            },
            "input_processor": {
                "enabled": enhanced_chat_service.enhanced_processor_enabled,
                "description": "增强版输入处理"
            }
        },
        "status": "operational"
    }

