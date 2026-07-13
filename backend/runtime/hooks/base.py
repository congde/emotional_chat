# -*- coding: utf-8 -*-
"""
Hook Protocol — 生命周期钩子

内置钩子: PreLLMCallHook, PostLLMCallHook, ToolUseFailureHook
自定义钩子通过 ConversationRuntime 构造函数注册。

注入语义：
  • on_pre_llm_call 返回 {"context": "..."} 会追加到用户消息
  • on_post_llm_call 是 fire-and-forget；错误被吞掉并记为 WARN
  • on_tool_use_failure 可以返回一个 dict 来替代错误结果

情感陪伴场景的典型 Hook：
  • 危机检测 Hook — 在 pre_llm_call 中注入安全指令
  • 情感追踪 Hook — 在 post_llm_call 中记录情感变化
  • 工具降级 Hook — 在 tool_use_failure 中返回安全默认值
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional, Protocol, runtime_checkable

logger = logging.getLogger(__name__)


# ── Context objects passed to hooks ──────────────────────────


@dataclass
class HookContext:
    """传递给每个 Hook 的不可变运行时状态快照"""

    session_id: str
    workspace_id: str
    iteration: int  # 1-based, 当前 ReAct 迭代
    model: str  # 当前模型名
    is_fallback: bool  # 是否在使用降级模型
    # 情感陪伴扩展
    emotion_tag: str = ""  # 当前情感标签
    user_id: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class ToolFailureContext(HookContext):
    """工具失败时的扩展上下文"""

    tool_name: str = ""
    tool_args: dict = field(default_factory=dict)
    error_message: str = ""


# ── Hook Protocol ────────────────────────────────────────────


@runtime_checkable
class PluginHook(Protocol):
    """
    ConversationRuntime 生命周期钩子协议

    实现此协议的任意子集方法 — 只有被实现的方法才会被调用。
    所有 Hook 方法都是同步的以保持运行时简单；I/O 操作使用
    asyncio.create_task() 在 Hook 体内执行。
    """

    def on_pre_llm_call(self, context: HookContext) -> Optional[dict]:
        """
        在每次 LLM API 调用之前被调用。

        Returns
        -------
        dict | None
            如果返回包含 ``"context"`` 键的 dict，值会被追加到
            当前轮次的最后一条用户消息。这是唯一的注入点以
            避免破坏 prompt cache。
            返回 None 不注入任何内容。
        """
        ...

    def on_post_llm_call(self, context: HookContext, response_text: str) -> None:
        """
        在每次 LLM 响应接收后被调用。

        适用于日志记录、成本计量和分析。
        这里抛出的错误会被捕获并记为 WARN — 不会中断 agent 循环。
        """
        ...

    def on_session_start(self, session_id: str, workspace_id: str) -> None:
        """会话开始时被调用（在第一个 turn 之前）"""
        ...

    def on_session_end(
        self, session_id: str, workspace_id: str, stop_reason: str
    ) -> None:
        """会话结束时被调用（在最后一个 turn 之后）"""
        ...

    def on_tool_use_failure(self, context: ToolFailureContext) -> Optional[dict]:
        """
        工具执行抛出未处理异常时被调用。

        Returns
        -------
        dict | None
            可以返回一个 dict 来替代错误结果，格式:
            {"output": "...", "error": None}
            返回 None 让原始错误传播。
        """
        ...


# ── Hook Dispatcher ──────────────────────────────────────────


class HookDispatcher:
    """
    钩子分发器 — 管理和分发生命周期事件给所有注册的 Hook

    Usage::

        dispatcher = HookDispatcher([
            CrisisDetectionHook(),
            EmotionTrackingHook(),
        ])

        # 分发事件
        result = dispatcher.dispatch_pre_llm_call(context)
        dispatcher.dispatch_post_llm_call(context, response)
    """

    def __init__(self, hooks: Optional[list] = None):
        self._hooks: list = hooks or []

    def add_hook(self, hook) -> None:
        """添加 Hook"""
        self._hooks.append(hook)

    def remove_hook(self, hook) -> None:
        """移除 Hook"""
        self._hooks.remove(hook)

    def dispatch_pre_llm_call(self, context: HookContext) -> Optional[dict]:
        """分发 pre_llm_call 事件"""
        merged: dict = {}
        for hook in self._hooks:
            try:
                if hasattr(hook, "on_pre_llm_call"):
                    result = hook.on_pre_llm_call(context)
                    if result and isinstance(result, dict):
                        merged.update(result)
            except Exception as e:
                logger.warning("Hook %s.on_pre_llm_call failed: %s", type(hook).__name__, e)
        return merged if merged else None

    def dispatch_post_llm_call(
        self, context: HookContext, response_text: str
    ) -> None:
        """分发 post_llm_call 事件"""
        for hook in self._hooks:
            try:
                if hasattr(hook, "on_post_llm_call"):
                    hook.on_post_llm_call(context, response_text)
            except Exception as e:
                logger.warning("Hook %s.on_post_llm_call failed: %s", type(hook).__name__, e)

    def dispatch_session_start(self, session_id: str, workspace_id: str) -> None:
        """分发 session_start 事件"""
        for hook in self._hooks:
            try:
                if hasattr(hook, "on_session_start"):
                    hook.on_session_start(session_id, workspace_id)
            except Exception as e:
                logger.warning("Hook %s.on_session_start failed: %s", type(hook).__name__, e)

    def dispatch_session_end(
        self, session_id: str, workspace_id: str, stop_reason: str
    ) -> None:
        """分发 session_end 事件"""
        for hook in self._hooks:
            try:
                if hasattr(hook, "on_session_end"):
                    hook.on_session_end(session_id, workspace_id, stop_reason)
            except Exception as e:
                logger.warning("Hook %s.on_session_end failed: %s", type(hook).__name__, e)

    def dispatch_tool_use_failure(
        self, context: ToolFailureContext
    ) -> Optional[dict]:
        """分发 tool_use_failure 事件"""
        for hook in self._hooks:
            try:
                if hasattr(hook, "on_tool_use_failure"):
                    result = hook.on_tool_use_failure(context)
                    if result is not None:
                        return result
            except Exception as e:
                logger.warning("Hook %s.on_tool_use_failure failed: %s", type(hook).__name__, e)
        return None

    @property
    def hook_count(self) -> int:
        return len(self._hooks)
