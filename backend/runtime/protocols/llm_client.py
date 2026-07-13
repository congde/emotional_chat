# -*- coding: utf-8 -*-
"""
Protocol 1: LLM Client — LLM 调用抽象

Defines the contract for LLM interaction. All ConversationRuntime
modules depend on this Protocol, never on concrete implementations.

Adapted for emotional chat:
- 支持 stream 和 complete 两种调用模式
- 统一的 AssistantEvent 事件格式
- 支持 tool_use 和纯文本两种输出
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import AsyncIterator, Literal, Protocol


@dataclass
class AssistantEvent:
    """LLM 流式事件 — 统一的事件格式"""

    type: Literal["text_delta", "tool_use", "stop", "usage"]
    text: str | None = None
    tool_name: str | None = None
    tool_args: dict | None = None
    call_id: str | None = None
    usage: dict | None = None  # {prompt_tokens, completion_tokens, cache_*}
    # 情感陪伴扩展字段
    emotion_tag: str | None = None  # "empathy" | "encouragement" | "neutral" | ...


@dataclass
class TurnSummary:
    """一轮对话的完整汇总"""

    text: str
    tool_calls: list[dict] = field(default_factory=list)
    usage: dict = field(default_factory=dict)  # {input_tokens, output_tokens, total_tokens}
    iterations: int = 0
    emotion_analysis: dict | None = None  # 情感分析结果（可选）


class LLMClient(Protocol):
    """LLM 通信协议 — 所有 LLM 提供商实现此接口"""

    async def stream_turn(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        *,
        system_prompt: str | None = None,
        max_tokens: int = 4096,
    ) -> AsyncIterator[AssistantEvent]:
        """流式调用 LLM，返回 AsyncIterator[AssistantEvent]"""
        ...

    async def complete(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        *,
        system_prompt: str | None = None,
        max_tokens: int = 4096,
    ) -> TurnSummary:
        """非流式调用 LLM，返回完整的 TurnSummary"""
        ...
