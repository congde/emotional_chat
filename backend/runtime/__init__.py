# -*- coding: utf-8 -*-
"""
Runtime — Emotional Chat Agent Runtime

从线性 Workflow 升级为 Runtime + Skills 架构：
- Protocol-first: 三协议抽象 (LLM / Tool / Permission)
- Skill-based: 每个 workflow 阶段变为独立 Skill
- FSM-governed: 会话有 6 状态 FSM
- Toggle-gated: 每个模块可独立开关
- Hook-extensible: pre/post 行为可注入
- Policy-driven: 声明式规则引擎
- Workspace-isolated: 用户/会话工作区隔离
"""

from backend.runtime.protocols import (
    AssistantEvent,
    LLMClient,
    PermissionDecision,
    PermissionPrompter,
    PermissionRequest,
    ToolExecutor,
    ToolResult,
    TurnSummary,
)
from backend.runtime.session.fsm import SessionFSM, SessionState, IllegalTransitionError
from backend.runtime.config.toggles import ModuleToggles
from backend.runtime.config.guards import is_module_enabled, require_module
from backend.runtime.skills.base import Skill, SkillContext, SkillResult, SkillRegistry
from backend.runtime.skills.emotion_skill import EmotionSkill
from backend.runtime.skills.memory_skill import MemorySkill
from backend.runtime.skills.planning_skill import PlanningSkill
from backend.runtime.skills.reflect_skill import ReflectSkill
from backend.runtime.skills.tool_skill import ToolSkill
from backend.runtime.policy.policy_engine import PolicyEngine, PolicyRule
from backend.runtime.hooks.base import PluginHook, HookDispatcher, HookContext
from backend.runtime.conversation import ConversationRuntime
from backend.runtime.budget.pressure import BudgetPressure
from backend.runtime.fallback.manager import FallbackManager, FallbackConfig
from backend.runtime.workspace.manager import WorkspaceManager, WorkspaceInfo
from backend.runtime.activity.tracker import ActivityTracker
from backend.runtime.activity.distiller import ActivityDistiller, TurnDigest
from backend.runtime.prompt_builder import SystemPromptBuilder, PromptLayer
from backend.runtime.task_packet import TaskPacket, TaskPriority, TaskStatus

__all__ = [
    # Protocols
    "AssistantEvent",
    "LLMClient",
    "PermissionDecision",
    "PermissionPrompter",
    "PermissionRequest",
    "ToolExecutor",
    "ToolResult",
    "TurnSummary",
    # Session
    "SessionFSM",
    "SessionState",
    "IllegalTransitionError",
    # Config
    "ModuleToggles",
    "is_module_enabled",
    "require_module",
    # Skills
    "Skill",
    "SkillContext",
    "SkillResult",
    "SkillRegistry",
    "EmotionSkill",
    "MemorySkill",
    "PlanningSkill",
    "ReflectSkill",
    "ToolSkill",
    # Policy
    "PolicyEngine",
    "PolicyRule",
    # Hooks
    "PluginHook",
    "HookDispatcher",
    "HookContext",
    # Conversation
    "ConversationRuntime",
    # Budget
    "BudgetPressure",
    # Fallback
    "FallbackManager",
    "FallbackConfig",
    # Workspace
    "WorkspaceManager",
    "WorkspaceInfo",
    # Activity
    "ActivityTracker",
    "ActivityDistiller",
    "TurnDigest",
    # Prompt
    "SystemPromptBuilder",
    "PromptLayer",
    # Task
    "TaskPacket",
    "TaskPriority",
    "TaskStatus",
]
