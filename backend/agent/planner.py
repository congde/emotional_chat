"""
Planner - 规划模块

负责：
- 目标识别与分解
- 任务排序
- 策略选择
- 执行计划生成

支持MCP协议：接收MCP消息，输出标准化的MCP消息
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

# 导入MCP协议
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, project_root)

from backend.modules.agent.protocol.mcp import (
    MCPMessage, MCPProtocol, MCPToolCall, MCPContext, 
    MCPMessageType, get_mcp_logger
)


class GoalType(Enum):
    """目标类型"""
    INFORMATION_QUERY = "information_query"     # 信息查询
    EMOTIONAL_SUPPORT = "emotional_support"     # 情感支持
    PROBLEM_SOLVING = "problem_solving"         # 问题解决
    BEHAVIOR_CHANGE = "behavior_change"         # 行为改变
    CASUAL_CHAT = "casual_chat"                 # 闲聊


class Complexity(Enum):
    """任务复杂度"""
    SIMPLE = "simple"       # 简单（直接回复）
    MEDIUM = "medium"       # 中等（需要检索）
    COMPLEX = "complex"     # 复杂（需要多步骤）


class Strategy(Enum):
    """执行策略"""
    DIRECT_RESPONSE = "direct_response"           # 直接回复
    EMPATHY_FIRST = "empathy_first"               # 情感优先
    TOOL_USE = "tool_use"                         # 工具调用
    SCHEDULED_FOLLOWUP = "scheduled_followup"     # 定时回访
    CONVERSATIONAL = "conversational"             # 对话引导


class ExecutionPlan:
    """执行计划"""
    
    def __init__(
        self,
        goal: Dict[str, Any],
        strategy: Strategy,
        steps: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.goal = goal
        self.strategy = strategy
        self.steps = steps
        self.metadata = metadata or {}
        self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "goal": self.goal,
            "strategy": self.strategy.value,
            "steps": self.steps,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }


class Planner:
    """规划模块 - Agent的任务规划器"""
    
    def __init__(self, llm_client=None):
        """
        初始化规划器
        
        Args:
            llm_client: LLM客户端（用于复杂规划）
        """
        self.llm = llm_client
        
        # 规则库
        self.rules = self._init_rules()
        
        # MCP协议支持
        self.mcp_protocol = MCPProtocol()
        self.mcp_logger = get_mcp_logger()
    
    async def plan(
        self, 
        user_input: str, 
        context: Dict[str, Any]
    ) -> ExecutionPlan:
        """
        生成执行计划（传统接口，保持向后兼容）
        
        Args:
            user_input: 用户输入
            context: 上下文信息（包含perception、memories等）
            
        Returns:
            执行计划
        """
        # 1. 目标识别
        goal = self._identify_goal(user_input, context)
        
        # 2. 判断复杂度
        if goal["complexity"] == Complexity.SIMPLE:
            # 简单任务：直接回复
            return ExecutionPlan(
                goal=goal,
                strategy=Strategy.DIRECT_RESPONSE,
                steps=[{
                    "action": "respond",
                    "tool": "llm_generate",
                    "parameters": {
                        "user_input": user_input,
                        "context": context
                    }
                }]
            )
        
        # 3. 目标分解（复杂任务）
        sub_goals = self._decompose_goal(goal, context)
        
        # 4. 构建任务图
        task_graph = self._build_task_graph(sub_goals)
        
        # 5. 策略选择
        strategy = self._select_strategy(task_graph, context)
        
        # 6. 生成执行计划
        execution_plan = self._generate_plan(task_graph, strategy, context)
        
        return execution_plan
    
    def _identify_goal(
        self, 
        user_input: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        识别用户目标
        
        使用规则匹配，避免每次都调用LLM
        """
        perception = context.get("perception", {})
        emotion = perception.get("emotion", "")
        emotion_intensity = perception.get("emotion_intensity", 0)
        
        # 规则1：高情绪强度 -> 情感支持
        if emotion_intensity >= 7.0:
            return {
                "goal_type": GoalType.EMOTIONAL_SUPPORT,
                "complexity": Complexity.MEDIUM,
                "urgency": "high",
                "description": "用户情绪强烈，需要情感支持"
            }
        
        # 规则2：包含问题关键词 -> 问题解决
        problem_keywords = ["怎么办", "怎么做", "如何", "帮我", "建议"]
        if any(kw in user_input for kw in problem_keywords):
            return {
                "goal_type": GoalType.PROBLEM_SOLVING,
                "complexity": Complexity.COMPLEX,
                "urgency": "medium",
                "description": "用户寻求解决方案"
            }
        
        # 规则3：包含查询关键词 -> 信息查询
        query_keywords = ["是什么", "为什么", "什么时候", "在哪里"]
        if any(kw in user_input for kw in query_keywords):
            return {
                "goal_type": GoalType.INFORMATION_QUERY,
                "complexity": Complexity.SIMPLE,
                "urgency": "low",
                "description": "用户查询信息"
            }
        
        # 规则4：包含计划关键词 -> 行为改变
        change_keywords = ["打算", "计划", "决定", "想要", "改变"]
        if any(kw in user_input for kw in change_keywords):
            return {
                "goal_type": GoalType.BEHAVIOR_CHANGE,
                "complexity": Complexity.COMPLEX,
                "urgency": "medium",
                "description": "用户计划行为改变"
            }
        
        # 默认：闲聊
        return {
            "goal_type": GoalType.CASUAL_CHAT,
            "complexity": Complexity.SIMPLE,
            "urgency": "low",
            "description": "日常闲聊"
        }
    
    def _decompose_goal(
        self, 
        goal: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        目标分解
        
        将复杂目标分解为可执行的子任务
        """
        goal_type = goal["goal_type"]
        sub_goals = []
        
        if goal_type == GoalType.EMOTIONAL_SUPPORT:
            # 情感支持流程
            sub_goals = [
                {
                    "task_id": "empathy",
                    "description": "提供共情回应",
                    "depends_on": [],
                    "priority": "high",
                    "tools_needed": []
                },
                {
                    "task_id": "retrieve_memory",
                    "description": "检索相关记忆",
                    "depends_on": [],
                    "priority": "medium",
                    "tools_needed": ["search_memory"]
                },
                {
                    "task_id": "emotional_support",
                    "description": "提供情感支持和建议",
                    "depends_on": ["empathy", "retrieve_memory"],
                    "priority": "high",
                    "tools_needed": []
                }
            ]
        
        elif goal_type == GoalType.PROBLEM_SOLVING:
            # 问题解决流程
            sub_goals = [
                {
                    "task_id": "understand_problem",
                    "description": "理解问题",
                    "depends_on": [],
                    "priority": "high",
                    "tools_needed": []
                },
                {
                    "task_id": "search_solutions",
                    "description": "搜索解决方案",
                    "depends_on": ["understand_problem"],
                    "priority": "high",
                    "tools_needed": ["search_memory", "recommend_resource"]
                },
                {
                    "task_id": "provide_solution",
                    "description": "提供解决方案",
                    "depends_on": ["search_solutions"],
                    "priority": "high",
                    "tools_needed": []
                },
                {
                    "task_id": "schedule_followup",
                    "description": "安排后续跟进",
                    "depends_on": ["provide_solution"],
                    "priority": "medium",
                    "tools_needed": ["set_reminder"],
                    "requires_followup": True
                }
            ]
        
        elif goal_type == GoalType.BEHAVIOR_CHANGE:
            # 行为改变流程
            sub_goals = [
                {
                    "task_id": "clarify_goal",
                    "description": "明确改变目标",
                    "depends_on": [],
                    "priority": "high",
                    "tools_needed": []
                },
                {
                    "task_id": "create_plan",
                    "description": "制定行动计划",
                    "depends_on": ["clarify_goal"],
                    "priority": "high",
                    "tools_needed": []
                },
                {
                    "task_id": "set_reminders",
                    "description": "设置提醒",
                    "depends_on": ["create_plan"],
                    "priority": "medium",
                    "tools_needed": ["set_reminder"]
                },
                {
                    "task_id": "schedule_checkin",
                    "description": "安排定期检查",
                    "depends_on": ["set_reminders"],
                    "priority": "medium",
                    "tools_needed": ["set_reminder"],
                    "requires_followup": True
                }
            ]
        
        else:
            # 默认：简单回复
            sub_goals = [
                {
                    "task_id": "respond",
                    "description": "生成回复",
                    "depends_on": [],
                    "priority": "high",
                    "tools_needed": []
                }
            ]
        
        return sub_goals
    
    def _build_task_graph(self, sub_goals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        构建任务依赖图
        
        返回拓扑排序后的任务列表
        """
        # 简化实现：按优先级和依赖关系排序
        task_map = {task["task_id"]: task for task in sub_goals}
        
        # 拓扑排序
        sorted_tasks = []
        visited = set()
        
        def dfs(task_id: str):
            if task_id in visited:
                return
            
            task = task_map[task_id]
            
            # 先访问依赖
            for dep in task.get("depends_on", []):
                if dep in task_map:
                    dfs(dep)
            
            visited.add(task_id)
            sorted_tasks.append(task)
        
        # 从所有任务开始DFS
        for task_id in task_map:
            dfs(task_id)
        
        return {
            "tasks": sorted_tasks,
            "total_count": len(sorted_tasks)
        }
    
    def _select_strategy(
        self, 
        task_graph: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Strategy:
        """
        策略选择
        
        根据任务特征和上下文选择执行策略
        """
        tasks = task_graph["tasks"]
        perception = context.get("perception", {})
        emotion_intensity = perception.get("emotion_intensity", 0)
        
        # 规则1：如果用户情绪强度高，优先情感支持
        if emotion_intensity > 7.0:
            return Strategy.EMPATHY_FIRST
        
        # 规则2：如果任务需要外部工具，使用Tool-Use策略
        if any(task.get("tools_needed") for task in tasks):
            return Strategy.TOOL_USE
        
        # 规则3：如果需要长期跟踪，使用Follow-up策略
        if any(task.get("requires_followup") for task in tasks):
            return Strategy.SCHEDULED_FOLLOWUP
        
        # 规则4：如果任务简单，直接回复
        if len(tasks) == 1:
            return Strategy.DIRECT_RESPONSE
        
        # 默认：对话引导策略
        return Strategy.CONVERSATIONAL
    
    def _generate_plan(
        self,
        task_graph: Dict[str, Any],
        strategy: Strategy,
        context: Dict[str, Any]
    ) -> ExecutionPlan:
        """
        生成执行计划
        
        将任务图转换为可执行的步骤列表
        """
        tasks = task_graph["tasks"]
        steps = []
        
        for task in tasks:
            # 根据任务类型生成步骤
            if task.get("tools_needed"):
                # 需要调用工具
                for tool in task["tools_needed"]:
                    steps.append({
                        "action": "tool_call",
                        "tool": tool,
                        "parameters": self._generate_tool_parameters(
                            tool, task, context
                        ),
                        "task_id": task["task_id"]
                    })
            else:
                # 不需要工具，直接对话/生成
                steps.append({
                    "action": "respond",
                    "tool": "llm_generate",
                    "parameters": {
                        "task_description": task["description"],
                        "context": context
                    },
                    "task_id": task["task_id"]
                })
        
        return ExecutionPlan(
            goal=context.get("goal", {}),
            strategy=strategy,
            steps=steps,
            metadata={
                "total_tasks": len(tasks),
                "tool_count": sum(1 for s in steps if s["action"] == "tool_call")
            }
        )
    
    async def plan_with_mcp(
        self,
        mcp_message: MCPMessage
    ) -> MCPMessage:
        """
        使用MCP协议进行规划（新接口）
        
        Args:
            mcp_message: 输入的MCP消息（通常来自Agent Core）
            
        Returns:
            输出的MCP消息（包含规划结果和工具调用指令）
        """
        # 提取信息
        user_input = mcp_message.content
        mcp_context = mcp_message.context
        
        # 转换为传统context格式
        context = {
            "user_input": user_input,
            "user_id": mcp_context.user_profile.get("user_id") if mcp_context.user_profile else None,
            "perception": {
                "emotion": mcp_context.emotion_state.get("emotion") if mcp_context.emotion_state else "平静",
                "emotion_intensity": mcp_context.emotion_state.get("intensity", 5.0) if mcp_context.emotion_state else 5.0
            },
            "memories": mcp_context.memory_summary.get("memories", []) if mcp_context.memory_summary else [],
            "user_profile": mcp_context.user_profile or {}
        }
        
        # 生成执行计划
        execution_plan = await self.plan(user_input, context)
        
        # 构建任务目标
        goal_type = execution_plan.goal.get("goal_type")
        if hasattr(goal_type, "value"):
            goal_type_value = goal_type.value
        else:
            goal_type_value = str(goal_type) if goal_type else ""
        
        complexity = execution_plan.goal.get("complexity")
        if hasattr(complexity, "value"):
            complexity_value = complexity.value
        else:
            complexity_value = str(complexity) if complexity else ""
        
        task_goal = {
            "goal_type": goal_type_value,
            "complexity": complexity_value,
            "urgency": execution_plan.goal.get("urgency", "medium"),
            "description": execution_plan.goal.get("description", "")
        }
        
        # 转换为MCP工具调用
        tool_calls = []
        for step in execution_plan.steps:
            if step.get("action") == "tool_call":
                tool_call = MCPToolCall(
                    tool_name=step.get("tool", ""),
                    parameters=step.get("parameters", {})
                )
                tool_calls.append(tool_call)
        
        # 生成规划说明
        plan_description = f"目标：{task_goal['description']}，策略：{execution_plan.strategy.value}，步骤数：{len(execution_plan.steps)}"
        
        # 创建MCP上下文（合并原有上下文）
        output_context = MCPContext(
            user_profile=mcp_context.user_profile,
            emotion_state=mcp_context.emotion_state,
            task_goal=task_goal,
            memory_summary=mcp_context.memory_summary,
            conversation_history=mcp_context.conversation_history,
            metadata={
                "strategy": execution_plan.strategy.value,
                "steps_count": len(execution_plan.steps),
                "plan_metadata": execution_plan.metadata
            }
        )
        
        # 创建MCP输出消息
        output_message = self.mcp_protocol.create_planner_output(
            content=plan_description,
            task_goal=task_goal,
            tool_calls=tool_calls,
            context=output_context
        )
        
        # 设置元数据
        output_message.metadata = {
            **(output_message.metadata or {}),
            "interaction_id": mcp_message.metadata.get("interaction_id") if mcp_message.metadata else None,
            "plan_id": execution_plan.metadata.get("plan_id"),
            "execution_plan": execution_plan.to_dict()
        }
        
        # 记录日志
        self.mcp_logger.log(output_message)
        
        return output_message
    
    def _generate_tool_parameters(
        self,
        tool_name: str,
        task: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        生成工具调用参数
        
        根据工具类型和上下文生成合适的参数
        """
        user_id = context.get("user_id", "")
        perception = context.get("perception", {})
        
        if tool_name == "search_memory":
            return {
                "query": context.get("user_input", ""),
                "user_id": user_id,
                "time_range": 30,
                "emotion_filter": perception.get("emotion")
            }
        
        elif tool_name == "set_reminder":
            return {
                "content": task.get("description", ""),
                "user_id": user_id,
                "schedule_time": self._calculate_followup_time(task),
                "repeat": task.get("requires_followup", False)
            }
        
        elif tool_name == "recommend_resource":
            return {
                "theme": perception.get("emotion", "relaxation"),
                "user_id": user_id
            }
        
        elif tool_name == "get_emotion_log":
            return {
                "user_id": user_id,
                "days": 7,
                "emotion_type": perception.get("emotion")
            }
        
        else:
            return {}
    
    def _calculate_followup_time(self, task: Dict[str, Any]) -> str:
        """
        计算回访时间
        
        根据任务类型确定合适的回访时间
        """
        from datetime import datetime, timedelta
        
        task_description = task.get("description", "")
        
        # 睡眠问题：7天后
        if "睡眠" in task_description:
            followup_time = datetime.now() + timedelta(days=7)
        
        # 情绪问题：3天后
        elif "情绪" in task_description or "心情" in task_description:
            followup_time = datetime.now() + timedelta(days=3)
        
        # 行为改变：1周后
        elif "改变" in task_description or "计划" in task_description:
            followup_time = datetime.now() + timedelta(days=7)
        
        # 默认：2天后
        else:
            followup_time = datetime.now() + timedelta(days=2)
        
        return followup_time.isoformat()
    
    def _init_rules(self) -> Dict[str, Any]:
        """
        初始化规则库
        
        定义各种决策规则
        """
        return {
            "emotion_threshold": {
                "high": 7.0,
                "medium": 5.0,
                "low": 3.0
            },
            "complexity_rules": {
                "simple": ["查询", "是什么", "定义"],
                "medium": ["怎么办", "建议"],
                "complex": ["计划", "改变", "系统"]
            },
            "urgency_keywords": {
                "high": ["紧急", "马上", "立刻", "危险"],
                "medium": ["重要", "尽快"],
                "low": ["有空", "方便的时候"]
            }
        }


# 使用示例
if __name__ == "__main__":
    # 创建规划器
    planner = Planner()
    
    # 模拟用户输入和上下文
    user_input = "我最近睡不好，怎么办？"
    context = {
        "user_id": "user_123",
        "perception": {
            "emotion": "焦虑",
            "emotion_intensity": 7.5,
            "intent": "problem_solving"
        },
        "memories": []
    }
    
    # 生成执行计划
    import asyncio
    plan = asyncio.run(planner.plan(user_input, context))
    
    print("执行计划：")
    print(json.dumps(plan.to_dict(), ensure_ascii=False, indent=2))

