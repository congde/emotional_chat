"""
Activity Distiller — 活动蒸馏管道

参考 ai-buddy Phase 6.3 设计，适配 emotional_chat 场景。

后台蒸馏管道：每轮对话结束后，将 L2 活动日志浓缩到 L3 用户偏好 + L4 Agent 模式。
  - 不调用 LLM，纯聚合计算
  - 幂等：相同输入 → 相同 content_sha256
  - 失败静默：任何错误仅 log，不影响主流程

蒸馏输出（两条稳定路径）：
  L3 user store:
      path = "preferences/recent_topics"
      content = JSON [{topic, freq, last_seen}, ...]

      path = "preferences/emotion_baseline"
      content = JSON {dominant_emotion, avg_intensity, distribution}

  L4 agent_instance store:
      path = "patterns/emotion_response"
      content = JSON {emotion: {count, avg_score, last_seen}}
"""

from __future__ import annotations

import json
import logging
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ── 常量 ──────────────────────────────────────────────────────────────────────

RECENT_TOPICS_LIMIT = 20
EMOTION_PATTERNS_LIMIT = 30

PREFS_TOPICS_PATH = "preferences/recent_topics"
PREFS_EMOTION_PATH = "preferences/emotion_baseline"
PATTERNS_EMOTION_RESPONSE_PATH = "patterns/emotion_response"


# ── TurnDigest ────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class TurnDigest:
    """一轮对话的蒸馏输入数据"""
    session_id: str
    user_id: str
    query: str                     # 用户消息
    timestamp: float               # Unix timestamp
    emotion: str = "neutral"       # 用户情绪标签
    emotion_intensity: float = 5.0 # 情绪强度 (0-10)
    bot_empathy_score: float = 0.0 # 共情评分 (0-1, 可选)
    tool_calls: List[Dict[str, Any]] = ()  # [{name, success}]
    final_status: str = "success"  # success / failed / timeout


# ── 聚合函数（纯函数，无副作用） ──────────────────────────────────────────────

def _extract_topic(query: str) -> str:
    """启发式话题提取 — 取前50字符，规范化空白"""
    if not query:
        return ""
    cleaned = " ".join(query.split())
    return cleaned[:50]


