# -*- coding: utf-8 -*-
"""
Hooks — 生命周期钩子系统

支持 pre/post LLM call、tool failure 等生命周期事件注入。
"""

from backend.runtime.hooks.base import (
    HookContext,
    ToolFailureContext,
    PluginHook,
    HookDispatcher,
)

__all__ = [
    "HookContext",
    "ToolFailureContext",
    "PluginHook",
    "HookDispatcher",
]
