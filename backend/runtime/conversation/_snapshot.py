# -*- coding: utf-8 -*-
"""
SnapshotMixin — 运行时状态快照

提供运行时当前状态的快照，用于监控和调试。
"""

from __future__ import annotations

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class SnapshotMixin:
    """
    快照 Mixin — 提供运行时状态查询
    """

    def snapshot(self) -> Dict[str, Any]:
        """
        获取运行时当前状态快照

        Returns:
            包含 FSM 状态、Skill 状态、Token 使用等的字典
        """
        return {
            "session_id": self._session_id,
            "workspace_id": self._workspace_id,
            "user_id": self._user_id,
            "fsm_state": self._fsm.state.value,
            "current_iteration": self._current_iteration,
            "max_iterations": self._max_iterations,
            "token_usage": {
                "input_last": self._input_tokens_last,
                "output_last": self._output_tokens_last,
                "total": self._tokens_total,
            },
            "tool_call_count": self._tool_call_count,
            "cancel_requested": self._cancel_requested,
            "skills": self._skill_registry.list_skills(),
            "toggles": self._toggles.list_modules() if self._toggles else {},
        }

    def health_check(self) -> Dict[str, Any]:
        """
        健康检查

        Returns:
            健康状态字典
        """
        return {
            "healthy": self._fsm.is_running or self._fsm.state.value == "idle",
            "session_id": self._session_id,
            "fsm_state": self._fsm.state.value,
            "skill_count": self._skill_registry.skill_count,
        }
