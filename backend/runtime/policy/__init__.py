# -*- coding: utf-8 -*-
"""
Policy — 声明式策略引擎

策略 = "何时触发什么动作" (workflow 规则)
权限 = "谁能做什么" (访问控制)

两者正交：权限系统决定 ALLOW/DENY/ASK，策略引擎决定附加动作。
"""

from backend.runtime.policy.policy_engine import (
    ActionType,
    PolicyAction,
    PolicyRule,
    PolicyEngine,
)

__all__ = [
    "ActionType",
    "PolicyAction",
    "PolicyRule",
    "PolicyEngine",
]