def merge_recent_topics(prior_json: Optional[str], digest: TurnDigest) -> str:
    """合并新话题到已有列表，去重并排序。

    Returns: canonical JSON (sort_keys, separators) 保证幂等 sha256。
    """
    items: List[Dict[str, Any]] = []
    if prior_json:
        try:
            parsed = json.loads(prior_json)
            if isinstance(parsed, list):
                items = [x for x in parsed if isinstance(x, dict)]
        except (json.JSONDecodeError, TypeError):
            items = []

    topic = _extract_topic(digest.query)
    if not topic:
        return prior_json or ""

    # 已存在则更新频率和最后时间，否则插入
    found = False
    for entry in items:
        if entry.get("topic") == topic:
            entry["freq"] = int(entry.get("freq", 0)) + 1
            entry["last_seen"] = digest.timestamp
            found = True
            break
    if not found:
        items.insert(0, {
            "topic": topic,
            "freq": 1,
            "last_seen": digest.timestamp,
        })

    # 按最后出现时间降序，保留上限
    items.sort(key=lambda x: x.get("last_seen", 0), reverse=True)
    items = items[:RECENT_TOPICS_LIMIT]

    return json.dumps(items, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def merge_emotion_baseline(prior_json: Optional[str], digest: TurnDigest) -> str:
    """合并情绪基线数据"""
    distribution: Dict[str, int] = {}
    intensities: Dict[str, List[float]] = {}
    total_intensity = 0.0
    count = 0

    # 先恢复已有数据
    if prior_json:
        try:
            parsed = json.loads(prior_json)
            if isinstance(parsed, dict):
                distribution = parsed.get("distribution", {})
                # 重建 intensities 用 avg
                for emo, cnt in distribution.items():
                    avg_i = parsed.get("intensity_avg", {}).get(emo, 5.0)
                    intensities[emo] = [avg_i] * cnt
                    total_intensity += avg_i * cnt
                    count += cnt
        except (json.JSONDecodeError, TypeError):
            pass

    # 合并本轮
    if digest.emotion:
        distribution[digest.emotion] = distribution.get(digest.emotion, 0) + 1
        if digest.emotion not in intensities:
            intensities[digest.emotion] = []
        intensities[digest.emotion].append(digest.emotion_intensity)
        total_intensity += digest.emotion_intensity
        count += 1

    # 计算统计
    intensity_avg = {}
    for emo, iv_list in intensities.items():
        intensity_avg[emo] = round(sum(iv_list) / len(iv_list), 2) if iv_list else 0

    dominant = max(distribution.items(), key=lambda x: x[1])[0] if distribution else "neutral"
    avg_intensity = round(total_intensity / count, 2) if count else 0

    result = {
        "dominant_emotion": dominant,
        "avg_intensity": avg_intensity,
        "distribution": distribution,
        "intensity_avg": intensity_avg,
    }

    return json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def merge_emotion_response_patterns(prior_json: Optional[str], digest: TurnDigest) -> str:
    """合并情绪响应模式到 L4"""
    patterns: Dict[str, Dict[str, Any]] = {}
    if prior_json:
        try:
            parsed = json.loads(prior_json)
            if isinstance(parsed, dict):
                patterns = {k: v for k, v in parsed.items() if isinstance(v, dict)}
        except (json.JSONDecodeError, TypeError):
            patterns = {}

    # 按情绪归类响应
    emotion_key = digest.emotion or "neutral"
    bucket = patterns.setdefault(emotion_key, {
        "count": 0, "avg_score": 0, "total_score": 0.0, "last_seen": 0
    })
    bucket["count"] = int(bucket.get("count", 0)) + 1
    bucket["total_score"] = float(bucket.get("total_score", 0)) + digest.bot_empathy_score
    bucket["avg_score"] = round(bucket["total_score"] / bucket["count"], 3)
    bucket["last_seen"] = digest.timestamp

    # 限制数量
    if len(patterns) > EMOTION_PATTERNS_LIMIT:
        kept = sorted(
            patterns.items(),
            key=lambda kv: kv[1].get("last_seen", 0),
            reverse=True,
        )[:EMOTION_PATTERNS_LIMIT]
        patterns = dict(kept)

    return json.dumps(patterns, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


# ── 公共入口 ──────────────────────────────────────────────────────────────────

async def distill_turn(
    digest: TurnDigest,
    *,
    user_store: Optional[Any] = None,
    agent_instance_store: Optional[Any] = None,
) -> Dict[str, bool]:
    """蒸馏一轮对话到 L3/L4 store。

    Args:
        digest: TurnDigest 数据
        user_store: L3 MemoryStore（用户作用域）
        agent_instance_store: L4 MemoryStore（Agent 实例作用域）

    Returns:
        {"topics_updated": bool, "emotion_baseline_updated": bool, "patterns_updated": bool}
    """
    result = {
        "topics_updated": False,
        "emotion_baseline_updated": False,
        "patterns_updated": False,
    }

    # ── L3: 用户偏好 ────────────────────────────────────────────────────
    if user_store is not None:
        # 话题偏好
        try:
            existing = await user_store.read(PREFS_TOPICS_PATH)
            prior = existing.content if existing else None
            new_content = merge_recent_topics(prior, digest)
            if new_content and new_content != (prior or ""):
                await user_store.write(PREFS_TOPICS_PATH, new_content)
                result["topics_updated"] = True
        except Exception as exc:
            logger.warning("distill_turn(L3 topics) failed: %s", exc)

        # 情绪基线
        try:
            existing = await user_store.read(PREFS_EMOTION_PATH)
            prior = existing.content if existing else None
            new_content = merge_emotion_baseline(prior, digest)
            if new_content and new_content != (prior or ""):
                await user_store.write(PREFS_EMOTION_PATH, new_content)
                result["emotion_baseline_updated"] = True
        except Exception as exc:
            logger.warning("distill_turn(L3 emotion) failed: %s", exc)

    # ── L4: Agent 实例模式 ──────────────────────────────────────────────
    if agent_instance_store is not None:
        try:
            existing = await agent_instance_store.read(PATTERNS_EMOTION_RESPONSE_PATH)
            prior = existing.content if existing else None
            new_content = merge_emotion_response_patterns(prior, digest)
            if new_content and new_content != (prior or ""):
                await agent_instance_store.write(PATTERNS_EMOTION_RESPONSE_PATH, new_content)
                result["patterns_updated"] = True
        except Exception as exc:
            logger.warning("distill_turn(L4 patterns) failed: %s", exc)

    updated = [k for k, v in result.items() if v]
    if updated:
        logger.info(
            "distill_turn: session=%s, user=%s, updated=%s",
            digest.session_id[:8], digest.user_id[:8], updated,
        )
    return result
