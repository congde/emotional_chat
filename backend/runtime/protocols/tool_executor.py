# -*- coding: utf-8 -*-
"""
Protocol 2: Tool Executor — 工具执行抽象

Defines the contract for tool execution. Tools always return ToolResult
and never raise exceptions (error in .error field).

Adapted for emotional chat:
- 工具包含情感陪伴专用工具 (心理数据库、日历、音频播放器等)
- ToolResult 包含工具类别标记
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class ToolResult:
    """工具执行结果 — 永不抛异常，错误在 error 字段返回"""

    output: str = ""
    error: str | None = None
    metadata: dict = field(default_factory=dict)
    # 情感陪伴扩展字段
    tool_category: str = "general"  # "emotion" | "memory" | "calendar" | "general"

    @property
    def is_error(self) -> bool:
        return self.error is not None

    @property
    def is_success(self) -> bool:
        return self.error is None


class ToolExecutor(Protocol):
    """Protocol for tool execution — never throws, error in ToolResult."""

    async def execute(self, name: str, args: dict) -> ToolResult: ...

    def list_tools(self) -> list[dict]:
        """返回所有可用工具的描述列表"""
        ...
