# -*- coding: utf-8 -*-
"""
Session — 会话状态管理

提供 6-state FSM 管理会话生命周期，确保状态转换合法可追踪。
包含会话血缘追踪和检查点恢复功能。
"""

from backend.runtime.session.fsm import (
    SessionFSM,
    SessionState,
    IllegalTransitionError,
    TERMINAL_STATES,
)
from backend.runtime.session.lineage import LineageTracker, SessionLineage
from backend.runtime.session.resume import SessionResumer

__all__ = [
    "SessionFSM",
    "SessionState",
    "IllegalTransitionError",
    "TERMINAL_STATES",
    "LineageTracker",
    "SessionLineage",
    "SessionResumer",
]
