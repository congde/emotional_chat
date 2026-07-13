# -*- coding: utf-8 -*-
"""
Budget Warning Strip — 在 turn 开始时移除过期预算警告
"""

from __future__ import annotations

import logging
from typing import List

logger = logging.getLogger(__name__)


def strip_budget_warnings(messages: List[dict]) -> List[dict]:
    """
    移除消息中的预算警告标记

    在每个 turn 开始时调用，确保上一 turn 的预算警告不会
    影响当前 turn 的 LLM 上下文。
    """
    stripped = []
    for msg in messages:
        content = msg.get("content", "")
        if isinstance(content, str):
            # 移除预算警告行
            lines = content.split("\n")
            cleaned = [
                line
                for line in lines
                if not line.startswith("[系统提示:")
                and not line.startswith("⚠️")
                and not line.startswith("⏳")
                and not line.startswith("💡")
            ]
            msg = {**msg, "content": "\n".join(cleaned)}
        stripped.append(msg)
    return stripped
