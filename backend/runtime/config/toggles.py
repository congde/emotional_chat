# -*- coding: utf-8 -*-
"""
Module Toggles — per-module enable/disable switches

每个 runtime 模块可以独立开关：
  runtime.modules.<module>.enabled = true | false

支持环境变量覆盖：
  EMOTIONAL_CHAT__MODULES__<MODULE>__ENABLED=true|false

这使得：
1. 渐进式发布：新功能背后有开关
2. 紧急禁用：不需要代码部署即可关闭异常模块
3. 隔离测试：开发期间可以只开某个模块

情感陪伴模块列表：
  emotion_skill        — 情感分析 Skill
  memory_skill         — 记忆检索 Skill
  planning_skill       — 任务规划 Skill
  reflect_skill        — 反思评估 Skill
  tool_skill           — 工具调用 Skill
  activity_distillation — Activity Distiller
  policy_engine        — 策略引擎
  session_fsm          — 会话状态机
  budget_pressure      — 预算压力注入
  fallback_manager     — 降级管理
  workspace_isolation  — 工作区隔离
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class ModuleToggle:
    """单个模块的开关状态"""
    name: str
    enabled: bool = True
    description: str = ""


class ModuleToggles:
    """
    模块开关管理器 — 统一管理所有 runtime 模块的启用/禁用状态。

    Usage::

        toggles = ModuleToggles()
        toggles.set_enabled("emotion_skill", False)

        if toggles.is_enabled("emotion_skill"):
            ...

    环境变量覆盖（优先级最高）::

        EMOTIONAL_CHAT__MODULES__EMOTION_SKILL__ENABLED=true
    """

    # 所有模块的默认状态
    _DEFAULTS: Dict[str, bool] = {
        # Skills — 默认启用
        "emotion_skill": True,
        "memory_skill": True,
        "planning_skill": True,
        "reflect_skill": True,
        "tool_skill": True,
        # Infrastructure — 默认启用
        "activity_distillation": True,
        "policy_engine": True,
        "session_fsm": True,
        "budget_pressure": True,
        "fallback_manager": True,
        "workspace_isolation": True,
        # 高级功能 — 默认禁用
        "crisis_intervention": False,
        "auto_followup": False,
        "content_safety_filter": False,
        "skill_review": False,
    }

    ENV_PREFIX = "EMOTIONAL_CHAT__MODULES__"

    def __init__(self, overrides: Optional[Dict[str, bool]] = None):
        # 初始化为默认值
        self._toggles: Dict[str, ModuleToggle] = {}
        for name, default in self._DEFAULTS.items():
            self._toggles[name] = ModuleToggle(
                name=name,
                enabled=default,
            )

        # 应用显式覆盖
        if overrides:
            for name, enabled in overrides.items():
                self.set_enabled(name, enabled)

        # 应用环境变量覆盖
        self._apply_env_overrides()

    def _apply_env_overrides(self) -> None:
        """从环境变量中读取覆盖配置"""
        for name in self._toggles:
            env_key = f"{self.ENV_PREFIX}{name.upper()}__ENABLED"
            env_val = os.environ.get(env_key)
            if env_val is not None:
                enabled = env_val.lower() in ("true", "1", "yes")
                self._toggles[name].enabled = enabled
                logger.info("Module '%s' overridden by env %s=%s", name, env_key, enabled)

    def is_enabled(self, module: str) -> bool:
        """检查模块是否启用"""
        toggle = self._toggles.get(module)
        if toggle is None:
            # 未知模块 — 默认启用 (fail-open)
            logger.debug("Unknown module '%s', defaulting to enabled", module)
            return True
        return toggle.enabled

    def set_enabled(self, module: str, enabled: bool) -> None:
        """设置模块启用状态"""
        if module in self._toggles:
            self._toggles[module].enabled = enabled
        else:
            self._toggles[module] = ModuleToggle(name=module, enabled=enabled)
        logger.info("Module '%s' set to enabled=%s", module, enabled)

    def enable(self, module: str) -> None:
        """启用模块"""
        self.set_enabled(module, True)

    def disable(self, module: str) -> None:
        """禁用模块"""
        self.set_enabled(module, False)

    def list_modules(self) -> Dict[str, bool]:
        """列出所有模块及其状态"""
        return {name: toggle.enabled for name, toggle in self._toggles.items()}

    def get_description(self, module: str) -> str:
        """获取模块描述"""
        toggle = self._toggles.get(module)
        return toggle.description if toggle else ""
