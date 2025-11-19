"""
Agent Router - Agent路由

提供Agent相关的API端点
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

from backend.services.agent_service import AgentService, get_agent_service


router = APIRouter(prefix="/agent", tags=["agent"])


# ==================== 请求模型 ====================

class MessageRequest(BaseModel):
    """消息请求"""
    user_id: str
    message: str
    conversation_id: Optional[str] = None


class FollowupRequest(BaseModel):
    """回访请求"""
    user_id: str


# ==================== API端点 ====================

@router.post("/chat")
async def agent_chat(
    request: MessageRequest,
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    Agent聊天接口
    
    使用Agent模式处理用户消息，提供智能规划和工具调用
    """
    try:
        result = await agent_service.process_message(
            user_id=request.user_id,
            message=request.message,
            conversation_id=request.conversation_id
        )
        
        return {
            "code": 200 if result["success"] else 500,
            "message": "success" if result["success"] else "error",
            "data": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_agent_status(
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    获取Agent状态
    
    返回Agent各模块的运行状态和统计信息
    """
    try:
        status = agent_service.get_agent_status()
        
        return {
            "code": 200,
            "message": "success",
            "data": status
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{user_id}")
async def get_execution_history(
    user_id: str,
    limit: int = 10,
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    获取用户执行历史
    
    查看用户与Agent的交互记录
    """
    try:
        history = agent_service.get_execution_history(user_id, limit)
        
        return {
            "code": 200,
            "message": "success",
            "data": history
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memory/{user_id}")
async def get_memory_summary(
    user_id: str,
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    获取用户记忆摘要
    
    查看用户画像、工作记忆、行为日志等
    """
    try:
        summary = agent_service.get_memory_summary(user_id)
        
        return {
            "code": 200,
            "message": "success",
            "data": summary
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tools")
async def get_available_tools(
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    获取可用工具列表
    
    查看Agent可以调用的所有工具
    """
    try:
        tools = agent_service.get_available_tools()
        
        return {
            "code": 200,
            "message": "success",
            "data": tools
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/followup")
async def plan_followup(
    request: FollowupRequest,
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    规划回访任务
    
    为用户创建回访计划
    """
    try:
        followup = await agent_service.schedule_followup(request.user_id)
        
        if followup:
            return {
                "code": 200,
                "message": "已创建回访计划",
                "data": followup
            }
        else:
            return {
                "code": 200,
                "message": "暂无回访需求",
                "data": None
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    健康检查
    
    检查Agent服务是否正常运行
    """
    return {
        "code": 200,
        "message": "Agent服务运行正常",
        "data": {
            "status": "healthy",
            "version": "1.0.0"
        }
    }

