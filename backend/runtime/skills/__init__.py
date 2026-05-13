# -*- coding: utf-8 -*-
"""
Skills — 可插拔技能系统

每个 Skill 实现统一协议，可独立启用/禁用/替换。
Runtime 通过 SkillRegistry 管理所有 Skill 的生命周期。
"""

from backend.runtime.skills.base import (
    Skill,
    SkillContext,
    SkillResult,
    SkillRegistry,
)

__all__ = [
    "Skill",
    "SkillContext",
    "SkillResult",
    "SkillRegistry",
]
