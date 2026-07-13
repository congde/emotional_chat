# -*- coding: utf-8 -*-
"""
PlanningSkill — 任务规划技能

从原 planner.py 迁移而来。
将 Planner 封装为独立 Skill，支持策略选择和执行计划生成。

迁移映射：
  原: Planner.plan() → ExecutionPlan
  新: PlanningSkill.execute() → SkillResult (output = execution_plan)
"""

from __future__ import annotations

import logging
import time
from enum import Enum
from typing import Any, Dict, List, Optional

from backend.runtime.skills.base import Skill, SkillContext, SkillResult
from backend.runtime.config.guards import is_module_enabled

logger = logging.getLogger(__name__)


# ────────────────── Enums ──────────────────


class GoalType(str, Enum):
    """目标类型"""
    INFORMATION_QUERY = "information_query"
    EMOTIONAL_SUPPORT = "emotional_support"
    PROBLEM_SOLVING = "problem_solving"
    BEHAVIOR_CHANGE = "behavior_change"
    CASUAL_CHAT = "casual_chat"


class Complexity(str, Enum):
    """任务复杂度"""
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"


class Strategy(str, Enum):
    """执行策略"""
    DIRECT_RESPONSE = "direct_response"
    EMPATHY_FIRST = "empathy_first"
    TOOL_USE = "tool_use"
    SCHEDULED_FOLLOWUP = "scheduled_followup"
    CONVERSATIONAL = "conversational"


# ────────────────── Execution Plan ──────────────────


class ExecutionPlan:
    """执行计划 — 替代原 planner.ExecutionPlan"""

    def __init__(
        self,
        goal: Dict[str, Any],
        strategy: Strategy,
        steps: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.goal = goal
        self.strategy = strategy
        self.steps = steps
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal": self.goal,
            "strategy": self.strategy.value,
            "steps": self.steps,
            "metadata": self.metadata,
        }


# ────────────────── Planning Skill ──────────────────


