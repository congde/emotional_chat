"""
Agent Service - Agent服务层

提供Agent功能的服务接口，集成到现有系统
"""

from typing import Dict, Any, Optional
from datetime import datetime

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from agent.agent_core import AgentCore, get_agent_core


class AgentService:
    """
    Agent服务
    
    封装Agent Core，提供业务层接口
    """
    
    def __init__(self, agent_core: Optional[AgentCore] = None):
        """
        初始化Agent服务
        
        Args:
            agent_core: Agent核心实例（可选）
        """
        self.agent_core = agent_core or get_agent_core()
    
    async def process_message(
        self,
        user_id: str,
        message: str,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        处理用户消息（Agent模式）
        
        Args:
            user_id: 用户ID
            message: 用户消息
            conversation_id: 对话ID
            
        Returns:
            处理结果
        """
        try:
            # 使用Agent Core处理
            result = await self.agent_core.process(
                user_input=message,
                user_id=user_id,
                conversation_id=conversation_id
            )
            
            return {
                "success": True,
                "data": result,
                "mode": "agent"
            }
        
        except Exception as e:
            print(f"Agent处理失败: {str(e)}")
            
            # 降级到普通模式
            return {
                "success": False,
                "error": str(e),
                "mode": "fallback"
            }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """
        获取Agent状态
        
        Returns:
            状态信息
        """
        return self.agent_core.get_agent_status()
    
    def get_execution_history(
        self,
        user_id: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        获取执行历史
        
        Args:
            user_id: 用户ID（可选）
            limit: 返回数量限制
            
        Returns:
            执行历史
        """
        history = self.agent_core.get_execution_history(user_id, limit)
        
        # 格式化输出
        formatted_history = []
        for record in history:
            formatted_history.append({
                "interaction_id": record.get("interaction_id"),
                "user_id": record.get("user_id"),
                "timestamp": record.get("timestamp").isoformat() if record.get("timestamp") else None,
                "emotion": record.get("perception", {}).get("emotion"),
                "plan_strategy": record.get("plan", {}).get("strategy"),
                "actions_count": len(record.get("results", {}).get("actions", [])),
                "evaluation_score": record.get("evaluation", {}).get("score"),
                "followup": record.get("followup") is not None
            })
        
        return {
            "total": len(formatted_history),
            "history": formatted_history
        }
    
    def get_memory_summary(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户记忆摘要
        
        Args:
            user_id: 用户ID
            
        Returns:
            记忆摘要
        """
        memory_hub = self.agent_core.memory_hub
        
        # 用户画像
        profile = memory_hub.get_user_profile(user_id)
        
        # 工作记忆
        working_memory = memory_hub.get_working_memory()
        
        # 行为日志
        action_log = memory_hub.get_action_log(user_id, days=7)
        
        return {
            "user_id": user_id,
            "profile": profile,
            "working_memory": {
                "conversation_length": len(working_memory.get("conversation", [])),
                "active_tasks": len(working_memory.get("active_tasks", []))
            },
            "recent_actions": len(action_log)
        }
    
    def get_available_tools(self) -> Dict[str, Any]:
        """
        获取可用工具列表
        
        Returns:
            工具列表
        """
        tool_caller = self.agent_core.tool_caller
        
        tools = []
        for tool in tool_caller.registry.list_tools():
            tools.append({
                "name": tool.name,
                "description": tool.description,
                "category": tool.category,
                "parameters": tool.parameters
            })
        
        return {
            "total": len(tools),
            "tools": tools
        }
    
    async def schedule_followup(
        self,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        规划回访任务
        
        Args:
            user_id: 用户ID
            
        Returns:
            回访计划
        """
        reflector = self.agent_core.reflector
        
        followup = await reflector.plan_followup(user_id, {})
        
        if followup:
            # 这里可以触发实际的定时任务
            # 例如调用scheduler_service创建提醒
            pass
        
        return followup


# 单例模式
_agent_service_instance = None

def get_agent_service() -> AgentService:
    """获取全局AgentService实例"""
    global _agent_service_instance
    if _agent_service_instance is None:
        _agent_service_instance = AgentService()
    return _agent_service_instance

