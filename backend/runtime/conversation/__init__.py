# -*- coding: utf-8 -*-
"""
runtime.conversation — ConversationRuntime package

基于 Skill 的对话运行时，替代原 AgentCore 的 7 阶段线性 Workflow。

外部导入路径保持不变：
    from runtime.conversation import ConversationRuntime
"""

from backend.runtime.conversation._lifecycle import LifecycleMixin
from backend.runtime.conversation._turn import TurnMixin
from backend.runtime.conversation._snapshot import SnapshotMixin
from backend.runtime.conversation._helpers import TurnResult


class ConversationRuntime(
    LifecycleMixin,
    TurnMixin,
    SnapshotMixin,
):
    """
    ConversationRuntime — 基于 Skill 的 ReAct 运行时

    替代原 AgentCore 的 7 阶段线性 Workflow：
    - 原线性流水线 → Skill-based ReAct loop
    - 原 7 固定阶段 → 可插拔的 Skill 链
    - 原无状态管理 → 6-state FSM
    - 原无策略治理 → PolicyEngine
    - 原无 Hook → HookDispatcher

    组合所有 mixin 能力：
    - LifecycleMixin: init, registry, FSM transitions
    - TurnMixin: ReAct loop (替代原 7 阶段流水线)
    - SnapshotMixin: 运行时状态快照
    """

    pass


__all__ = ["ConversationRuntime", "TurnResult"]
