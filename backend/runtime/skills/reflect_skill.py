# -*- coding: utf-8 -*-
"""
ReflectSkill — 反思评估技能

从原 reflector.py 迁移而来。
将 Reflector 封装为独立 Skill，支持效果评估和回访规划。

迁移映射：
  原: Reflector.evaluate() → 评估结果
  原: Reflector.plan_followup() → 回访计划
  新: ReflectSkill.execute(mode="evaluate" | "followup")
"""

from __future__ import annotations

import logging
import time
from enum import Enum
from typing import Any, Dict, List, Optional

from backend.runtime.skills.base import Skill, SkillContext, SkillResult
from backend.runtime.config.guards import is_module_enabled

logger = logging.getLogger(__name__)


class InteractionResult(str, Enum):
    """交互结果"""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial"
    FAILURE = "failure"
    UNKNOWN = "unknown"


class FollowupType(str, Enum):
    """回访类型"""
    ROUTINE_CHECK = "routine_check"
    GOAL_TRACKING = "goal_tracking"
    EMOTIONAL_SUPPORT = "emotional_support"
    CRISIS_INTERVENTION = "crisis_intervention"


class ReflectSkill(Skill):
    """
    反思评估技能 — 评估交互效果、规划回访

    功能：
    - 交互效果评估
    - 策略优化建议
    - 回访任务规划
    - 经验学习
    """

    def __init__(self, llm_client=None):
        self._llm = llm_client
        self._experience_db: List[Dict[str, Any]] = []

    @property
    def name(self) -> str:
        return "reflect_skill"

    @property
    def description(self) -> str:
        return "反思评估技能 — 评估交互效果、生成改进建议、规划回访"

    def is_applicable(self, context: SkillContext) -> bool:
        """反思技能在交互完成后适用"""
        return context.metadata.get("interaction_complete", False) or context.metadata.get("mode") == "followup"

    async def execute(self, context: SkillContext, **kwargs) -> SkillResult:
        """
        执行反思评估

        Args:
            context: 执行上下文
            **kwargs:
                mode: "evaluate" | "followup" (默认 "evaluate")
                interaction: 交互记录（evaluate 模式需要）

        Returns:
            SkillResult，output 取决于模式
        """
        if not is_module_enabled("reflect_skill"):
            return SkillResult(
                success=True,
                output={"result": "skipped", "score": 0.5},
                skill_name=self.name,
            )

        start_ms = time.time() * 1000
        mode = kwargs.get("mode", "evaluate")

        try:
            if mode == "evaluate":
                result = await self._evaluate(context, **kwargs)
            elif mode == "followup":
                result = await self._plan_followup(context, **kwargs)
            else:
                return SkillResult(
                    success=False,
                    error=f"Unknown reflect mode: {mode}",
                    skill_name=self.name,
                )

            execution_time = time.time() * 1000 - start_ms

            return SkillResult(
                success=True,
                output=result,
                skill_name=self.name,
                execution_time_ms=execution_time,
            )

        except Exception as e:
            logger.error("ReflectSkill execution failed: %s", e, exc_info=True)
            return SkillResult(
                success=False,
                error=str(e),
                skill_name=self.name,
                execution_time_ms=time.time() * 1000 - start_ms,
            )

    async def _evaluate(self, context: SkillContext, **kwargs) -> Dict[str, Any]:
        """评估交互效果"""
        interaction = kwargs.get("interaction", {})

        # 收集指标
        metrics = self._collect_metrics(interaction)

        # 判断结果
        result = self._determine_result(metrics)

        # 计算评分
        score = self._calculate_score(metrics)

        # 生成改进建议
        improvements = self._generate_improvements(result, metrics)

        # 更新经验库
        experience = {
            "interaction_id": interaction.get("id"),
            "result": result.value,
            "score": score,
            "metrics": metrics,
            "improvements": improvements,
        }
        self._experience_db.append(experience)

        return {
            "result": result.value,
            "score": score,
            "metrics": metrics,
            "improvements": improvements,
        }

    async def _plan_followup(self, context: SkillContext, **kwargs) -> Optional[Dict[str, Any]]:
        """规划回访任务"""
        emotion_data = context.emotion_data

        # 基于情绪状态决定回访类型
        if emotion_data.get("is_crisis"):
            return {
                "type": FollowupType.CRISIS_INTERVENTION.value,
                "message": "检查用户安全状况",
                "schedule_hours": 1,
                "priority": "critical",
            }

        emotion = emotion_data.get("emotion", "")
        if emotion in ["sad", "anxious", "lonely"]:
            return {
                "type": FollowupType.EMOTIONAL_SUPPORT.value,
                "message": "关心用户当前状态",
                "schedule_hours": 4,
                "priority": "high",
            }

        # 默认常规检查
        return {
            "type": FollowupType.ROUTINE_CHECK.value,
            "message": "日常关心",
            "schedule_hours": 24,
            "priority": "low",
        }

    def _collect_metrics(self, interaction: Dict) -> Dict[str, Any]:
        """收集交互指标"""
        return {
            "response_time": interaction.get("response_time", 0),
            "has_tool_calls": bool(interaction.get("results", [])),
            "feedback_score": interaction.get("feedback_score", 0.5),
            "goal_achieved": interaction.get("goal_achieved", False),
        }

    def _determine_result(self, metrics: Dict) -> InteractionResult:
        """判断交互结果"""
        if metrics.get("goal_achieved"):
            return InteractionResult.SUCCESS
        if metrics.get("feedback_score", 0.5) >= 0.7:
            return InteractionResult.PARTIAL_SUCCESS
        if metrics.get("feedback_score", 0.5) < 0.3:
            return InteractionResult.FAILURE
        return InteractionResult.UNKNOWN

    def _calculate_score(self, metrics: Dict) -> float:
        """计算评分"""
        score = 0.5
        if metrics.get("goal_achieved"):
            score += 0.3
        score += metrics.get("feedback_score", 0.5) * 0.2
        return min(score, 1.0)

    def _generate_improvements(self, result: InteractionResult, metrics: Dict) -> List[str]:
        """生成改进建议"""
        improvements = []
        if result == InteractionResult.FAILURE:
            improvements.append("尝试更直接的情感回应策略")
        if metrics.get("response_time", 0) > 5.0:
            improvements.append("减少工具调用以提升响应速度")
        if not metrics.get("has_tool_calls") and metrics.get("feedback_score", 0.5) < 0.5:
            improvements.append("考虑使用工具辅助回复")
        return improvements
