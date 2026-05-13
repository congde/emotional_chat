#!/usr/bin/env python3
"""Test all runtime module imports."""
import sys

errors = []

def test_import(label, statement):
    try:
        exec(statement, {"__builtins__": __builtins__})
        print(f"  ✓ {label}")
    except Exception as e:
        print(f"✗ {label}: {e}")
        errors.append((label, str(e)))

print("=== Runtime Module Import Tests ===\n")

# 1. Protocols
test_import("protocols.llm_client", "from backend.runtime.protocols.llm_client import LLMClient, TurnSummary, AssistantEvent")
test_import("protocols.tool_executor", "from backend.runtime.protocols.tool_executor import ToolExecutor, ToolResult")
test_import("protocols.permission_prompter", "from backend.runtime.protocols.permission_prompter import PermissionPrompter, PermissionRequest, PermissionDecision")

# 2. Session
test_import("session.fsm", "from backend.runtime.session.fsm import SessionFSM, SessionState, IllegalTransitionError")
test_import("session.lineage", "from backend.runtime.session.lineage import LineageTracker, SessionLineage")
test_import("session.resume", "from backend.runtime.session.resume import SessionResumer")

# 3. Config
test_import("config.toggles", "from backend.runtime.config.toggles import ModuleToggles")
test_import("config.guards", "from backend.runtime.config.guards import is_module_enabled, require_module, ModuleDisabledError")

# 4. Skills
test_import("skills.base", "from backend.runtime.skills.base import Skill, SkillContext, SkillResult, SkillRegistry")
test_import("skills.emotion_skill", "from backend.runtime.skills.emotion_skill import EmotionSkill")
test_import("skills.memory_skill", "from backend.runtime.skills.memory_skill import MemorySkill")
test_import("skills.planning_skill", "from backend.runtime.skills.planning_skill import PlanningSkill")
test_import("skills.reflect_skill", "from backend.runtime.skills.reflect_skill import ReflectSkill")
test_import("skills.tool_skill", "from backend.runtime.skills.tool_skill import ToolSkill")

# 5. Policy + Hooks
test_import("policy.policy_engine", "from backend.runtime.policy.policy_engine import PolicyEngine, PolicyRule")
test_import("hooks.base", "from backend.runtime.hooks.base import PluginHook, HookDispatcher, HookContext")

# 6. Conversation
test_import("conversation", "from backend.runtime.conversation import ConversationRuntime")

# 7. Budget
test_import("budget.pressure", "from backend.runtime.budget.pressure import BudgetPressure")
test_import("budget.warning", "from backend.runtime.budget.warning import strip_budget_warnings")

# 8. Fallback
test_import("fallback.manager", "from backend.runtime.fallback.manager import FallbackManager, FallbackConfig")

# 9. Workspace
test_import("workspace.manager", "from backend.runtime.workspace.manager import WorkspaceManager, WorkspaceInfo")

# 10. Activity
test_import("activity.tracker", "from backend.runtime.activity.tracker import ActivityTracker")
test_import("activity.distiller", "from backend.runtime.activity.distiller import ActivityDistiller, TurnDigest")

# 11. Tools
test_import("tools.dedup", "from backend.runtime.tools.dedup import deduplicate_tool_calls")
test_import("tools.repair", "from backend.runtime.tools.repair import repair_tool_calls")

# 12. Prompt + Task
test_import("prompt_builder", "from backend.runtime.prompt_builder import SystemPromptBuilder, PromptLayer")
test_import("task_packet", "from backend.runtime.task_packet import TaskPacket, TaskPriority, TaskStatus")

# 13. Top-level
test_import("runtime __init__", "from backend.runtime import ConversationRuntime, ModuleToggles, SkillRegistry, PolicyEngine")

# 14. Agent V2
test_import("agent_core_v2", "from backend.agent.agent_core_v2 import AgentCore")

print(f"\n{'='*40}")
if errors:
    print(f"FAILED: {len(errors)} errors")
    for label, err in errors:
        print(f"  - {label}: {err}")
    sys.exit(1)
else:
    print("ALL PASSED ✓")
    sys.exit(0)
