#!/usr/bin/env python3
"""
评估相关路由
"""

from fastapi import APIRouter, HTTPException
from typing import Optional
from backend.models import (
    EvaluationRequest, EvaluationResponse, BatchEvaluationRequest,
    ComparePromptsRequest, HumanVerificationRequest,
    EvaluationStatistics, EvaluationListResponse
)
from backend.database import DatabaseManager, ResponseEvaluation, ChatMessage
from backend.evaluation_engine import EvaluationEngine
from backend.logging_config import get_logger
import json
from datetime import datetime

router = APIRouter(prefix="/evaluation", tags=["评估"])
logger = get_logger(__name__)

# 初始化评估引擎
evaluation_engine = EvaluationEngine()


@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_response(request: EvaluationRequest):
    """
    评估单个回应
    使用LLM作为裁判，从共情程度、自然度、安全性三个维度评分
    """
    try:
        # 调用评估引擎
        evaluation_result = evaluation_engine.evaluate_response(
            user_message=request.user_message,
            bot_response=request.bot_response,
            user_emotion=request.user_emotion or "neutral",
            emotion_intensity=request.emotion_intensity or 5.0
        )
        
        # 检查是否有错误
        if "error" in evaluation_result:
            raise HTTPException(status_code=500, detail=evaluation_result["error"])
        
        # 保存评估结果到数据库
        with DatabaseManager() as db:
            evaluation_data = {
                "session_id": request.session_id,
                "user_id": request.user_id or "anonymous",
                "message_id": request.message_id,
                "user_message": request.user_message,
                "bot_response": request.bot_response,
                "user_emotion": request.user_emotion or "neutral",
                "emotion_intensity": request.emotion_intensity or 5.0,
                "empathy_score": evaluation_result.get("empathy_score"),
                "naturalness_score": evaluation_result.get("naturalness_score"),
                "safety_score": evaluation_result.get("safety_score"),
                "total_score": evaluation_result.get("total_score"),
                "average_score": evaluation_result.get("average_score"),
                "empathy_reasoning": evaluation_result.get("empathy_reasoning", ""),
                "naturalness_reasoning": evaluation_result.get("naturalness_reasoning", ""),
                "safety_reasoning": evaluation_result.get("safety_reasoning", ""),
                "overall_comment": evaluation_result.get("overall_comment", ""),
                "strengths": evaluation_result.get("strengths", []),
                "weaknesses": evaluation_result.get("weaknesses", []),
                "improvement_suggestions": evaluation_result.get("improvement_suggestions", []),
                "model": evaluation_result.get("model"),
                "prompt_version": request.prompt_version
            }
            
            saved_evaluation = db.save_evaluation(evaluation_data)
            
            return EvaluationResponse(
                evaluation_id=saved_evaluation.id,
                empathy_score=saved_evaluation.empathy_score,
                naturalness_score=saved_evaluation.naturalness_score,
                safety_score=saved_evaluation.safety_score,
                average_score=saved_evaluation.average_score,
                total_score=saved_evaluation.total_score,
                overall_comment=saved_evaluation.overall_comment or "",
                strengths=json.loads(saved_evaluation.strengths) if saved_evaluation.strengths else [],
                weaknesses=json.loads(saved_evaluation.weaknesses) if saved_evaluation.weaknesses else [],
                improvement_suggestions=json.loads(saved_evaluation.improvement_suggestions) if saved_evaluation.improvement_suggestions else [],
                created_at=saved_evaluation.created_at
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"评估接口错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch")
async def batch_evaluate(request: BatchEvaluationRequest):
    """批量评估会话中的对话"""
    try:
        with DatabaseManager() as db:
            # 获取会话消息
            if request.session_id:
                messages = db.get_session_messages(request.session_id, limit=request.limit or 10)
            else:
                # 如果没有指定session_id，获取最新的对话
                messages = db.db.query(ChatMessage)\
                    .order_by(ChatMessage.created_at.desc())\
                    .limit(request.limit or 10)\
                    .all()
            
            if not messages:
                raise HTTPException(status_code=404, detail="没有找到对话记录")
            
            # 组织对话对（用户消息 + 助手回复）
            conversations = []
            user_msg = None
            
            for msg in reversed(messages):
                if msg.role == "user":
                    user_msg = msg
                elif msg.role == "assistant" and user_msg:
                    conversations.append({
                        "id": msg.id,
                        "session_id": msg.session_id,
                        "user_message": user_msg.content,
                        "bot_response": msg.content,
                        "user_emotion": user_msg.emotion or "neutral",
                        "emotion_intensity": user_msg.emotion_intensity or 5.0
                    })
                    user_msg = None
            
            # 批量评估
            results = evaluation_engine.batch_evaluate(conversations)
            
            # 保存评估结果
            saved_results = []
            for i, result in enumerate(results):
                evaluation_data = {
                    "session_id": conversations[i]["session_id"],
                    "user_id": "anonymous",
                    "message_id": conversations[i]["id"],
                    "user_message": conversations[i]["user_message"],
                    "bot_response": conversations[i]["bot_response"],
                    "user_emotion": conversations[i]["user_emotion"],
                    "emotion_intensity": conversations[i]["emotion_intensity"],
                    "empathy_score": result.get("empathy_score"),
                    "naturalness_score": result.get("naturalness_score"),
                    "safety_score": result.get("safety_score"),
                    "total_score": result.get("total_score"),
                    "average_score": result.get("average_score"),
                    "empathy_reasoning": result.get("empathy_reasoning", ""),
                    "naturalness_reasoning": result.get("naturalness_reasoning", ""),
                    "safety_reasoning": result.get("safety_reasoning", ""),
                    "overall_comment": result.get("overall_comment", ""),
                    "strengths": result.get("strengths", []),
                    "weaknesses": result.get("weaknesses", []),
                    "improvement_suggestions": result.get("improvement_suggestions", []),
                    "model": result.get("model")
                }
                
                saved = db.save_evaluation(evaluation_data)
                saved_results.append({
                    "evaluation_id": saved.id,
                    "average_score": saved.average_score,
                    "user_message": conversations[i]["user_message"][:50] + "..."
                })
            
            return {
                "message": "批量评估完成",
                "total_evaluated": len(saved_results),
                "results": saved_results
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量评估错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare-prompts")
async def compare_prompts(request: ComparePromptsRequest):
    """对比不同Prompt生成的回应"""
    try:
        comparison_result = evaluation_engine.compare_prompts(
            user_message=request.user_message,
            responses=request.responses,
            user_emotion=request.user_emotion or "neutral",
            emotion_intensity=request.emotion_intensity or 5.0
        )
        
        return comparison_result
        
    except Exception as e:
        logger.error(f"Prompt对比错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=EvaluationListResponse)
async def get_evaluations(session_id: str = None, limit: int = 100):
    """获取评估列表"""
    try:
        with DatabaseManager() as db:
            evaluations = db.get_evaluations(session_id=session_id, limit=limit)
            
            evaluation_list = []
            for e in evaluations:
                evaluation_list.append({
                    "id": e.id,
                    "session_id": e.session_id,
                    "user_id": e.user_id,
                    "user_message": e.user_message[:100] + "..." if len(e.user_message or "") > 100 else e.user_message,
                    "bot_response": e.bot_response[:100] + "..." if len(e.bot_response or "") > 100 else e.bot_response,
                    "empathy_score": e.empathy_score,
                    "naturalness_score": e.naturalness_score,
                    "safety_score": e.safety_score,
                    "average_score": e.average_score,
                    "overall_comment": e.overall_comment,
                    "is_human_verified": e.is_human_verified,
                    "created_at": e.created_at.isoformat() if e.created_at else None
                })
            
            # 获取统计信息
            stats = db.get_evaluation_statistics()
            
            return EvaluationListResponse(
                evaluations=evaluation_list,
                total=len(evaluation_list),
                statistics=stats
            )
            
    except Exception as e:
        logger.error(f"获取评估列表错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics", response_model=EvaluationStatistics)
async def get_evaluation_statistics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """获取评估统计信息"""
    try:
        # 解析日期
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        with DatabaseManager() as db:
            stats = db.get_evaluation_statistics(start_date=start, end_date=end)
            return EvaluationStatistics(**stats)
            
    except Exception as e:
        logger.error(f"获取评估统计错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{evaluation_id}")
async def get_evaluation_detail(evaluation_id: int):
    """获取评估详情"""
    try:
        with DatabaseManager() as db:
            evaluation = db.db.query(ResponseEvaluation)\
                .filter(ResponseEvaluation.id == evaluation_id)\
                .first()
            
            if not evaluation:
                raise HTTPException(status_code=404, detail="评估记录不存在")
            
            return {
                "id": evaluation.id,
                "session_id": evaluation.session_id,
                "user_id": evaluation.user_id,
                "message_id": evaluation.message_id,
                "user_message": evaluation.user_message,
                "bot_response": evaluation.bot_response,
                "user_emotion": evaluation.user_emotion,
                "emotion_intensity": evaluation.emotion_intensity,
                "scores": {
                    "empathy": evaluation.empathy_score,
                    "naturalness": evaluation.naturalness_score,
                    "safety": evaluation.safety_score,
                    "average": evaluation.average_score,
                    "total": evaluation.total_score
                },
                "reasoning": {
                    "empathy": evaluation.empathy_reasoning,
                    "naturalness": evaluation.naturalness_reasoning,
                    "safety": evaluation.safety_reasoning
                },
                "overall_comment": evaluation.overall_comment,
                "strengths": json.loads(evaluation.strengths) if evaluation.strengths else [],
                "weaknesses": json.loads(evaluation.weaknesses) if evaluation.weaknesses else [],
                "improvement_suggestions": json.loads(evaluation.improvement_suggestions) if evaluation.improvement_suggestions else [],
                "evaluation_model": evaluation.evaluation_model,
                "prompt_version": evaluation.prompt_version,
                "is_human_verified": evaluation.is_human_verified,
                "human_rating_diff": evaluation.human_rating_diff,
                "created_at": evaluation.created_at.isoformat() if evaluation.created_at else None
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取评估详情错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{evaluation_id}/human-verify")
async def human_verify_evaluation(evaluation_id: int, request: HumanVerificationRequest):
    """人工验证评估结果"""
    try:
        with DatabaseManager() as db:
            human_scores = {
                "empathy": request.empathy_score,
                "naturalness": request.naturalness_score,
                "safety": request.safety_score
            }
            
            evaluation = db.update_evaluation_human_verification(
                evaluation_id=evaluation_id,
                human_scores=human_scores
            )
            
            if not evaluation:
                raise HTTPException(status_code=404, detail="评估记录不存在")
            
            return {
                "message": "人工验证完成",
                "evaluation_id": evaluation_id,
                "ai_scores": {
                    "empathy": evaluation.empathy_score,
                    "naturalness": evaluation.naturalness_score,
                    "safety": evaluation.safety_score,
                    "average": evaluation.average_score
                },
                "human_scores": human_scores,
                "rating_diff": evaluation.human_rating_diff
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"人工验证错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report/generate")
async def generate_evaluation_report(
    session_id: Optional[str] = None,
    limit: int = 100
):
    """生成评估报告"""
    try:
        with DatabaseManager() as db:
            evaluations_db = db.get_evaluations(session_id=session_id, limit=limit)
            
            if not evaluations_db:
                raise HTTPException(status_code=404, detail="没有评估数据")
            
            # 转换为字典格式
            evaluations = []
            for e in evaluations_db:
                evaluations.append({
                    "empathy_score": e.empathy_score,
                    "naturalness_score": e.naturalness_score,
                    "safety_score": e.safety_score,
                    "average_score": e.average_score,
                    "strengths": json.loads(e.strengths) if e.strengths else [],
                    "weaknesses": json.loads(e.weaknesses) if e.weaknesses else []
                })
            
            # 生成报告
            report = evaluation_engine.generate_evaluation_report(evaluations)
            
            return report
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成评估报告错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

