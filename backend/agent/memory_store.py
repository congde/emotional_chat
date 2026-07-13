"""
MemoryStore — 路径寻址记忆存储

参考 ai-buddy 六层记忆架构实现，适配 emotional_chat 场景。

六层作用域：
  L1 组织级  (organization)  — 全局知识库，系统 prompt 注入，只读
  L2 工作区级 (workspace)     — 跨用户活动日志，不暴露为工具，蒸馏消费
  L3 用户级  (user)          — 长期用户偏好，memory_* 工具可读写
  L4 Agent实例级(agent_instance)— Agent 学习模式，memory_* 工具可读写
  L5 会话级  (session)       — 当次对话工作记忆，memory_* 工具可读写
  L6 当轮级  (turn)          — 对话上下文 window，不存储，虚拟层

核心设计原则：
  - 路径寻址：所有记忆通过 path（如 "preferences/recent_topics"）定位
  - 版本控制：每次写入生成新版本，支持审计链
  - 作用域权限：L3/L4/L5 可通过工具读写，L1/L2 不暴露
  - 幂等写入：相同内容不产生版本变更（sha256 校验）
  - 软删除：删除仅置 content=None，保留审计链
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Tuple

logger = logging.getLogger(__name__)

# ── Scope & Limits ─────────────────────────────────────────────────────────────

Scope = Literal["organization", "workspace", "user", "agent_instance", "session"]

MAX_ENTRY_BYTES = 100 * 1024  # 100 KB 单条上限
MAX_ENTRIES_PER_STORE = 200    # 每 store 条目上限
RECENT_TOPICS_LIMIT = 20      # L3 近期话题保留数量
TOOL_PATTERNS_LIMIT = 30      # L4 工具模式保留数量


# ── MemoryEntry ────────────────────────────────────────────────────────────────

@dataclass
class MemoryEntry:
    """单条记忆条目"""
    id: str
    store_id: str
    path: str
    content: Optional[str] = None  # None = soft-deleted
    content_sha256: Optional[str] = None
    version: int = 1
    updated_at: Optional[float] = None  # Unix timestamp
    metadata: Dict[str, Any] = field(default_factory=dict)


# ── InMemoryStore — 基于内存的轻量存储 ────────────────────────────────────────

class InMemoryStore:
    """
    内存级路径寻址存储，无需外部数据库依赖。
    生产环境可替换为 MongoDB / Redis 实现。
    """

    def __init__(
        self,
        store_id: str,
        scope: Scope,
        target_id: str,
        description: str = "",
    ):
        self._store_id = store_id
        self._scope = scope
        self._target_id = target_id
        self._description = description
        self._entries: Dict[str, MemoryEntry] = {}
        self._counter = 0

    @property
    def store_id(self) -> str:
        return self._store_id

    @property
    def scope(self) -> Scope:
        return self._scope

    @property
    def description(self) -> str:
        return self._description

    def _next_id(self) -> str:
        self._counter += 1
        return f"{self._store_id}_{self._counter:06d}"

    async def write(self, path: str, content: str) -> MemoryEntry:
        """写入（创建或更新）"""
        if len(content.encode()) > MAX_ENTRY_BYTES:
            raise ValueError(f"条目过大: {len(content.encode())} bytes > {MAX_ENTRY_BYTES}")

        sha256 = hashlib.sha256(content.encode()).hexdigest()
        now = time.time()

        existing = self._entries.get(path)
        if existing and existing.content_sha256 == sha256:
            # 幂等：内容没变，不产生版本变更
            return existing

        version = (existing.version + 1) if existing else 1
        entry = MemoryEntry(
            id=existing.id if existing else self._next_id(),
            store_id=self._store_id,
            path=path,
            content=content,
            content_sha256=sha256,
            version=version,
            updated_at=now,
            metadata=existing.metadata if existing else {},
        )
        self._entries[path] = entry
        return entry

    async def read(self, path: str) -> Optional[MemoryEntry]:
        """按路径精确读取"""
        return self._entries.get(path)

    async def edit(self, path: str, old_text: str, new_text: str) -> MemoryEntry:
        """局部编辑：替换首次匹配"""
        entry = self._entries.get(path)
        if entry is None or entry.content is None:
            raise KeyError(f"条目不存在: '{path}'")
        updated = entry.content.replace(old_text, new_text, 1)
        return await self.write(path, updated)

    async def delete(self, path: str) -> None:
        """软删除：保留审计链"""
        entry = self._entries.get(path)
        if entry is None:
            return  # 幂等
        entry.content = None
        entry.content_sha256 = None
        entry.version += 1
        entry.updated_at = time.time()

    async def list_entries(self, path_prefix: str = "") -> List[MemoryEntry]:
        """列出所有条目（可按前缀过滤）"""
        results = []
        for path, entry in self._entries.items():
            if entry.content is not None:  # 排除已软删除
                if not path_prefix or path.startswith(path_prefix):
                    results.append(entry)
        return sorted(results, key=lambda e: e.path)

    async def search(self, query: str) -> List[MemoryEntry]:
        """搜索：路径 + 内容子串匹配"""
        q = query.lower()
        results = []
        for path, entry in self._entries.items():
            if entry.content is None:
                continue
            if q in path.lower() or q in entry.content.lower():
                results.append(entry)
        return sorted(results, key=lambda e: e.updated_at or 0, reverse=True)

    def build_system_prompt_fragment(self) -> str:
        """构建注入到 system prompt 的记忆摘要"""
        if not self._description and not self._entries:
            return ""

        lines = [f"## 记忆存储: {self._store_id}"]
        lines.append(f"作用域: {self._scope} | 目标: {self._target_id}")
        if self._description:
            lines.append(self._description)

        # 列出条目摘要
        active = [e for e in self._entries.values() if e.content is not None]
        if active:
            lines.append("")
            for entry in active[:10]:  # 最多展示 10 条
                preview = (entry.content[:80] + "...") if len(entry.content) > 80 else entry.content
                lines.append(f"- `{entry.path}` (v{entry.version}) — {preview}")

        lines.append("可使用 memory_* 工具读写条目。")
        return "\n".join(lines)
