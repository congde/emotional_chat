# -*- coding: utf-8 -*-
"""
Skill Protocol — 技能系统的核心抽象

设计原则：
1. 每个 Skill 是独立的功能单元，可插拔
2. Skill 通过 SkillContext 获取运行时上下文
3. Skill 通过 SkillResult 返回结果
4. Skill 可声明自己的适用条件 (is_applicable)
5. SkillRegistry 统一管理所有 Skill

从 Workflow 到 Skill 的映射：
  原 7 阶段 Workflow          →  Skill
  ─────────────────────────────────────────
  阶段1: 感知层 (emotion)     →  EmotionSkill
  阶段2: 记忆检索 (memory)    →  MemorySkill
  阶段3: 任务规划 (planner)   →  PlanningSkill
  阶段4: 执行计划 (tool)      →  ToolSkill
  阶段5: 记忆巩固 (memory)    →  MemorySkill (consolidate mode)
  阶段6: 反思评估 (reflector) →  ReflectSkill
  阶段7: 记录历史             →  ActivityTracker (基础设施，非 Skill)
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ────────────────── Data Classes ──────────────────


@dataclass
class SkillContext:
    """Skill 执行上下文 — 包含 Skill 运行所需的全部信息"""

    session_id: str
    user_id: str
    workspace_id: str
    iteration: int = 0  # 当前 ReAct 迭代次数 (1-based)
    # 情感陪伴上下文
    user_input: str = ""
    emotion_data: Dict[str, Any] = field(default_factory=dict)
    memories: List[Dict[str, Any]] = field(default_factory=list)
    user_profile: Dict[str, Any] = field(default_factory=dict)
    # 执行上下文
    metadata: Dict[str, Any] = field(default_factory=dict)
    # 前序 Skill 结果
    prev_results: Dict[str, "SkillResult"] = field(default_factory=dict)


@dataclass
class SkillResult:
    """Skill 执行结果 — 统一的结果格式"""

    success: bool
    output: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    # 情感陪伴扩展
    emotion_tag: Optional[str] = None  # 当前情感标签
    confidence: float = 1.0  # 结果置信度 [0, 1]
    # Skill 调用信息
    skill_name: str = ""
    execution_time_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "emotion_tag": self.emotion_tag,
            "confidence": self.confidence,
            "skill_name": self.skill_name,
            "execution_time_ms": self.execution_time_ms,
        }


# ────────────────── Skill Protocol ──────────────────


class Skill(ABC):
    """
    技能协议 — 所有技能继承此抽象类

    每个 Skill 必须实现：
    - name: 技能名称
    - description: 技能描述
    - execute: 执行技能
    - is_applicable: 判断是否适用

    可选实现：
    - on_activate: Skill 被激活时调用
    - on_deactivate: Skill 被停用时调用
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """技能名称 — 唯一标识"""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """技能描述"""
        ...

    @abstractmethod
    async def execute(self, context: SkillContext, **kwargs) -> SkillResult:
        """
        执行技能

        Args:
            context: 执行上下文
            **kwargs: 技能特有参数

        Returns:
            执行结果
        """
        ...

    def is_applicable(self, context: SkillContext) -> bool:
        """
        判断此 Skill 是否适用于当前上下文

        默认总是适用，子类可覆盖实现条件判断。
        """
        return True

    def on_activate(self) -> None:
        """Skill 被激活时调用 — 可用于初始化资源"""
        pass

    def on_deactivate(self) -> None:
        """Skill 被停用时调用 — 可用于释放资源"""
        pass

    def __repr__(self) -> str:
        return f"Skill(name={self.name!r})"


# ────────────────── Skill Registry ──────────────────


class SkillRegistry:
    """
    技能注册表 — 管理所有 Skill 的生命周期

    Usage::

        registry = SkillRegistry()
        registry.register(EmotionSkill())
        registry.register(MemorySkill())

        # 获取适用的 Skill
        skills = registry.get_applicable_skills(context)

        # 按名称获取
        skill = registry.get_skill("emotion_skill")
    """

    def __init__(self):
        self._skills: Dict[str, Skill] = {}
        self._execution_order: List[str] = []  # 默认执行顺序

    def register(self, skill: Skill, order: Optional[int] = None) -> None:
        """
        注册 Skill

        Args:
            skill: 技能实例
            order: 执行顺序（数字越小越先执行），None 则追加到末尾
        """
        name = skill.name
        if name in self._skills:
            logger.warning("Skill '%s' already registered, replacing", name)
            self._skills[name].on_deactivate()

        self._skills[name] = skill
        skill.on_activate()

        if order is not None:
            self._execution_order.insert(order, name)
        else:
            self._execution_order.append(name)

        logger.info("Registered skill '%s'", name)

    def unregister(self, name: str) -> None:
        """注销 Skill"""
        skill = self._skills.pop(name, None)
        if skill:
            skill.on_deactivate()
            self._execution_order.remove(name)
            logger.info("Unregistered skill '%s'", name)

    def get_skill(self, name: str) -> Optional[Skill]:
        """按名称获取 Skill"""
        return self._skills.get(name)

    def get_applicable_skills(self, context: SkillContext) -> List[Skill]:
        """获取当前上下文适用的所有 Skill（按执行顺序）"""
        result = []
        for name in self._execution_order:
            skill = self._skills.get(name)
            if skill and skill.is_applicable(context):
                result.append(skill)
        return result

    def list_skills(self) -> List[Dict[str, Any]]:
        """列出所有已注册的 Skill"""
        return [
            {
                "name": skill.name,
                "description": skill.description,
            }
            for skill in self._skills.values()
        ]

    @property
    def skill_count(self) -> int:
        return len(self._skills)

    @property
    def skill_names(self) -> List[str]:
        return list(self._execution_order)
