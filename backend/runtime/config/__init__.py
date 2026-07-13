# -*- coding: utf-8 -*-
"""
Runtime Config — 模块配置与开关

- ModuleToggles: 每个模块可独立开关
- Guards: 统一的开关检查入口
"""

from backend.runtime.config.toggles import ModuleToggles
from backend.runtime.config.guards import is_module_enabled, require_module, ModuleDisabledError

__all__ = [
    "ModuleToggles",
    "is_module_enabled",
    "require_module",
    "ModuleDisabledError",
]