class PlanningSkill(Skill):
    """
    任务规划技能 — 识别目标、选择策略、生成执行计划

    功能：
    - 目标识别（规则优先，LLM 降级）
    - 复杂度评估
    - 策略选择
    - 执行步骤生成
    """

    def __init__(self, llm_client=None):
        self._llm = llm_client

    @property
    def name(self) -> str:
        return "planning_skill"

    @property
    def description(self) -> str:
        return "任务规划技能 — 识别用户目标、选择策略、生成执行计划"

    def is_applicable(self, context: SkillContext) -> bool:
        """规划技能对所有有用户输入的上下文都适用"""
        return bool(context.user_input)

    async def execute(self, context: SkillContext, **kwargs) -> SkillResult:
        """
        执行任务规划

        Args:
            context: 包含 user_input, emotion_data, memories 的上下文

        Returns:
            SkillResult，output 包含 ExecutionPlan.to_dict()
        """
        if not is_module_enabled("planning_skill"):
            # 禁用时返回默认计划
            return SkillResult(
                success=True,
                output=ExecutionPlan(
                    goal={"goal_type": GoalType.CASUAL_CHAT.value, "complexity": Complexity.SIMPLE.value},
                    strategy=Strategy.DIRECT_RESPONSE,
                    steps=[{"action": "respond"}],
                ).to_dict(),
                skill_name=self.name,
            )

        start_ms = time.time() * 1000

        try:
            user_input = context.user_input
            emotion_data = context.emotion_data

            # 1. 目标识别
            goal = self._identify_goal(user_input, emotion_data)

            # 2. 复杂度判断
            if goal["complexity"] == Complexity.SIMPLE.value:
                plan = ExecutionPlan(
                    goal=goal,
                    strategy=Strategy.DIRECT_RESPONSE,
                    steps=[{"action": "respond", "parameters": {"user_input": user_input}}],
                )
            else:
                # 3. 策略选择
                strategy = self._select_strategy(goal, emotion_data)

                # 4. 生成步骤
                steps = self._generate_steps(goal, strategy, context)

                plan = ExecutionPlan(goal=goal, strategy=strategy, steps=steps)

            execution_time = time.time() * 1000 - start_ms

            return SkillResult(
                success=True,
                output=plan.to_dict(),
                emotion_tag=emotion_data.get("emotion") if emotion_data else None,
                skill_name=self.name,
                execution_time_ms=execution_time,
            )

        except Exception as e:
            logger.error("PlanningSkill execution failed: %s", e, exc_info=True)
            return SkillResult(
                success=False,
                error=str(e),
                skill_name=self.name,
                execution_time_ms=time.time() * 1000 - start_ms,
            )

    def _identify_goal(self, user_input: str, emotion_data: Dict) -> Dict[str, Any]:
        """识别用户目标（规则优先）"""
        emotion = emotion_data.get("emotion", "") if emotion_data else ""
        intensity = emotion_data.get("emotion_intensity", 5.0) if emotion_data else 5.0

        # 规则1：高情绪强度 → 情感支持
        if intensity >= 7.0:
            return {
                "goal_type": GoalType.EMOTIONAL_SUPPORT.value,
                "complexity": Complexity.MEDIUM.value,
                "urgency": "high",
                "description": "用户情绪强烈，需要情感支持",
            }

        # 规则2：问题关键词 → 问题解决
        problem_keywords = ["怎么办", "怎么做", "如何", "帮我", "建议"]
        if any(kw in user_input for kw in problem_keywords):
            return {
                "goal_type": GoalType.PROBLEM_SOLVING.value,
                "complexity": Complexity.COMPLEX.value,
                "urgency": "medium",
                "description": "用户寻求解决方案",
            }

        # 规则3：查询关键词 → 信息查询
        query_keywords = ["是什么", "为什么", "什么时候", "在哪里"]
        if any(kw in user_input for kw in query_keywords):
            return {
                "goal_type": GoalType.INFORMATION_QUERY.value,
                "complexity": Complexity.SIMPLE.value,
                "urgency": "low",
                "description": "用户查询信息",
            }

        # 规则4：改变关键词 → 行为改变
        change_keywords = ["打算", "计划", "决定", "想要", "改变"]
        if any(kw in user_input for kw in change_keywords):
            return {
                "goal_type": GoalType.BEHAVIOR_CHANGE.value,
                "complexity": Complexity.COMPLEX.value,
                "urgency": "medium",
                "description": "用户计划行为改变",
            }

        # 默认：闲聊
        return {
            "goal_type": GoalType.CASUAL_CHAT.value,
            "complexity": Complexity.SIMPLE.value,
            "urgency": "low",
            "description": "日常对话",
        }

    def _select_strategy(self, goal: Dict, emotion_data: Dict) -> Strategy:
        """选择执行策略"""
        goal_type = goal.get("goal_type", "")

        if goal_type == GoalType.EMOTIONAL_SUPPORT.value:
            return Strategy.EMPATHY_FIRST
        elif goal_type == GoalType.PROBLEM_SOLVING.value:
            return Strategy.TOOL_USE
        elif goal_type == GoalType.BEHAVIOR_CHANGE.value:
            return Strategy.CONVERSATIONAL
        elif goal_type == GoalType.INFORMATION_QUERY.value:
            return Strategy.TOOL_USE
        else:
            return Strategy.DIRECT_RESPONSE

    def _generate_steps(
        self, goal: Dict, strategy: Strategy, context: SkillContext
    ) -> List[Dict[str, Any]]:
        """生成执行步骤"""
        steps = []

        if strategy == Strategy.EMPATHY_FIRST:
            steps.append({"action": "empathy_respond", "parameters": {"emotion_data": context.emotion_data}})
            steps.append({"action": "support", "parameters": {"goal": goal}})

        elif strategy == Strategy.TOOL_USE:
            steps.append({"action": "tool_call", "parameters": {"goal": goal}})
            steps.append({"action": "respond", "parameters": {"include_tool_result": True}})

        elif strategy == Strategy.CONVERSATIONAL:
            steps.append({"action": "guide", "parameters": {"goal": goal}})
            steps.append({"action": "followup", "parameters": {}})

        else:
            steps.append({"action": "respond", "parameters": {"user_input": context.user_input}})

        return steps
