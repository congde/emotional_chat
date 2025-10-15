#!/usr/bin/env python3
"""
反馈相关路由
"""

from fastapi import APIRouter, HTTPException
from backend.models import FeedbackRequest, FeedbackResponse, FeedbackStatistics, FeedbackListResponse
from backend.database import DatabaseManager
from backend.logging_config import get_logger

router = APIRouter(prefix="/feedback", tags=["反馈"])
logger = get_logger(__name__)


@router.post("/", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """提交用户反馈"""
    try:
        with DatabaseManager() as db:
            feedback = db.save_feedback(
                session_id=request.session_id,
                user_id=request.user_id or "anonymous",
                message_id=request.message_id,
                feedback_type=request.feedback_type,
                rating=request.rating,
                comment=request.comment or "",
                user_message=request.user_message or "",
                bot_response=request.bot_response or ""
            )
            
            return FeedbackResponse(
                feedback_id=feedback.id,
                session_id=feedback.session_id,
                feedback_type=feedback.feedback_type,
                rating=feedback.rating,
                created_at=feedback.created_at
            )
    except Exception as e:
        logger.error(f"提交反馈错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics", response_model=FeedbackStatistics)
async def get_feedback_statistics():
    """获取反馈统计信息"""
    try:
        with DatabaseManager() as db:
            stats = db.get_feedback_statistics()
            return FeedbackStatistics(**stats)
    except Exception as e:
        logger.error(f"获取反馈统计错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=FeedbackListResponse)
async def get_feedback_list(feedback_type: str = None, limit: int = 100):
    """获取反馈列表"""
    try:
        with DatabaseManager() as db:
            feedbacks = db.get_all_feedback(feedback_type=feedback_type, limit=limit)
            
            feedback_list = [
                {
                    "id": f.id,
                    "session_id": f.session_id,
                    "user_id": f.user_id,
                    "message_id": f.message_id,
                    "feedback_type": f.feedback_type,
                    "rating": f.rating,
                    "comment": f.comment,
                    "user_message": f.user_message,
                    "bot_response": f.bot_response,
                    "created_at": f.created_at.isoformat() if f.created_at else None,
                    "is_resolved": f.is_resolved
                }
                for f in feedbacks
            ]
            
            return FeedbackListResponse(
                feedbacks=feedback_list,
                total=len(feedback_list)
            )
    except Exception as e:
        logger.error(f"获取反馈列表错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}")
async def get_session_feedback(session_id: str):
    """获取特定会话的反馈"""
    try:
        with DatabaseManager() as db:
            feedbacks = db.get_feedback_by_session(session_id)
            
            return {
                "session_id": session_id,
                "feedbacks": [
                    {
                        "id": f.id,
                        "feedback_type": f.feedback_type,
                        "rating": f.rating,
                        "comment": f.comment,
                        "created_at": f.created_at.isoformat() if f.created_at else None
                    }
                    for f in feedbacks
                ]
            }
    except Exception as e:
        logger.error(f"获取会话反馈错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{feedback_id}/resolve")
async def resolve_feedback(feedback_id: int):
    """标记反馈已解决"""
    try:
        with DatabaseManager() as db:
            feedback = db.mark_feedback_resolved(feedback_id)
            if not feedback:
                raise HTTPException(status_code=404, detail="反馈不存在")
            
            return {
                "message": "反馈已标记为已解决",
                "feedback_id": feedback_id
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"标记反馈已解决错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

