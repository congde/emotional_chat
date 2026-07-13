# -*- coding: utf-8 -*-
"""
ActivityDistiller — 活动蒸馏器

将 L2 (workspace) Activity 记录蒸馏为 L3 (user preference) 和
L4 (agent_instance learned-pattern) 记忆条目。

设计规则：
- 确定性: 无 LLM 调用，纯聚合
- 幂等性: 相同输入产生相同 content_sha256
- 有界成本: O(N) over small window
- 失败安全: 任何 DAO 错误记为 WARNING 并静默返回
- 可开关: activity_distillation toggle

输出格式：
  L3 user store: "preferences/recent_topics" → JSON list of {topic, last_seen, freq}
  L4 agent_instance store: "patterns/tool_usage" → JSON dict of {tool_name: {count, success_rate}}
"""

from __future__ import annotations

import json
import logging
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from backend.runtime.config.guards import is_module_enabled

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TurnDigest:
    """一轮对话的蒸馏输入数据"""

    session_id: str
    user_id: str
    workspace_id: str
    query: str
    timestamp: float
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)  # [{name, success}]
    emotion_tag: str = ""
    final_status: str = "success"  # "success" | "failed" | "timeout"


# ── Constants ──

_RECENT_TOPICS_LIMIT = 20
_EMOTION_TRENDS_LIMIT = 10
_TOOL_PATTERNS_LIMIT = 30
_PREFS_PATH = "preferences/recent_topics"
_EMOTION_PATH = "patterns/emotion_trends"
_PATTERNS_PATH = "patterns/tool_usage"


