"""
Agent模块 - 智能Agent核心 (Runtime + Skills 版)

提供完整的Agent功能，包括：
- Agent Core V2: Runtime + Skills 架构（推荐）
- Agent Core: 旧版7阶段线性Workflow（兼容回退）
- Memory Hub: 记忆中枢
- Planner: 任务规划
- Tool Caller: 工具调用
- Reflector: 反思优化

架构升级：
  旧版 AgentCore.process() → 7阶段线性 workflow
  新版 AgentCore (V2) → ConversationRuntime + Skill-based ReAct 循环

使用方式：
  from backend.agent import get_agent_core  # 自动使用 V2
  agent = get_agent_core()
  result = await agent.process(user_input="...", user_id="...")
"""

# V2 (Runtime + Skills) 作为默认
from .agent_core_v2 import AgentCore, get_agent_core

# 旧版组件（仍可单独使用）
from .memory_hub import MemoryHub, get_memory_hub
from .planner import Planner
from .tool_caller import ToolCaller, get_tool_caller
from .reflector import Reflector, get_reflector

# 旧版 AgentCore 可通过显式导入使用
# from backend.agent.agent_core import AgentCore as LegacyAgentCore

__all__ = [
    # 默认使用 V2
    "AgentCore",
    "get_agent_core",
    # 旧版组件
    "MemoryHub",
    "get_memory_hub",
    "Planner",
    "ToolCaller",
    "get_tool_caller",
    "Reflector",
    "get_reflector",
]
