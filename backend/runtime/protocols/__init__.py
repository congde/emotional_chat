# -*- coding: utf-8 -*-
"""
Triple Protocol — 基础契约层

运行时所有上层模块通过三组 Protocol 与底层交互，确保可替换性：
- LLMClient: LLM 调用抽象
- ToolExecutor: 工具执行抽象
- PermissionPrompter: 权限提示抽象

参考 ai-buddy/src/runtime/protocols 设计，适配情感陪伴场景。
"""

from backend.runtime.protocols.llm_client import AssistantEvent, LLMClient, TurnSummary
from backend.runtime.protocols.permission_prompter import (
    PermissionDecision,
    PermissionPrompter,
    PermissionRequest,
)
from backend.runtime.protocols.tool_executor import ToolExecutor, ToolResult

__all__ = [
    "AssistantEvent",
    "LLMClient",
    "PermissionDecision",
    "PermissionPrompter",
    "PermissionRequest",
    "ToolExecutor",
    "ToolResult",
    "TurnSummary",
]
