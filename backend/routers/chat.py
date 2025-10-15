#!/usr/bin/env python3
"""
聊天相关路由
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
from backend.models import ChatRequest, ChatResponse
from backend.services.chat_service import ChatService
from backend.logging_config import get_logger
import json
from pathlib import Path
import uuid

router = APIRouter(prefix="/chat", tags=["聊天"])
logger = get_logger(__name__)

# 初始化服务
chat_service = ChatService()


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    聊天接口（启用记忆系统）
    """
    try:
        response = await chat_service.chat(request, use_memory_system=True)
        return response
    except Exception as e:
        logger.error(f"聊天接口错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simple", response_model=ChatResponse)
async def chat_simple(request: ChatRequest):
    """
    简单聊天接口（不使用记忆系统，用于对比）
    """
    try:
        response = await chat_service.chat(request, use_memory_system=False)
        return response
    except Exception as e:
        logger.error(f"简单聊天接口错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/summary")
async def get_session_summary(session_id: str):
    """获取会话摘要"""
    try:
        summary = await chat_service.get_session_summary(session_id)
        if "error" in summary:
            raise HTTPException(status_code=404, detail=summary["error"])
        return summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取会话摘要错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/history")
async def get_session_history(session_id: str, limit: int = 20):
    """获取会话历史"""
    try:
        history = await chat_service.get_session_history(session_id, limit)
        if not history.get("messages"):
            raise HTTPException(status_code=404, detail="会话不存在或无消息")
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
        sessions = await chat_service.get_user_sessions(user_id, limit)
        return sessions
    except Exception as e:
        logger.error(f"获取用户会话列表错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    try:
        success = await chat_service.delete_session(session_id)
        
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


@router.get("/users/{user_id}/emotion-trends")
async def get_user_emotion_trends(user_id: str):
    """获取用户情感趋势"""
    try:
        trends = await chat_service.get_user_emotion_trends(user_id)
        if "error" in trends:
            raise HTTPException(status_code=404, detail=trends["error"])
        return trends
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取情感趋势错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

