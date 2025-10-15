#!/usr/bin/env python3
"""
记忆系统相关路由
"""

from fastapi import APIRouter, HTTPException
from typing import Optional
from backend.services.memory_service import MemoryService
from backend.services.context_service import ContextService
from backend.logging_config import get_logger

router = APIRouter(prefix="/memory", tags=["记忆系统"])
logger = get_logger(__name__)

# 初始化服务
memory_service = MemoryService()
context_service = ContextService(memory_service=memory_service)


@router.get("/users/{user_id}/memories")
async def get_user_memories(
    user_id: str,
    memory_type: Optional[str] = None,
    limit: int = 50
):
    """
    获取用户记忆列表
    
    Args:
        user_id: 用户ID
        memory_type: 记忆类型（event/relationship/commitment/preference/concern）
        limit: 返回数量限制
    """
    try:
        memories = await memory_service.get_user_memories_list(
            user_id=user_id,
            memory_type=memory_type,
            limit=limit
        )
        
        return {
            "user_id": user_id,
            "memories": memories,
            "total": len(memories),
            "type_filter": memory_type
        }
    except Exception as e:
        logger.error(f"获取用户记忆失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/memories/important")
async def get_important_memories(user_id: str, limit: int = 5):
    """
    获取用户最重要的记忆
    
    Args:
        user_id: 用户ID
        limit: 返回数量限制
    """
    try:
        memories = await memory_service.get_important_memories(user_id, limit)
        
        return {
            "user_id": user_id,
            "important_memories": memories,
            "total": len(memories)
        }
    except Exception as e:
        logger.error(f"获取重要记忆失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/memories/search")
async def search_memories(
    user_id: str,
    query: str,
    n_results: int = 3,
    days_limit: int = 7
):
    """
    搜索相关记忆
    
    Args:
        user_id: 用户ID
        query: 搜索查询
        n_results: 返回数量
        days_limit: 时间限制（天数）
    """
    try:
        memories = await memory_service.retrieve_memories(
            user_id=user_id,
            query=query,
            n_results=n_results,
            days_limit=days_limit
        )
        
        return {
            "user_id": user_id,
            "query": query,
            "memories": memories,
            "total": len(memories)
        }
    except Exception as e:
        logger.error(f"搜索记忆失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/users/{user_id}/memories/{memory_id}")
async def delete_memory(user_id: str, memory_id: str):
    """
    删除指定记忆
    
    Args:
        user_id: 用户ID
        memory_id: 记忆ID
    """
    try:
        success = await memory_service.delete_memory(user_id, memory_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="记忆不存在")
        
        return {
            "message": "记忆删除成功",
            "memory_id": memory_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除记忆失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/emotion-trend")
async def get_emotion_trend(user_id: str, days: int = 7):
    """
    获取用户情绪趋势
    
    Args:
        user_id: 用户ID
        days: 统计天数
    """
    try:
        trend = await memory_service.get_emotion_trend(user_id, days)
        
        return {
            "user_id": user_id,
            "trend": trend,
            "days": days
        }
    except Exception as e:
        logger.error(f"获取情绪趋势失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/statistics")
async def get_memory_statistics(user_id: str):
    """
    获取用户记忆统计信息
    
    Args:
        user_id: 用户ID
    """
    try:
        stats = await memory_service.get_memory_statistics(user_id)
        
        return {
            "user_id": user_id,
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"获取记忆统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/profile")
async def get_user_profile(user_id: str):
    """
    获取用户画像
    
    Args:
        user_id: 用户ID
    """
    try:
        profile = await context_service.get_user_profile(user_id)
        
        return {
            "user_id": user_id,
            "profile": profile.to_dict()
        }
    except Exception as e:
        logger.error(f"获取用户画像失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/users/{user_id}/profile")
async def update_user_profile(user_id: str, updates: dict):
    """
    更新用户画像
    
    Args:
        user_id: 用户ID
        updates: 更新的字段
    """
    try:
        profile = await context_service.update_user_profile(user_id, updates)
        
        return {
            "message": "用户画像更新成功",
            "user_id": user_id,
            "profile": profile.to_dict()
        }
    except Exception as e:
        logger.error(f"更新用户画像失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

