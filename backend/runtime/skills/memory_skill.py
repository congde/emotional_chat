# -*- coding: utf-8 -*-
"""
MemorySkill — 记忆检索与巩固技能

从原 agent_core.py 的"阶段2: 记忆检索"和"阶段5: 记忆巩固"迁移而来。
将 memory_hub 封装为独立 Skill，支持检索和巩固两种模式。

迁移映射：
  原: AgentCore._perceive() → MemoryHub.retrieve()
  原: AgentCore._perceive() → MemoryHub.encode() / consolidate()
  新: MemorySkill.execute(mode="retrieve" | "encode" | "consolidate")
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from backend.runtime.skills.base import Skill, SkillContext, SkillResult
from backend.runtime.config.guards import is_module_enabled

logger = logging.getLogger(__name__)


class MemorySkill(Skill):
    """
    记忆检索与巩固技能 — 管理 Agent 的记忆系统

    支持三种模式：
    - retrieve: 检索相关记忆（原阶段2）
    - encode: 编码新记忆
    - consolidate: 巩固记忆（原阶段5）

    替代原 memory_hub 的直接调用，通过 Skill 协议统一管理。
    """

    def __init__(self, memory_hub=None):
        """
        初始化记忆技能

        Args:
            memory_hub: MemoryHub 实例（可选，延迟加载）
        """
        self._memory_hub = memory_hub

    @property
    def name(self) -> str:
        return "memory_skill"

    @property
    def description(self) -> str:
        return "记忆检索与巩固技能 — 检索相关记忆、编码新记忆、巩固工作记忆"

    def is_applicable(self, context: SkillContext) -> bool:
        """记忆技能对所有有用户输入的上下文都适用"""
        return bool(context.user_input) or bool(context.metadata.get("memory_mode"))

    async def execute(self, context: SkillContext, **kwargs) -> SkillResult:
        """
        执行记忆操作

        Args:
            context: 执行上下文
            **kwargs:
                mode: "retrieve" | "encode" | "consolidate" (默认 "retrieve")

        Returns:
            SkillResult，output 取决于模式：
            - retrieve: List[相关记忆]
            - encode: 编码后的记忆 ID
            - consolidate: 巩固结果
        """
        if not is_module_enabled("memory_skill"):
            return SkillResult(
                success=True,
                output=[],
                skill_name=self.name,
            )

        start_ms = time.time() * 1000
        mode = kwargs.get("mode", "retrieve")

        try:
            if mode == "retrieve":
                result = await self._retrieve(context, **kwargs)
            elif mode == "encode":
                result = await self._encode(context, **kwargs)
            elif mode == "consolidate":
                result = await self._consolidate(context, **kwargs)
            else:
                return SkillResult(
                    success=False,
                    error=f"Unknown memory mode: {mode}",
                    skill_name=self.name,
                )

            execution_time = time.time() * 1000 - start_ms

            return SkillResult(
                success=True,
                output=result,
                skill_name=self.name,
                execution_time_ms=execution_time,
            )

        except Exception as e:
            logger.error("MemorySkill execution failed: %s", e, exc_info=True)
            return SkillResult(
                success=False,
                error=str(e),
                skill_name=self.name,
                execution_time_ms=time.time() * 1000 - start_ms,
            )

    async def _retrieve(self, context: SkillContext, **kwargs) -> List[Dict[str, Any]]:
        """检索相关记忆"""
        if self._memory_hub:
            try:
                memories = self._memory_hub.retrieve(
                    query=context.user_input,
                    user_id=context.user_id,
                    context={
                        "emotion": context.emotion_data.get("emotion", ""),
                        "time_range": kwargs.get("time_range", 30),
                    },
                    top_k=kwargs.get("top_k", 5),
                )
                return memories if isinstance(memories, list) else []
            except Exception as e:
                logger.warning("MemoryHub.retrieve failed: %s", e)

        # 无 memory_hub 时返回空列表
        return []

    async def _encode(self, context: SkillContext, **kwargs) -> Dict[str, Any]:
        """编码新记忆"""
        content = kwargs.get("content", context.user_input)

        if self._memory_hub:
            try:
                memory = self._memory_hub.encode({
                    "content": content,
                    "emotion": context.emotion_data,
                    "user_id": context.user_id,
                    "role": kwargs.get("role", "user"),
                })
                return {"memory_id": getattr(memory, "id", "unknown")}
            except Exception as e:
                logger.warning("MemoryHub.encode failed: %s", e)

        return {"memory_id": "fallback"}

    async def _consolidate(self, context: SkillContext, **kwargs) -> Dict[str, Any]:
        """巩固记忆"""
        if self._memory_hub:
            try:
                memory_id = kwargs.get("memory_id")
                if memory_id:
                    self._memory_hub.consolidate(memory_id)
                return {"consolidated": True}
            except Exception as e:
                logger.warning("MemoryHub.consolidate failed: %s", e)

        return {"consolidated": False}