class ActivityDistiller:
    """
    活动蒸馏器 — 后台管道，将活动记录蒸馏为记忆

    Usage::

        distiller = ActivityDistiller()
        result = await distiller.distill_turn(
            digest,
            user_store=user_memory_store,
            agent_instance_store=agent_memory_store,
        )
    """

    async def distill_turn(
        self,
        digest: TurnDigest,
        *,
        user_store: Optional[Any] = None,
        agent_instance_store: Optional[Any] = None,
    ) -> Dict[str, bool]:
        """
        蒸馏一轮对话为 L3/L4 记忆更新

        Args:
            digest: TurnDigest
            user_store: L3 用户偏好存储
            agent_instance_store: L4 Agent 模式存储

        Returns:
            {"topics_updated": bool, "emotions_updated": bool, "patterns_updated": bool}
        """
        if not is_module_enabled("activity_distillation"):
            return {"topics_updated": False, "emotions_updated": False, "patterns_updated": False}

        result = {"topics_updated": False, "emotions_updated": False, "patterns_updated": False}

        try:
            # L3: 更新最近话题
            if user_store:
                prior = await self._read_store(user_store, _PREFS_PATH)
                updated = self._merge_recent_topics(prior, digest)
                if updated != prior:
                    await self._write_store(user_store, _PREFS_PATH, updated)
                    result["topics_updated"] = True

            # L3: 更新情感趋势
            if user_store:
                prior = await self._read_store(user_store, _EMOTION_PATH)
                updated = self._merge_emotion_trends(prior, digest)
                if updated != prior:
                    await self._write_store(user_store, _EMOTION_PATH, updated)
                    result["emotions_updated"] = True

            # L4: 更新工具使用模式
            if agent_instance_store:
                prior = await self._read_store(agent_instance_store, _PATTERNS_PATH)
                updated = self._merge_tool_patterns(prior, digest)
                if updated != prior:
                    await self._write_store(agent_instance_store, _PATTERNS_PATH, updated)
                    result["patterns_updated"] = True

        except Exception as e:
            logger.warning("Activity distillation failed: %s", e)

        return result

    def _merge_recent_topics(self, prior_json: Optional[str], digest: TurnDigest) -> str:
        """合并新话题到现有列表"""
        items: List[Dict[str, Any]] = []
        if prior_json:
            try:
                parsed = json.loads(prior_json)
                if isinstance(parsed, list):
                    items = [x for x in parsed if isinstance(x, dict)]
            except (json.JSONDecodeError, TypeError):
                items = []

        topic = self._extract_topic(digest.query)
        if not topic:
            return prior_json or ""

        found = False
        for entry in items:
            if entry.get("topic") == topic:
                entry["freq"] = int(entry.get("freq", 0)) + 1
                entry["last_seen"] = digest.timestamp
                found = True
                break
        if not found:
            items.insert(0, {"topic": topic, "freq": 1, "last_seen": digest.timestamp})

        items.sort(key=lambda x: x.get("last_seen", 0), reverse=True)
        items = items[:_RECENT_TOPICS_LIMIT]

        return json.dumps(items, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    def _merge_emotion_trends(self, prior_json: Optional[str], digest: TurnDigest) -> str:
        """合并情感趋势"""
        items: List[Dict[str, Any]] = []
        if prior_json:
            try:
                parsed = json.loads(prior_json)
                if isinstance(parsed, list):
                    items = [x for x in parsed if isinstance(x, dict)]
            except (json.JSONDecodeError, TypeError):
                items = []

        if digest.emotion_tag:
            items.insert(0, {
                "emotion": digest.emotion_tag,
                "timestamp": digest.timestamp,
                "session_id": digest.session_id,
            })

        items = items[:_EMOTION_TRENDS_LIMIT]
        return json.dumps(items, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    def _merge_tool_patterns(self, prior_json: Optional[str], digest: TurnDigest) -> str:
        """合并工具使用统计"""
        patterns: Dict[str, Dict[str, Any]] = {}
        if prior_json:
            try:
                parsed = json.loads(prior_json)
                if isinstance(parsed, dict):
                    patterns = {k: v for k, v in parsed.items() if isinstance(v, dict)}
            except (json.JSONDecodeError, TypeError):
                patterns = {}

        for call in digest.tool_calls:
            name = str(call.get("name", "")).strip()
            if not name:
                continue
            bucket = patterns.setdefault(name, {"count": 0, "success": 0, "failure": 0, "last_seen": 0})
            bucket["count"] = int(bucket.get("count", 0)) + 1
            if call.get("success", True):
                bucket["success"] = int(bucket.get("success", 0)) + 1
            else:
                bucket["failure"] = int(bucket.get("failure", 0)) + 1
            bucket["last_seen"] = digest.timestamp

        for name, bucket in patterns.items():
            total = bucket.get("count", 0) or 1
            bucket["success_rate"] = round(bucket.get("success", 0) / total, 3)

        if len(patterns) > _TOOL_PATTERNS_LIMIT:
            kept = sorted(patterns.items(), key=lambda kv: kv[1].get("last_seen", 0), reverse=True)[
                :_TOOL_PATTERNS_LIMIT
            ]
            patterns = dict(kept)

        return json.dumps(patterns, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    def _extract_topic(self, query: str) -> str:
        """提取话题（前50字符）"""
        if not query:
            return ""
        cleaned = " ".join(query.split())
        return cleaned[:50]

    async def _read_store(self, store: Any, path: str) -> Optional[str]:
        """从存储读取"""
        try:
            if hasattr(store, "read"):
                return await store.read(path) if asyncio.iscoroutinefunction(store.read) else store.read(path)
            if hasattr(store, "get"):
                return store.get(path)
        except Exception as e:
            logger.debug("Store read failed for '%s': %s", path, e)
        return None

    async def _write_store(self, store: Any, path: str, content: str) -> None:
        """写入存储"""
        try:
            if hasattr(store, "write"):
                if asyncio.iscoroutinefunction(store.write):
                    await store.write(path, content)
                else:
                    store.write(path, content)
            elif hasattr(store, "set"):
                store.set(path, content)
        except Exception as e:
            logger.warning("Store write failed for '%s': %s", path, e)


import asyncio  # noqa: E402 — needed for iscoroutinefunction check
