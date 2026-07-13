# -*- coding: utf-8 -*-
"""
Helpers — 共享工具和数据结构
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class TurnResult:
    """一轮对话的完整结果"""

    success: bool
    response: str = ""
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    skill_results: Dict[str, Any] = field(default_factory=dict)
    emotion_tag: Optional[str] = None
    usage: Dict[str, int] = field(default_factory=dict)
    iterations: int = 0
    stop_reason: str = ""  # "complete" | "budget_exceeded" | "error" | "cancelled"
    metadata: Dict[str, Any] = field(default_factory=dict)


def _done_dict(result: TurnResult) -> Dict[str, Any]:
    """将 TurnResult 转换为 SSE 事件 dict"""
    return {
        "type": "done",
        "success": result.success,
        "response": result.response,
        "emotion_tag": result.emotion_tag,
        "stop_reason": result.stop_reason,
        "iterations": result.iterations,
        "usage": result.usage,
    }


def _error_dict(error: str, **extra) -> Dict[str, Any]:
    """构造错误 SSE 事件 dict"""
    return {
        "type": "error",
        "error": error,
        **extra,
    }
