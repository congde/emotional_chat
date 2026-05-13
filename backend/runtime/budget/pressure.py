# -*- coding: utf-8 -*-
"""
BudgetPressure — 预算压力注入

在对话轮次接近上限时注入压力提示，引导 Agent 尽早收束。

情感陪伴场景：
- 当迭代接近 max_iterations 时注入"请尽快总结"提示
- 支持分级压力：soft (70%) → medium (85%) → hard (95%)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class BudgetWarning:
    """预算警告"""

    level: str  # "soft" | "medium" | "hard"
    message: str
    iteration: int
    max_iterations: int


class BudgetPressure:
    """
    预算压力管理器

    Usage::

        pressure = BudgetPressure(max_iterations=10)
        warning = pressure.check(iteration=8)
        if warning:
            # 注入压力提示到用户消息
            messages[-1]["content"] += f"\n[系统提示: {warning.message}]"
    """

    # 压力阈值
    SOFT_THRESHOLD = 0.70  # 70% 时轻柔提醒
    MEDIUM_THRESHOLD = 0.85  # 85% 时中等提醒
    HARD_THRESHOLD = 0.95  # 95% 时强制收束

    def __init__(self, max_iterations: int = 10):
        self._max_iterations = max_iterations

    def check(self, iteration: int) -> Optional[BudgetWarning]:
        """检查是否需要注入预算压力"""
        if self._max_iterations <= 0:
            return None

        ratio = iteration / self._max_iterations

        if ratio >= self.HARD_THRESHOLD:
            return BudgetWarning(
                level="hard",
                message="⚠️ 对话即将达到上限，请立即总结当前内容并给出最终回复。",
                iteration=iteration,
                max_iterations=self._max_iterations,
            )
        elif ratio >= self.MEDIUM_THRESHOLD:
            return BudgetWarning(
                level="medium",
                message="⏳ 对话轮次较多，请开始总结并准备收束。",
                iteration=iteration,
                max_iterations=self._max_iterations,
            )
        elif ratio >= self.SOFT_THRESHOLD:
            return BudgetWarning(
                level="soft",
                message="💡 对话进行了一段时间，请注意回复效率。",
                iteration=iteration,
                max_iterations=self._max_iterations,
            )

        return None

    def should_stop(self, iteration: int) -> bool:
        """是否已达到硬限制"""
        return iteration >= self._max_iterations


def inject_into_last_tool_result(warning: BudgetWarning, tool_results: list) -> None:
    """将预算压力注入到最后的工具结果中"""
    if tool_results and warning:
        last = tool_results[-1]
        if isinstance(last, dict):
            last["budget_warning"] = warning.message
