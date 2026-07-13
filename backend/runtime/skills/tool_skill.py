# -*- coding: utf-8 -*-
"""
ToolSkill — 工具调用技能

从原 tool_caller.py 迁移而来。
将 ToolCaller 封装为独立 Skill，通过 ToolExecutor Protocol 执行工具。

迁移映射：
  原: ToolCaller.call_tool() → 工具结果
  新: ToolSkill.execute() → SkillResult (via ToolExecutor Protocol)
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from backend.runtime.skills.base import Skill, SkillContext, SkillResult
from backend.runtime.config.guards import is_module_enabled
from backend.runtime.protocols.tool_executor import ToolExecutor, ToolResult

logger = logging.getLogger(__name__)


class ToolSkill(Skill):
    """
    工具调用技能 — 执行工具并返回结果

    功能：
    - 工具注册与发现
    - 工具调用执行
    - 参数验证
    - 结果解析

    通过 ToolExecutor Protocol 与具体工具实现解耦。
    """

    def __init__(self, tool_executor: Optional[ToolExecutor] = None):
        """
        初始化工具调用技能

        Args:
            tool_executor: ToolExecutor Protocol 实现（可选）
        """
        self._executor = tool_executor

    @property
    def name(self) -> str:
        return "tool_skill"

    @property
    def description(self) -> str:
        return "工具调用技能 — 执行注册的工具并返回结构化结果"

    def is_applicable(self, context: SkillContext) -> bool:
        """工具调用在有工具需求时适用"""
        plan = context.prev_results.get("planning_skill")
        if plan and plan.success:
            strategy = plan.output.get("strategy", "")
            return strategy in ("tool_use", "scheduled_followup")
        return False

    async def execute(self, context: SkillContext, **kwargs) -> SkillResult:
        """
        执行工具调用

        Args:
            context: 执行上下文
            **kwargs:
                tool_name: 工具名称
                tool_args: 工具参数

        Returns:
            SkillResult，output 包含工具执行结果
        """
        if not is_module_enabled("tool_skill"):
            return SkillResult(
                success=False,
                error="Tool skill is disabled",
                skill_name=self.name,
            )

        start_ms = time.time() * 1000
        tool_name = kwargs.get("tool_name", "")
        tool_args = kwargs.get("tool_args", {})

        if not tool_name:
            return SkillResult(
                success=False,
                error="No tool_name provided",
                skill_name=self.name,
            )

        try:
            if self._executor:
                result: ToolResult = await self._executor.execute(tool_name, tool_args)
                execution_time = time.time() * 1000 - start_ms

                return SkillResult(
                    success=result.is_success,
                    output=result.output if result.is_success else None,
                    error=result.error,
                    metadata=result.metadata,
                    skill_name=self.name,
                    execution_time_ms=execution_time,
                )
            else:
                return SkillResult(
                    success=False,
                    error="No ToolExecutor configured",
                    skill_name=self.name,
                    execution_time_ms=time.time() * 1000 - start_ms,
                )

        except Exception as e:
            logger.error("ToolSkill execution failed: %s", e, exc_info=True)
            return SkillResult(
                success=False,
                error=str(e),
                skill_name=self.name,
                execution_time_ms=time.time() * 1000 - start_ms,
            )

    def list_available_tools(self) -> List[Dict[str, Any]]:
        """列出可用工具"""
        if self._executor:
            return self._executor.list_tools()
        return []
