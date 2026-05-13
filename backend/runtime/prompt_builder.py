# -*- coding: utf-8 -*-
"""
SystemPromptBuilder — 动态系统提示构建

分层组装系统提示 (从上到下):
  1. Base identity: 角色 + 人格 + 语言指令
  2. Memory injection: 记忆注入 + 向量检索
  3. Skill descriptions: 可用 Skill 摘要 + 策略约束
  4. Workspace context: 当前工作区 + 会话信息
  5. Dynamic append: 覆盖提示 / 人格 / Skill 特定指令
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


@dataclass
class PromptLayer:
    """系统提示栈中的单个层"""

    name: str
    content: str
    priority: int = 0  # 数字越大 = 越早出现在组装的提示中
    separator: str = "\n\n"


class SystemPromptBuilder:
    """
    动态系统提示构建器 — 将多个层组装成连贯的系统提示

    Usage::

        builder = SystemPromptBuilder(
            base_identity="你是一个温暖的情感陪伴AI。"
        )
        builder.add_layer(PromptLayer(name="skills", content=skill_summary, priority=10))
        builder.add_layer(PromptLayer(name="memory", content=memory_block, priority=20))
        prompt = builder.build()
    """

    def __init__(
        self,
        base_identity: str = "你是一个温暖的情感陪伴AI，致力于倾听和理解用户的感受。",
        language_hint: Optional[str] = None,
        memory_block: Optional[str] = None,
        skill_summaries: Optional[List[Dict]] = None,
        workspace_root: Optional[str] = None,
        session_id: Optional[str] = None,
        append_system_prompt: Optional[str] = None,
    ):
        self._base_identity = base_identity
        self._language_hint = language_hint
        self._memory_block = memory_block
        self._skill_summaries = skill_summaries or []
        self._workspace_root = workspace_root
        self._session_id = session_id
        self._append_system_prompt = append_system_prompt
        self._extra_layers: List[PromptLayer] = []

    def add_layer(self, layer: PromptLayer) -> None:
        """添加额外的提示层"""
        self._extra_layers.append(layer)

    def remove_layer(self, name: str) -> None:
        """按名称移除层"""
        self._extra_layers = [l for l in self._extra_layers if l.name != name]

    def set_base_identity(self, identity: str) -> None:
        """覆盖基础身份"""
        self._base_identity = identity

    def set_memory_block(self, block: str) -> None:
        """设置记忆注入块"""
        self._memory_block = block

    def set_skill_summaries(self, summaries: List[Dict]) -> None:
        """设置 Skill 描述"""
        self._skill_summaries = summaries

    def build(self) -> str:
        """
        组装完整的系统提示

        层按优先级排序（高优先级在前），然后用分隔符连接。
        """
        layers: List[PromptLayer] = []

        # 1. 基础身份（优先级最高）
        layers.append(PromptLayer(
            name="identity",
            content=self._base_identity,
            priority=100,
        ))

        # 2. 语言提示
        if self._language_hint:
            layers.append(PromptLayer(
                name="language",
                content=f"Language: {self._language_hint}",
                priority=90,
            ))

        # 3. 记忆注入
        if self._memory_block:
            layers.append(PromptLayer(
                name="memory",
                content=self._memory_block,
                priority=50,
            ))

        # 4. Skill 描述
        if self._skill_summaries:
            skill_text = self._format_skill_summaries()
            layers.append(PromptLayer(
                name="skills",
                content=skill_text,
                priority=30,
            ))

        # 5. 工作区上下文
        if self._workspace_root or self._session_id:
            context_parts = []
            if self._session_id:
                context_parts.append(f"Session: {self._session_id}")
            if self._workspace_root:
                context_parts.append(f"Workspace: {self._workspace_root}")
            layers.append(PromptLayer(
                name="workspace",
                content="\n".join(context_parts),
                priority=10,
            ))

        # 6. 额外层
        layers.extend(self._extra_layers)

        # 7. 追加提示（优先级最低）
        if self._append_system_prompt:
            layers.append(PromptLayer(
                name="append",
                content=self._append_system_prompt,
                priority=-10,
            ))

        # 按优先级排序（高在前）
        layers.sort(key=lambda l: -l.priority)

        # 用分隔符连接
        parts = []
        for layer in layers:
            if layer.content:
                parts.append(layer.content)

        return "\n\n".join(parts)

    def _format_skill_summaries(self) -> str:
        """格式化 Skill 描述"""
        lines = ["Available Skills:"]
        for skill in self._skill_summaries:
            name = skill.get("name", "unknown")
            desc = skill.get("description", "")
            lines.append(f"  - {name}: {desc}")
        return "\n".join(lines)
