# -*- coding: utf-8 -*-
"""
Tool Call Dedup — 去除重复的工具调用

当 LLM 在一次响应中生成重复的工具调用时，去除重复项。
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def deduplicate_tool_calls(tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    去除重复的工具调用

    基于 (tool_name, tool_args) 的组合去重。
    保留第一个出现的调用，移除后续重复。

    Args:
        tool_calls: 工具调用列表

    Returns:
        去重后的工具调用列表
    """
    if not tool_calls:
        return []

    seen: set = set()
    deduped: List[Dict[str, Any]] = []

    for call in tool_calls:
        name = call.get("name", "") or call.get("function", {}).get("name", "")
        args = call.get("arguments", {}) or call.get("function", {}).get("arguments", {})

        # 序列化 args 用于去重
        if isinstance(args, str):
            args_key = args
        else:
            import json
            try:
                args_key = json.dumps(args, sort_keys=True)
            except (TypeError, ValueError):
                args_key = str(args)

        key = (name, args_key)
        if key not in seen:
            seen.add(key)
            deduped.append(call)
        else:
            logger.debug("Deduped tool call: %s", name)

    return deduped
