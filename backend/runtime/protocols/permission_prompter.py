# -*- coding: utf-8 -*-
"""
Protocol 3: Permission Prompter — 权限提示抽象

Defines the contract for permission interaction. Enables the same
ConversationRuntime to be reused by:
1. Main Agent (interactive, with prompter)
2. Sub-Agents (non-interactive, prompter=None → auto-deny)
3. Tests (mock implementations)

Adapted for emotional chat:
- 增加内容安全相关的权限类型
- 危机干预策略需要高等级权限
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class PermissionRequest:
    """权限审批请求"""

    tool_name: str
    arguments: dict
    reason: str
    risk_level: str = "low"  # "low" | "medium" | "high" | "critical"
    # 情感陪伴扩展：内容安全分类
    content_safety: str = "safe"  # "safe" | "sensitive" | "crisis"


@dataclass
class PermissionDecision:
    """权限审批决策"""

    allowed: bool
    reason: str = ""
    # 情感陪伴扩展：降级替代方案
    fallback_action: str | None = None  # "degrade_to_safe_response" | "escalate_to_human"


class PermissionPrompter(Protocol):
    """权限提示协议 — CLI / Web / 自动化实现此接口"""

    async def ask_permission(self, request: PermissionRequest) -> PermissionDecision:
        """
        请求权限审批

        Args:
            request: 权限请求

        Returns:
            审批决策
        """
        ...
