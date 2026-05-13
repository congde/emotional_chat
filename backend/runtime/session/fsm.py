# -*- coding: utf-8 -*-
"""
Session FSM — 6-state finite state machine

States: idle, running, requires_approval, compacted, forked, failed, timeout, terminated
Transitions enforce valid paths; invalid transitions raise IllegalTransitionError.

情感陪伴场景状态流：
  idle → running → (requires_approval | compacted | failed | timeout | terminated)
  requires_approval → running (approved) | terminated (rejected)
  compacted → running | terminated
  failed → terminated
  timeout → terminated

关键设计：
- 任何非终态都可转到 TERMINATED (用户取消/错误)
- FAILED / TIMEOUT 是非终态保持态 — 需要人工确认后才能归档
- COMPACTED / FORKED 代表结构性状态 — 可以恢复到 RUNNING
"""

from __future__ import annotations

from enum import Enum
from typing import FrozenSet


class SessionState(str, Enum):
    """所有有效的会话状态"""

    IDLE = "idle"
    RUNNING = "running"
    REQUIRES_APPROVAL = "requires_approval"
    COMPACTED = "compacted"
    FORKED = "forked"
    FAILED = "failed"
    TIMEOUT = "timeout"
    TERMINATED = "terminated"


class IllegalTransitionError(Exception):
    """当尝试非法状态转换时抛出"""

    def __init__(self, from_state: SessionState, to_state: SessionState):
        self.from_state = from_state
        self.to_state = to_state
        super().__init__(
            f"Illegal session state transition: {from_state.value!r} → {to_state.value!r}"
        )


# ── 终态 — 不允许进一步转换 ──────────────────────────
TERMINAL_STATES: FrozenSet[SessionState] = frozenset(
    {
        SessionState.TERMINATED,
    }
)

# ── 有效转换 (from_state → set of allowed to_states) ──────
_TRANSITIONS: dict[SessionState, FrozenSet[SessionState]] = {
    SessionState.IDLE: frozenset(
        {
            SessionState.RUNNING,
            SessionState.TERMINATED,
        }
    ),
    SessionState.RUNNING: frozenset(
        {
            SessionState.REQUIRES_APPROVAL,
            SessionState.COMPACTED,
            SessionState.FORKED,
            SessionState.FAILED,
            SessionState.TIMEOUT,
            SessionState.TERMINATED,
        }
    ),
    SessionState.REQUIRES_APPROVAL: frozenset(
        {
            SessionState.RUNNING,  # approved
            SessionState.TERMINATED,  # rejected or expired
        }
    ),
    SessionState.COMPACTED: frozenset(
        {
            SessionState.RUNNING,
            SessionState.TERMINATED,
        }
    ),
    SessionState.FORKED: frozenset(
        {
            SessionState.RUNNING,
            SessionState.TERMINATED,
        }
    ),
    SessionState.FAILED: frozenset(
        {
            SessionState.TERMINATED,
        }
    ),
    SessionState.TIMEOUT: frozenset(
        {
            SessionState.TERMINATED,
        }
    ),
    SessionState.TERMINATED: frozenset(),  # terminal — no outbound transitions
}


class SessionFSM:
    """
    管理单个会话生命周期的有限状态机。

    Usage::

        fsm = SessionFSM()                  # starts in IDLE
        fsm.transition(SessionState.RUNNING)
        fsm.transition(SessionState.TERMINATED)

    Raises ``IllegalTransitionError`` on invalid paths so callers never
    silently corrupt session state.
    """

    def __init__(self, initial: SessionState = SessionState.IDLE):
        self._state = initial

    # ── Properties ─────────────────────────────────────────────

    @property
    def state(self) -> SessionState:
        return self._state

    @property
    def is_terminal(self) -> bool:
        return self._state in TERMINAL_STATES

    @property
    def is_running(self) -> bool:
        return self._state == SessionState.RUNNING

    @property
    def requires_approval(self) -> bool:
        return self._state == SessionState.REQUIRES_APPROVAL

    # ── Transitions ────────────────────────────────────────────

    def transition(self, to: SessionState) -> None:
        """
        推进 FSM 到目标状态。

        Raises
        ------
        IllegalTransitionError
            If the transition is not allowed from the current state.
        """
        allowed = _TRANSITIONS.get(self._state, frozenset())
        if to not in allowed:
            raise IllegalTransitionError(self._state, to)
        self._state = to

    def can_transition(self, to: SessionState) -> bool:
        """Return True if the transition to *to* is currently legal."""
        allowed = _TRANSITIONS.get(self._state, frozenset())
        return to in allowed

    def force_terminal(self) -> None:
        """Force transition to TERMINATED regardless of current state.

        Used for emergency shutdown — bypasses transition validation.
        """
        self._state = SessionState.TERMINATED

    # ── Representations ────────────────────────────────────────

    def __repr__(self) -> str:
        return f"SessionFSM(state={self._state.value!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, SessionFSM):
            return self._state == other._state
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._state)
