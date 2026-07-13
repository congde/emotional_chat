# -*- coding: utf-8 -*-
"""
Agent Core — Runtime + Skills 适配层

本模块是旧 AgentCore 的 **Runtime 版本**，
对外接口完全兼容 `AgentCore`，内部委托给 `ConversationRuntime`。

迁移映射：
  AgentCore.process()       → ConversationRuntime.process_turn()
  AgentCore._perceive()     → EmotionSkill.execute(mode="analyze")
  AgentCore.memory_hub      → MemorySkill + MemoryHub (注入)
  AgentCore.planner         → PlanningSkill.execute(mode="plan")
  AgentCore.tool_caller     → ToolSkill + ToolExecutor Protocol
  AgentCore.reflector       → ReflectSkill.execute(mode="evaluate")
  MCP 协议通信              → Protocol 依赖注入 (LLMClient / ToolExecutor / PermissionPrompter)
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ── Protocol 适配器 ──────────────────────────────────────────


class _LLMClientAdapter:
    """
    将旧的 LLM 调用方式适配为 LLMClient Protocol

    旧方式: self.llm / self._call_llm(context, user_input)
    新方式: LLMClient.stream_turn() / LLMClient.complete()

    Protocol 签名:
        complete(messages, tools=None, *, system_prompt=None, max_tokens=4096) → TurnSummary
        stream_turn(messages, tools=None, *, system_prompt=None, max_tokens=4096) → AsyncIterator[AssistantEvent]
    """

    def __init__(self, legacy_llm=None, context_assembler=None, emotion_analyzer=None):
        self._llm = legacy_llm
        self._context_assembler = context_assembler
        self._emotion_analyzer = emotion_analyzer

    async def stream_turn(
        self,
        messages: list,
        tools: list | None = None,
        *,
        system_prompt: str | None = None,
        max_tokens: int = 4096,
    ):
        """流式输出 — 返回 async generator"""
        from runtime.protocols.llm_client import AssistantEvent

        if self._llm and hasattr(self._llm, "astream"):
            async for chunk in self._llm.astream(messages, system=system_prompt):
                yield AssistantEvent(
                    type="text_delta",
                    text=chunk,
                    emotion_tag="",
                )
        else:
            # 降级: 同步生成后一次性输出
            summary = await self.complete(messages, tools, system_prompt=system_prompt, max_tokens=max_tokens)
            yield AssistantEvent(type="text_delta", text=summary.text, emotion_tag="")
            yield AssistantEvent(type="stop", text=None, usage=summary.usage)

    async def complete(
        self,
        messages: list,
        tools: list | None = None,
        *,
        system_prompt: str | None = None,
        max_tokens: int = 4096,
    ):
        """完整生成 — 返回 TurnSummary"""
        from runtime.protocols.llm_client import TurnSummary

        text = ""

        if self._llm and hasattr(self._llm, "agenerate"):
            text = await self._llm.agenerate(messages, system=system_prompt)
        elif self._llm and hasattr(self._llm, "generate"):
            text = self._llm.generate(messages, system=system_prompt)
        else:
            # 降级: 使用模板回复
            text = "我在这里倾听你的感受。能多告诉我一些吗？"

        return TurnSummary(text=text, usage={"input_tokens": 0, "output_tokens": 0})


class _ToolExecutorAdapter:
    """
    将旧的 ToolCaller 适配为 ToolExecutor Protocol

    旧方式: ToolCaller.call(tool_name, parameters)
    新方式: ToolExecutor.execute(tool_name, parameters)
    """

    def __init__(self, legacy_tool_caller=None):
        self._tool_caller = legacy_tool_caller

    async def execute(self, tool_name: str, parameters: dict, **kwargs) -> Any:
        """执行工具调用"""
        if self._tool_caller:
            return await self._tool_caller.call(tool_name, parameters)
        raise RuntimeError(f"Tool not found: {tool_name}")

    def list_tools(self) -> list:
        """列出可用工具"""
        if self._tool_caller and hasattr(self._tool_caller, "registry"):
            return [
                {"name": t.name, "description": t.description, "parameters": t.parameters}
                for t in self._tool_caller.registry.list_tools()
            ]
        return []


class _PermissionPrompterAdapter:
    """
    权限确认 — 情感陪伴场景默认自动批准（无危险操作）

    如果后续需要用户确认（如删除记忆等），可替换实现。
    """

    async def confirm(self, request) -> Any:
        """自动批准"""
        from runtime.protocols.permission_prompter import PermissionDecision
        return PermissionDecision(approved=True, reason="auto_approved")


# ── AgentCore (Runtime 版) ──────────────────────────────────


class AgentCore:
    """
    Agent核心控制器 — Runtime + Skills 版

    对外接口与旧版完全兼容：
      - process(user_input, user_id, conversation_id) → dict
      - process_with_mcp(...) → MCPMessage (兼容旧 MCP 接口)
      - get_agent_status() → dict
      - get_execution_history(user_id, limit) → list

    内部使用 ConversationRuntime + Skill 系统：
      - EmotionSkill 替代 _perceive()
      - MemorySkill 替代 memory_hub 阶段
      - PlanningSkill 替代 planner
      - ToolSkill 替代 tool_caller
      - ReflectSkill 替代 reflector
    """

    def __init__(
        self,
        memory_hub=None,
        planner=None,
        tool_caller=None,
        reflector=None,
        llm_client=None,
    ):
        """
        初始化 — 自动检测并使用 Runtime 或回退到旧模式
        """
        self._use_runtime = True

        # 保留旧组件引用（向后兼容）
        self.memory_hub = memory_hub
        self.planner = planner
        self.tool_caller = tool_caller
        self.reflector = reflector
        self.llm = llm_client

        # 初始化旧组件（如果未传入）
        self._init_legacy_components()

        # 初始化 Runtime
        self._runtime = None
        self._runtime_key = None
        # AgentCore remains a process-wide singleton for backward compatibility.
        # Serialize turns while its Runtime/Skill dependencies are rebound to a
        # user scope, preventing concurrent requests from crossing scopes.
        self._process_lock = asyncio.Lock()
        self._execution_history: List[Dict[str, Any]] = []

        # MCP 兼容字段
        self.use_mcp = False  # Runtime 模式不需要 MCP

    def _init_legacy_components(self):
        """初始化现有系统组件（向后兼容）"""
        try:
            if self.memory_hub is None:
                from .memory_hub import get_memory_hub
                self.memory_hub = get_memory_hub()
        except ImportError:
            self.memory_hub = None

        try:
            if self.planner is None:
                from .planner import Planner
                self.planner = Planner(self.llm)
        except ImportError:
            self.planner = None

        try:
            if self.tool_caller is None:
                from .tool_caller import get_tool_caller
                self.tool_caller = get_tool_caller()
        except ImportError:
            self.tool_caller = None

        try:
            if self.reflector is None:
                from .reflector import get_reflector
                self.reflector = get_reflector()
        except ImportError:
            self.reflector = None

        # 旧系统组件
        try:
            from backend.emotion_analyzer import EmotionAnalyzer
            from backend.context_assembler import ContextAssembler
            self.emotion_analyzer = EmotionAnalyzer()
            self.context_assembler = ContextAssembler()
        except ImportError:
            self.emotion_analyzer = None
            self.context_assembler = None

    def _build_runtime(self, user_id: str, session_id: Optional[str] = None):
        """
        构建 ConversationRuntime 实例

        每个用户/会话创建独立的 Runtime 实例。
        """
        from runtime.conversation import ConversationRuntime

        # 创建 Protocol 适配器
        llm_adapter = _LLMClientAdapter(
            legacy_llm=self.llm,
            context_assembler=self.context_assembler,
            emotion_analyzer=self.emotion_analyzer,
        )
        tool_adapter = _ToolExecutorAdapter(legacy_tool_caller=self.tool_caller)
        permission_adapter = _PermissionPrompterAdapter()

        # 创建 Runtime — 参数名匹配 LifecycleMixin.__init__
        runtime = ConversationRuntime(
            user_id=user_id,
            session_id=session_id or f"session_{uuid.uuid4().hex[:8]}",
            llm_client=llm_adapter,
            tool_executor=tool_adapter,
            memory_hub=self.memory_hub,
            emotion_analyzer=self.emotion_analyzer,
        )

        # 注入 permission prompter（通过属性注入）
        runtime._permission = permission_adapter

        return runtime

    # ── 主要接口 ──────────────────────────────────────────────

    async def process(
        self,
        user_input: str,
        user_id: str,
        conversation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        处理用户输入 — Runtime 版

        对外接口与旧版完全兼容，内部使用 ConversationRuntime.process_turn()
        """
        interaction_id = str(uuid.uuid4())
        start_time = datetime.now()

        async with self._process_lock:
            if self._use_runtime:
                return await self._process_with_runtime(
                    user_input=user_input,
                    user_id=user_id,
                    conversation_id=conversation_id,
                    interaction_id=interaction_id,
                    start_time=start_time,
                )
            else:
                # 回退到旧模式
                return await self._process_legacy(
                    user_input=user_input,
                    user_id=user_id,
                    conversation_id=conversation_id,
                    interaction_id=interaction_id,
                    start_time=start_time,
                )

    async def _process_with_runtime(
        self,
        user_input: str,
        user_id: str,
        conversation_id: Optional[str],
        interaction_id: str,
        start_time: datetime,
    ) -> Dict[str, Any]:
        """使用 ConversationRuntime 处理"""
        try:
            runtime_key = (user_id, conversation_id or "")
            # 1. 构建或复用 Runtime
            if self._runtime is None or self._runtime_key != runtime_key:
                from .memory_hub import get_memory_hub_async

                self.memory_hub = await get_memory_hub_async(
                    user_id=user_id,
                    session_id=conversation_id or "",
                )
                self._runtime = self._build_runtime(user_id, conversation_id)
                self._runtime_key = runtime_key
                await self._runtime.start()

            # 2. 注入旧系统依赖到 Skill
            self._inject_legacy_deps()

            # 3. 调用 process_turn
            result = await self._runtime.process_turn(user_input=user_input)

            # 4. 记录历史
            response_time = (datetime.now() - start_time).total_seconds()

            # 从 TurnResult 提取数据
            emotion_data = result.skill_results.get("emotion_skill", {})
            emotion = emotion_data.get("output", {}).get("emotion", "") if isinstance(emotion_data, dict) else ""
            emotion_intensity = emotion_data.get("output", {}).get("emotion_intensity", 0) if isinstance(emotion_data, dict) else 0
            evaluation_data = result.skill_results.get("reflect_skill", {})

            execution_record = {
                "interaction_id": interaction_id,
                "user_id": user_id,
                "timestamp": datetime.now(),
                "response": result.response,
                "emotion": emotion,
                "emotion_intensity": emotion_intensity,
                "skill_results": result.skill_results,
                "evaluation": evaluation_data,
                "response_time": response_time,
                "mode": "runtime",
                "iterations": result.iterations,
            }
            self._execution_history.append(execution_record)

            # 5. 返回兼容格式
            return {
                "success": result.success,
                "interaction_id": interaction_id,
                "response": result.response,
                "actions": [],  # Skill results 已在 skill_results 中
                "emotion": emotion,
                "emotion_intensity": emotion_intensity,
                "evaluation": evaluation_data,
                "followup_scheduled": False,
                "response_time": response_time,
                "iterations": result.iterations,
                "emotion_tag": result.emotion_tag,
            }

        except Exception as e:
            logger.error("Runtime处理错误: %s", e, exc_info=True)

            # 降级到旧模式
            logger.info("降级到旧模式处理")
            return await self._process_legacy(
                user_input=user_input,
                user_id=user_id,
                conversation_id=conversation_id,
                interaction_id=interaction_id,
                start_time=start_time,
            )

    def _inject_legacy_deps(self):
        """将旧系统组件注入到 Skill 中"""
        if self._runtime is None:
            return

        # 注入 EmotionAnalyzer 到 EmotionSkill
        try:
            emotion_skill = self._runtime._skill_registry.get_skill("emotion_skill")
            if emotion_skill and hasattr(emotion_skill, "_emotion_analyzer"):
                emotion_skill._emotion_analyzer = self.emotion_analyzer
        except Exception:
            pass

        # 注入 MemoryHub 到 MemorySkill
        try:
            memory_skill = self._runtime._skill_registry.get_skill("memory_skill")
            if memory_skill and hasattr(memory_skill, "_memory_hub"):
                memory_skill._memory_hub = self.memory_hub
        except Exception:
            pass

    async def _process_legacy(
        self,
        user_input: str,
        user_id: str,
        conversation_id: Optional[str],
        interaction_id: str,
        start_time: datetime,
    ) -> Dict[str, Any]:
        """
        旧模式处理 — 7 阶段线性 Workflow（向后兼容回退）

        当 Runtime 初始化失败或被禁用时使用。
        """
        try:
            from .memory_hub import get_memory_hub_async

            self.memory_hub = await get_memory_hub_async(
                user_id=user_id,
                session_id=conversation_id or "",
            )
            # ===== 阶段1: 感知层 =====
            perception = await self._perceive(user_input, user_id)

            # ===== 阶段2: 记忆检索 =====
            relevant_memories = []
            user_profile = {}
            if self.memory_hub:
                current_memory = self.memory_hub.encode({
                    "content": user_input,
                    "emotion": perception.get("emotion_data", {}),
                    "user_id": user_id,
                    "role": "user",
                })
                relevant_memories = self.memory_hub.retrieve(
                    query=user_input, user_id=user_id,
                    context={"emotion": perception.get("emotion", ""), "time_range": 30},
                    top_k=5,
                )
                user_profile = await self.memory_hub.get_user_profile(user_id) or {}

            # ===== 阶段3: 任务规划 =====
            execution_plan = None
            if self.planner:
                planning_context = {
                    "user_input": user_input, "user_id": user_id,
                    "perception": perception, "memories": relevant_memories,
                    "user_profile": user_profile,
                }
                execution_plan = await self.planner.plan(user_input, planning_context)

            # ===== 阶段4: 执行 =====
            execution_results = {"response": "", "actions": []}
            if execution_plan:
                execution_results = await self._execute_plan(execution_plan, {
                    "user_input": user_input, "user_id": user_id,
                    "perception": perception, "memories": relevant_memories,
                    "user_profile": user_profile,
                })
            else:
                # 无 Planner，直接生成回复
                execution_results["response"] = await self._generate_response(
                    user_input, {"perception": perception}, []
                )

            # ===== 阶段5: 记忆巩固 =====
            if self.memory_hub:
                self.memory_hub.consolidate(current_memory if 'current_memory' in dir() else None)
                self.memory_hub.update_working_memory(conversation=[
                    {"role": "user", "content": user_input},
                    {"role": "assistant", "content": execution_results.get("response", "")},
                ])

            # ===== 阶段6: 反思评估 =====
            evaluation = None
            followup = None
            response_time = (datetime.now() - start_time).total_seconds()

            if self.reflector:
                interaction = {
                    "id": interaction_id, "user_id": user_id,
                    "input": user_input, "perception": perception,
                    "response": execution_results.get("response", ""),
                    "response_time": response_time,
                    "timestamp": datetime.now(),
                }
                evaluation = await self.reflector.evaluate(interaction)
                followup = await self.reflector.plan_followup(user_id, {
                    "perception": perception,
                })

            # ===== 阶段7: 记录历史 =====
            self._execution_history.append({
                "interaction_id": interaction_id, "user_id": user_id,
                "timestamp": datetime.now(), "perception": perception,
                "results": execution_results, "evaluation": evaluation,
                "response_time": response_time, "mode": "legacy",
            })

            return {
                "success": True,
                "interaction_id": interaction_id,
                "response": execution_results.get("response", ""),
                "actions": execution_results.get("actions", []),
                "emotion": perception.get("emotion", ""),
                "emotion_intensity": perception.get("emotion_intensity", 0),
                "evaluation": evaluation,
                "followup_scheduled": followup is not None,
                "response_time": response_time,
            }

        except Exception as e:
            logger.error("Legacy处理错误: %s", e, exc_info=True)
            return {
                "success": False,
                "interaction_id": interaction_id,
                "response": "抱歉，我遇到了一些问题。能再说一遍吗？",
                "error": str(e),
                "response_time": (datetime.now() - start_time).total_seconds(),
            }

    # ── MCP 兼容接口 ─────────────────────────────────────────

    async def process_with_mcp(
        self,
        user_input: str,
        user_id: str,
        conversation_id: Optional[str] = None,
    ):
        """
        MCP 协议处理（兼容旧接口）

        Runtime 模式不再使用 MCP，此方法转为调用 process() 并包装为兼容格式。
        """
        result = await self.process(user_input, user_id, conversation_id)

        # 尝试返回 MCP 消息格式
        try:
            from backend.modules.agent.protocol.mcp import MCPMessage, MCPContext, MCPMessageType
            return MCPMessage(
                message_type=MCPMessageType.AGENT_RESPONSE,
                content=result.get("response", ""),
                context=MCPContext(user_profile={"user_id": user_id}),
                metadata=result,
            )
        except ImportError:
            # MCP 模块不可用，返回原始字典
            return result

    # ── 旧版辅助方法（向后兼容）────────────────────────────────

    async def _perceive(self, user_input: str, user_id: str) -> Dict[str, Any]:
        """感知层 — 情绪分析 + 意图识别"""
        perception = {}
        if self.emotion_analyzer:
            try:
                emotion_result = self.emotion_analyzer.analyze(user_input)
                perception["emotion"] = emotion_result.get("emotion", "平静")
                perception["emotion_intensity"] = emotion_result.get("intensity", 5.0)
                perception["emotion_data"] = emotion_result
            except Exception:
                perception["emotion"] = "平静"
                perception["emotion_intensity"] = 5.0
        else:
            perception["emotion"] = self._simple_emotion_detect(user_input)
            perception["emotion_intensity"] = 5.0
        perception["intent"] = self._identify_intent(user_input)
        perception["entities"] = self._extract_entities(user_input)
        return perception

    async def _execute_plan(self, execution_plan, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行计划"""
        results = {"response": "", "actions": [], "tool_outputs": []}
        tool_outputs = []
        for step in execution_plan.steps:
            action = step.get("action")
            if action == "tool_call" and self.tool_caller:
                tool_name = step.get("tool")
                parameters = step.get("parameters", {})
                try:
                    tool_result = await self.tool_caller.call(tool_name, parameters)
                    tool_outputs.append(tool_result)
                    results["actions"].append({
                        "type": "tool_call", "tool": tool_name,
                        "success": tool_result.get("success", False),
                        "result": tool_result.get("result"),
                    })
                except Exception as e:
                    results["actions"].append({
                        "type": "tool_call", "tool": tool_name,
                        "success": False, "error": str(e),
                    })
            elif action == "respond":
                response = await self._generate_response(
                    context.get("user_input", ""), context, tool_outputs
                )
                results["response"] = response
                results["actions"].append({"type": "response", "content": response})
        results["tool_outputs"] = tool_outputs
        return results

    async def _generate_response(self, user_input: str, context: Dict, tool_outputs: list) -> str:
        """生成回复"""
        if self.llm:
            return await self._call_llm("", user_input)
        return self._template_response(context.get("perception", {}), tool_outputs)

    async def _call_llm(self, context: str, user_input: str) -> str:
        """调用 LLM"""
        return "我理解你的感受。让我们一起面对这个问题。"

    def _template_response(self, perception: Dict, tool_outputs: list) -> str:
        """模板回复"""
        emotion = perception.get("emotion", "")
        templates = {
            "焦虑": "我能感受到你的焦虑。深呼吸，我们一起来面对。",
            "难过": "我能理解你现在的难过。想聊聊吗？",
            "愤怒": "我听到了你的愤怒。能告诉我发生了什么吗？",
            "开心": "真为你感到开心！",
        }
        return templates.get(emotion, "我在这里倾听。想跟我聊聊吗？")

    def _simple_emotion_detect(self, text: str) -> str:
        """简单情绪检测"""
        emotion_keywords = {
            "焦虑": ["焦虑", "担心", "紧张", "不安"],
            "难过": ["难过", "伤心", "失落", "沮丧"],
            "愤怒": ["生气", "愤怒", "气愤"],
            "开心": ["开心", "高兴", "快乐"],
            "恐惧": ["害怕", "恐惧"],
        }
        for emotion, keywords in emotion_keywords.items():
            if any(kw in text for kw in keywords):
                return emotion
        return "平静"

    def _identify_intent(self, text: str) -> str:
        """意图识别"""
        if any(kw in text for kw in ["怎么办", "怎么做", "如何", "帮我"]):
            return "problem_solving"
        elif any(kw in text for kw in ["是什么", "为什么"]):
            return "information_query"
        elif any(kw in text for kw in ["计划", "打算", "决定"]):
            return "behavior_change"
        return "emotional_support"

    def _extract_entities(self, text: str) -> List[str]:
        """实体提取"""
        entities = []
        for kw in ["今天", "昨天", "明天"]:
            if kw in text:
                entities.append(f"时间:{kw}")
        for kw in ["考试", "面试", "会议"]:
            if kw in text:
                entities.append(f"事件:{kw}")
        return entities

    # ── 状态接口 ──────────────────────────────────────────────

    def get_execution_history(
        self,
        user_id: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """获取执行历史"""
        history = self._execution_history
        if user_id:
            history = [h for h in history if h.get("user_id") == user_id]
        return history[-limit:]

    def get_agent_status(self) -> Dict[str, Any]:
        """获取 Agent 状态"""
        status = {
            "status": "running",
            "mode": "runtime" if self._use_runtime else "legacy",
            "modules": {},
            "statistics": {
                "total_interactions": len(self._execution_history),
            },
        }

        if self._use_runtime and self._runtime:
            try:
                health = self._runtime.health_check()
                status["modules"] = health
            except Exception:
                status["modules"] = {"runtime": "error"}

            # Runtime 中的 Skill 信息
            try:
                skills = self._runtime._skill_registry.list_skills()
                status["modules"]["skills"] = [s["name"] for s in skills]
                status["statistics"]["available_skills"] = len(skills)
            except Exception:
                pass
        else:
            # 旧模式状态
            status["modules"] = {
                "memory_hub": "active" if self.memory_hub else "unavailable",
                "planner": "active" if self.planner else "unavailable",
                "tool_caller": "active" if self.tool_caller else "unavailable",
                "reflector": "active" if self.reflector else "unavailable",
            }
            if self.tool_caller and hasattr(self.tool_caller, "registry"):
                status["statistics"]["available_tools"] = len(
                    self.tool_caller.registry.get_available_tools()
                )

        return status


# ── 单例 ────────────────────────────────────────────────────

_agent_core_instance = None


def get_agent_core() -> AgentCore:
    """获取全局 AgentCore 实例"""
    global _agent_core_instance
    if _agent_core_instance is None:
        _agent_core_instance = AgentCore()
    return _agent_core_instance
