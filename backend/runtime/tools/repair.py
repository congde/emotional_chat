# -*- coding: utf-8 -*-
"""
Tool Call Repair — 模糊修复工具名称

当 LLM 生成的工具名称有轻微拼写错误时，尝试修复到最近的匹配。
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def repair_tool_calls(
    tool_calls: List[Dict[str, Any]],
    available_tools: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    修复工具调用中的拼写错误

    Args:
        tool_calls: 工具调用列表
        available_tools: 可用工具名称列表

    Returns:
        修复后的工具调用列表
    """
    if not tool_calls or not available_tools:
        return tool_calls

    repaired: List[Dict[str, Any]] = []
    for call in tool_calls:
        name = call.get("name", "") or call.get("function", {}).get("name", "")

        if name and name not in available_tools:
            # 尝试模糊匹配
            best_match = _fuzzy_match(name, available_tools)
            if best_match:
                logger.info("Repaired tool name: '%s' → '%s'", name, best_match)
                call = _replace_tool_name(call, best_match)

        repaired.append(call)

    return repaired


def _fuzzy_match(name: str, available: List[str], threshold: float = 0.7) -> Optional[str]:
    """模糊匹配工具名称"""
    name_lower = name.lower()

    # 精确匹配（忽略大小写）
    for tool in available:
        if tool.lower() == name_lower:
            return tool

    # 前缀匹配
    for tool in available:
        if tool.lower().startswith(name_lower) or name_lower.startswith(tool.lower()):
            return tool

    # 编辑距离匹配
    best_score = 0.0
    best_tool = None
    for tool in available:
        score = _similarity(name_lower, tool.lower())
        if score > best_score:
            best_score = score
            best_tool = tool

    if best_score >= threshold:
        return best_tool

    return None


def _similarity(a: str, b: str) -> float:
    """计算两个字符串的相似度 (简化版 Jaccard)"""
    if not a or not b:
        return 0.0

    set_a = set(a)
    set_b = set(b)
    intersection = set_a & set_b
    union = set_a | set_b

    if not union:
        return 0.0

    return len(intersection) / len(union)


def _replace_tool_name(call: Dict[str, Any], new_name: str) -> Dict[str, Any]:
    """替换工具调用中的名称"""
    call = dict(call)
    if "name" in call:
        call["name"] = new_name
    if "function" in call and isinstance(call["function"], dict):
        call["function"] = dict(call["function"])
        call["function"]["name"] = new_name
    return call
