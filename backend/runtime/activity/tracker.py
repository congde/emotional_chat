# -*- coding: utf-8 -*-
"""
ActivityTracker — 活动追踪器

追踪每次 Skill 执行和工具调用的活动记录。
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ActivityRecord:
    """单次活动记录"""

    session_id: str
    timestamp: float
    activity_type: str  # "skill" | "tool" | "llm" | "memory"
    name: str
    success: bool
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ActivityTracker:
    """
    活动追踪器 — 记录运行时中的所有活动

    Usage::

        tracker = ActivityTracker(session_id="session_123")
        tracker.record_skill("emotion_skill", success=True, duration_ms=50)
    """

    def __init__(self, session_id: str = "", max_records: int = 1000):
        self._session_id = session_id
        self._records: List[ActivityRecord] = []
        self._max_records = max_records

    def record_skill(
        self, name: str, success: bool, duration_ms: float = 0.0, **metadata
    ) -> None:
        """记录 Skill 执行"""
        self._add_record(
            activity_type="skill",
            name=name,
            success=success,
            duration_ms=duration_ms,
            **metadata,
        )

    def record_tool(
        self, name: str, success: bool, duration_ms: float = 0.0, **metadata
    ) -> None:
        """记录工具调用"""
        self._add_record(
            activity_type="tool",
            name=name,
            success=success,
            duration_ms=duration_ms,
            **metadata,
        )

    def record_llm(
        self, success: bool, duration_ms: float = 0.0, **metadata
    ) -> None:
        """记录 LLM 调用"""
        self._add_record(
            activity_type="llm",
            name="llm_call",
            success=success,
            duration_ms=duration_ms,
            **metadata,
        )

    def _add_record(
        self,
        activity_type: str,
        name: str,
        success: bool,
        duration_ms: float = 0.0,
        **metadata,
    ) -> None:
        """添加活动记录"""
        record = ActivityRecord(
            session_id=self._session_id,
            timestamp=time.time(),
            activity_type=activity_type,
            name=name,
            success=success,
            duration_ms=duration_ms,
            metadata=metadata,
        )
        self._records.append(record)

        # 裁剪记录
        if len(self._records) > self._max_records:
            self._records = self._records[-self._max_records:]

    def get_recent(self, limit: int = 100) -> List[ActivityRecord]:
        """获取最近的活动记录"""
        return self._records[-limit:]

    def get_skill_stats(self) -> Dict[str, Dict[str, Any]]:
        """获取 Skill 执行统计"""
        stats: Dict[str, Dict[str, Any]] = {}
        for record in self._records:
            if record.activity_type != "skill":
                continue
            bucket = stats.setdefault(record.name, {"count": 0, "success": 0, "failure": 0, "total_ms": 0.0})
            bucket["count"] += 1
            if record.success:
                bucket["success"] += 1
            else:
                bucket["failure"] += 1
            bucket["total_ms"] += record.duration_ms
        return stats

    @property
    def record_count(self) -> int:
        return len(self._records)
