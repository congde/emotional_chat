# -*- coding: utf-8 -*-
"""
Module Guards — 统一的开关检查入口

提供 is_module_enabled 和 require_module 两个核心函数：
- is_module_enabled: 软检查，返回 bool
- require_module: 硬检查，禁用时抛 ModuleDisabledError

Usage::

    from runtime.config.guards import is_module_enabled

    if is_module_enabled("emotion_skill"):
        result = await emotion_skill.execute(context)
    ...

    from runtime.config.guards import require_module

    async def dangerous_operation(self, ...):
        require_module("crisis_intervention")  # raises if disabled
        ...
"""

from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# 全局 toggles 实例 — 由应用启动时设置
_toggles: Optional[object] = None


class ModuleDisabledError(RuntimeError):
    """当调用被禁用的模块时抛出"""

    def __init__(self, module: str) -> None:
        super().__init__(
            f"Module '{module}' is disabled via ModuleToggles. "
            f"Enable it with EMOTIONAL_CHAT__MODULES__{module.upper()}__ENABLED=true"
        )
        self.module = module


def init_guards(toggles: object) -> None:
    """初始化全局 toggles 引用。应用启动时调用一次。"""
    global _toggles
    _toggles = toggles
    logger.debug("Module guards initialized")


def is_module_enabled(module: str) -> bool:
    """
    检查模块是否启用。

    如果 toggles 未初始化，返回 True (fail-open for tests)。
    """
    if _toggles is None:
        return True  # no toggles → all enabled (test / dev mode)
    return _toggles.is_enabled(module)


def require_module(module: str) -> None:
    """
    断言模块已启用；如果禁用则抛 ModuleDisabledError。

    如果 toggles 未初始化，不执行任何操作 (test / dev mode)。
    """
    if _toggles is not None and not _toggles.is_enabled(module):
        raise ModuleDisabledError(module)
