# -*- coding: utf-8 -*-
"""
LifecycleMixin — 初始化、注册、FSM 转换

从原 AgentCore.__init__() 迁移，扩展为完整的运行时生命周期管理。
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Any, Dict, List, Optional

from backend.runtime.session.fsm import SessionFSM, SessionState, IllegalTransitionError
from backend.runtime.config.toggles import ModuleToggles
from backend.runtime.config.guards import init_guards, is_module_enabled
from backend.runtime.hooks.base import HookContext, HookDispatcher
from backend.runtime.skills.base import Skill, SkillRegistry
from backend.runtime.policy.policy_engine import PolicyEngine

logger = logging.getLogger(__name__)


class LifecycleMixin:
    """
    生命周期管理 Mixin

    负责：
    - 初始化运行时组件 (Skills, Policy, Hooks, FSM)
    - 管理运行时注册表
    - FSM 状态转换
    - 运行时启动/关闭
    """

    def __init__(
        self,
        session_id: str = "",
        workspace_id: str = "",
        user_id: str = "",
        max_iterations: int = 10,
        toggles: Optional[ModuleToggles] = None,
        hooks: Optional[list] = None,
        skills: Optional[List[Skill]] = None,
        policy_engine: Optional[PolicyEngine] = None,
        llm_client=None,
        tool_executor=None,
        memory_hub=None,
        emotion_analyzer=None,
    ):
        # ── Identity ──
        self._session_id = session_id or f"session_{uuid.uuid4().hex[:8]}"
        self._workspace_id = workspace_id or f"ws_{uuid.uuid4().hex[:8]}"
        self._user_id = user_id
        self._max_iterations = max_iterations

        # ── Toggles & Guards ──
        self._toggles = toggles or ModuleToggles()
        init_guards(self._toggles)

        # ── FSM ──
        self._fsm = SessionFSM()
        if is_module_enabled("session_fsm"):
            self._fsm.transition(SessionState.IDLE)

        # ── Hooks ──
        self._dispatcher = HookDispatcher(hooks or [])

        # ── Skills ──
        self._skill_registry = SkillRegistry()
        self._register_default_skills(
            skills=skills,
            llm_client=llm_client,
            tool_executor=tool_executor,
            memory_hub=memory_hub,
            emotion_analyzer=emotion_analyzer,
        )

        # ── Policy ──
        self._policy_engine = policy_engine or PolicyEngine()

        # ── LLM ──
        self._llm = llm_client

        # ── Live counters ──
        self._current_iteration: int = 0
        self._input_tokens_last: int = 0
        self._output_tokens_last: int = 0
        self._tokens_total: int = 0
        self._tool_call_count: int = 0

        # ── Cancel signal ──
        self._cancel_requested: bool = False

        logger.info(
            "ConversationRuntime initialized: session=%s, workspace=%s, skills=%s",
            self._session_id,
            self._workspace_id,
            self._skill_registry.skill_names,
        )

    def _register_default_skills(
        self,
        skills: Optional[List[Skill]] = None,
        llm_client=None,
        tool_executor=None,
        memory_hub=None,
        emotion_analyzer=None,
    ) -> None:
        """注册默认 Skills（如果用户没有提供自定义 Skills）"""
        if skills:
            for skill in skills:
                self._skill_registry.register(skill)
            return

        # 注册默认 Skills
        from runtime.skills.emotion_skill import EmotionSkill
        from runtime.skills.memory_skill import MemorySkill
        from runtime.skills.planning_skill import PlanningSkill
        from runtime.skills.reflect_skill import ReflectSkill
        from runtime.skills.tool_skill import ToolSkill

        self._skill_registry.register(EmotionSkill(emotion_analyzer=emotion_analyzer), order=0)
        self._skill_registry.register(MemorySkill(memory_hub=memory_hub), order=1)
        self._skill_registry.register(PlanningSkill(llm_client=llm_client), order=2)
        self._skill_registry.register(ToolSkill(tool_executor=tool_executor), order=3)
        self._skill_registry.register(ReflectSkill(llm_client=llm_client), order=4)

    # ── Lifecycle Methods ──

    async def start(self) -> None:
        """启动运行时 — FSM IDLE → RUNNING"""
        if is_module_enabled("session_fsm"):
            self._fsm.transition(SessionState.RUNNING)
        self._dispatcher.dispatch_session_start(self._session_id, self._workspace_id)
        logger.info("ConversationRuntime started: session=%s", self._session_id)

    async def stop(self, reason: str = "complete") -> None:
        """停止运行时 — FSM → TERMINATED"""
        self._cancel_requested = True
        if is_module_enabled("session_fsm") and not self._fsm.is_terminal:
            self._fsm.transition(SessionState.TERMINATED)
        self._dispatcher.dispatch_session_end(self._session_id, self._workspace_id, reason)
        logger.info("ConversationRuntime stopped: session=%s, reason=%s", self._session_id, reason)

    def cancel(self) -> None:
        """请求取消 — 在下一个迭代边界生效"""
        self._cancel_requested = True
        logger.info("Cancel requested for session=%s", self._session_id)

    # ── Properties ──

    @property
    def session_id(self) -> str:
        return self._session_id

    @property
    def workspace_id(self) -> str:
        return self._workspace_id

    @property
    def user_id(self) -> str:
        return self._user_id

    @property
    def current_iteration(self) -> int:
        return self._current_iteration

    @property
    def is_running(self) -> bool:
        return self._fsm.is_running

    @property
    def skill_registry(self) -> SkillRegistry:
        return self._skill_registry
