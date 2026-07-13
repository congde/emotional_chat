"""
Memory Hub — 六层记忆中枢

参考 ai-buddy Phase 6.3 六层记忆架构设计，适配 emotional_chat 情感聊天场景。

六层作用域：
  L1 组织级  (organization)  — 全局知识库（如共情话术库），系统 prompt 注入，只读
  L2 工作区级 (workspace)     — 跨用户活动日志，不暴露为工具，蒸馏管道消费
  L3 用户级  (user)          — 长期用户偏好（兴趣、情绪基线），memory_* 工具可读写
  L4 Agent实例级(agent_instance)— Agent 学习模式（情绪响应策略），memory_* 工具可读写
  L5 会话级  (session)       — 当次对话工作记忆（当前话题、用户状态），memory_* 工具可读写
  L6 当轮级  (turn)          — 对话上下文 window，不存储，虚拟层

工具可寻址层：仅 L3 / L4 / L5。L1/L2 不通过工具暴露；L6 是 LLM context 本身。

核心设计原则：
  - 路径寻址：所有记忆通过 path 定位（如 "preferences/recent_topics"）
  - 后台蒸馏：每轮结束后将 L2 活动日志浓缩到 L3/L4，无 LLM 调用，幂等
  - 系统 Prompt 自动注入：L3/L4/L5 摘要自动注入每轮 system prompt
  - 门控开关：全部功能通过 ModuleToggles 门控，默认关闭，可逐层灰度
"""

from __future__ import annotations

import logging
import threading
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from backend.agent.memory_store import (
    InMemoryStore,
    MemoryEntry,
    Scope,
    MAX_ENTRIES_PER_STORE,
)
from backend.agent.activity_distiller import (
    TurnDigest,
    distill_turn,
    PREFS_TOPICS_PATH,
    PREFS_EMOTION_PATH,
    PATTERNS_EMOTION_RESPONSE_PATH,
)

# 惰性导入：MemoryManager 依赖 chromadb，数据库依赖 SQLAlchemy，允许缺失
try:
    from backend.memory_manager import MemoryManager
except ImportError:
    MemoryManager = None  # type: ignore

try:
    from backend.database import get_db, User, ChatSession, ChatMessage
except ImportError:
    get_db = None  # type: ignore
    User = None  # type: ignore
    ChatSession = None  # type: ignore
    ChatMessage = None  # type: ignore

logger = logging.getLogger(__name__)


# ── ModuleToggles 门控 ────────────────────────────────────────────────────────

class ModuleToggles:
    """记忆系统功能开关，默认关闭，可逐层灰度开启"""

    def __init__(self):
        self.memory_tool_exposure: bool = False       # 向 Agent 暴露 memory_* 工具
        self.memory_prompt_injection: bool = False     # L3/L4/L5 摘要注入 system prompt
        self.activity_distillation: bool = False       # 后台 L2→L3/L4 蒸馏
        self.vector_search: bool = True                # 向量语义检索（已有功能）

    def is_enabled(self, name: str) -> bool:
        return getattr(self, name, False)


# ── MemoryHub ─────────────────────────────────────────────────────────────────

class MemoryHub:
    """
    六层记忆中枢 — Agent 的记忆系统核心。

    职责：
      1. 管理六个作用域的 MemoryStore 实例
      2. 提供 6 个 memory_* 工具接口（L3/L4/L5 可寻址）
      3. 协调短期记忆（L5/L6）与长期记忆（L3）的联动
      4. 每轮结束后触发蒸馏管道（L2→L3/L4）
      5. 构建 system prompt 记忆摘要片段

    使用方式：
      hub = MemoryHub(user_id="user_123", session_id="sess_456")
      await hub.initialize()

      # 每轮对话前
      memory_prompt = hub.build_memory_prompt("今天心情不太好")

      # 每轮对话后
      await hub.on_turn_end(query="今天心情不太好", emotion="sad", intensity=7.0)
    """

    # 稳定路径常量
    PATH_CURRENT_TASK = "context/current_task"
    PATH_USER_STATE = "context/user_state"
    PATH_SESSION_SUMMARY = "context/session_summary"

    def __init__(
        self,
        user_id: str = "",
        session_id: str = "",
        agent_type: str = "xinyu",
        memory_manager: Optional[MemoryManager] = None,
        toggles: Optional[ModuleToggles] = None,
    ):
        self._user_id = user_id
        self._session_id = session_id
        self._agent_type = agent_type
        self._memory_manager = memory_manager  # 保留向量检索能力
        self._toggles = toggles or ModuleToggles()

        # 六层 Store 实例（惰性初始化）
        self._stores: Dict[str, InMemoryStore] = {}

        # L6 当轮上下文（虚拟层，不持久化）
        self._turn_context: Dict[str, Any] = {}

        # L2 活动日志缓冲（本轮累积，蒸馏后清空）
        self._activity_log: List[Dict[str, Any]] = []

        self._persistent_loaded = False

        # Store creation is intentionally synchronous so legacy Agent constructors
        # never receive a coroutine in place of a MemoryHub.
        self._initialize_stores()

    def _initialize_stores(self) -> None:
        """Create scope stores once without performing database I/O."""
        if self._stores:
            return

        # L1 组织级 — 全局知识库，只读
        self._stores["organization"] = InMemoryStore(
            store_id=f"org_{self._agent_type}",
            scope="organization",
            target_id=self._agent_type,
            description="组织级知识库：共情话术库、安全规范等",
        )

        # L2 工作区级 — 活动日志，不暴露
        self._stores["workspace"] = InMemoryStore(
            store_id=f"ws_default",
            scope="workspace",
            target_id="default",
            description="工作区级活动日志",
        )

        # L3 用户级 — 长期偏好
        if self._user_id:
            self._stores["user"] = InMemoryStore(
                store_id=f"user_{self._user_id}",
                scope="user",
                target_id=self._user_id,
                description="用户级记忆：偏好、兴趣、情绪基线",
            )

        # L4 Agent 实例级 — Agent 学习模式
        self._stores["agent_instance"] = InMemoryStore(
            store_id=f"agent_{self._agent_type}_{self._user_id}",
            scope="agent_instance",
            target_id=self._agent_type,
            description="Agent 实例级记忆：情绪响应策略、交互模式",
        )

        # L5 会话级 — 当次对话工作记忆
        if self._session_id:
            self._stores["session"] = InMemoryStore(
                store_id=f"session_{self._session_id}",
                scope="session",
                target_id=self._session_id,
                description="会话级工作记忆：当前话题、用户状态",
            )

        logger.info(
            "MemoryHub initialized: user=%s, session=%s, stores=%s",
            self._user_id[:8], self._session_id[:8], list(self._stores.keys()),
        )

    async def initialize(self) -> None:
        """Load persistent state once; safe to call repeatedly."""
        self._initialize_stores()
        if not self._persistent_loaded:
            await self._load_persistent_data()
            self._persistent_loaded = True

    # ── 六层 Store 访问 ──────────────────────────────────────────────────

    def get_store(self, scope: str) -> Optional[InMemoryStore]:
        """获取指定作用域的 Store"""
        return self._stores.get(scope)

    @property
    def user_store(self) -> Optional[InMemoryStore]:
        """L3 用户级 Store"""
        return self._stores.get("user")

    @property
    def agent_store(self) -> Optional[InMemoryStore]:
        """L4 Agent 实例级 Store"""
        return self._stores.get("agent_instance")

    @property
    def session_store(self) -> Optional[InMemoryStore]:
        """L5 会话级 Store"""
        return self._stores.get("session")

    @property
    def organization_store(self) -> Optional[InMemoryStore]:
        """L1 组织级 Store（只读）"""
        return self._stores.get("organization")

    # ── 记忆工具接口（LLM 可见，6 个 memory_* 工具） ─────────────────────

    def get_tool_schemas(self) -> List[dict]:
        """返回 6 个 memory_* 工具的 schema（用于 LLM function calling）"""
        if not self._toggles.is_enabled("memory_tool_exposure"):
            return []

        schemas = []
        # L3/L4/L5 各自注册一套工具
        for scope_name in ["user", "agent_instance", "session"]:
            store = self._stores.get(scope_name)
            if store is None:
                continue
            scope_label = {"user": "L3用户", "agent_instance": "L4Agent", "session": "L5会话"}

            schemas.extend([
                {
                    "name": "memory_list",
                    "description": f"列出{scope_label[scope_name]}记忆中的所有条目",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "scope": {"type": "string", "enum": [scope_name]},
                            "path_prefix": {"type": "string", "description": "路径前缀过滤"},
                        },
                        "required": ["scope"],
                    },
                },
                {
                    "name": "memory_search",
                    "description": f"在{scope_label[scope_name]}记忆中搜索关键词",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "scope": {"type": "string", "enum": [scope_name]},
                            "query": {"type": "string", "description": "搜索关键词"},
                        },
                        "required": ["scope", "query"],
                    },
                },
                {
                    "name": "memory_read",
                    "description": f"读取{scope_label[scope_name]}记忆中的指定条目",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "scope": {"type": "string", "enum": [scope_name]},
                            "path": {"type": "string", "description": "条目路径"},
                        },
                        "required": ["scope", "path"],
                    },
                },
                {
                    "name": "memory_write",
                    "description": f"写入{scope_label[scope_name]}记忆（创建或更新）",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "scope": {"type": "string", "enum": [scope_name]},
                            "path": {"type": "string", "description": "条目路径"},
                            "content": {"type": "string", "description": "条目内容"},
                        },
                        "required": ["scope", "path", "content"],
                    },
                },
                {
                    "name": "memory_edit",
                    "description": f"局部编辑{scope_label[scope_name]}记忆（替换首次匹配）",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "scope": {"type": "string", "enum": [scope_name]},
                            "path": {"type": "string", "description": "条目路径"},
                            "old_text": {"type": "string", "description": "要替换的旧文本"},
                            "new_text": {"type": "string", "description": "替换后的新文本"},
                        },
                        "required": ["scope", "path", "old_text", "new_text"],
                    },
                },
                {
                    "name": "memory_delete",
                    "description": f"删除{scope_label[scope_name]}记忆中的条目（软删除）",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "scope": {"type": "string", "enum": [scope_name]},
                            "path": {"type": "string", "description": "条目路径"},
                        },
                        "required": ["scope", "path"],
                    },
                },
            ])
        return schemas

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行 memory_* 工具调用"""
        scope = arguments.get("scope", "")

        # L1/L2 不可通过工具寻址
        if scope in ("organization", "workspace"):
            return {"success": False, "error": f"scope '{scope}' 不可通过工具操作"}

        store = self._stores.get(scope)
        if store is None:
            return {"success": False, "error": f"scope '{scope}' 对应的 store 不存在"}

        try:
            if tool_name == "memory_list":
                entries = await store.list_entries(arguments.get("path_prefix", ""))
                return {
                    "success": True,
                    "entries": [
                        {"path": e.path, "version": e.version, "preview": (e.content or "")[:100]}
                        for e in entries
                    ],
                }

            elif tool_name == "memory_search":
                entries = await store.search(arguments["query"])
                return {
                    "success": True,
                    "results": [
                        {"path": e.path, "version": e.version, "preview": (e.content or "")[:100]}
                        for e in entries[:10]
                    ],
                }

            elif tool_name == "memory_read":
                entry = await store.read(arguments["path"])
                if entry is None or entry.content is None:
                    return {"success": False, "error": f"条目不存在: {arguments['path']}"}
                return {
                    "success": True,
                    "path": entry.path,
                    "content": entry.content,
                    "version": entry.version,
                }

            elif tool_name == "memory_write":
                entry = await store.write(arguments["path"], arguments["content"])
                # 同时写入向量存储（如果可用）
                await self._sync_to_vector_store(arguments["path"], arguments["content"])
                return {"success": True, "path": entry.path, "version": entry.version}

            elif tool_name == "memory_edit":
                entry = await store.edit(
                    arguments["path"], arguments["old_text"], arguments["new_text"]
                )
                return {"success": True, "path": entry.path, "version": entry.version}

            elif tool_name == "memory_delete":
                await store.delete(arguments["path"])
                return {"success": True, "path": arguments["path"]}

            else:
                return {"success": False, "error": f"未知工具: {tool_name}"}

        except Exception as e:
            logger.warning("memory tool error: %s — %s", tool_name, e)
            return {"success": False, "error": str(e)}

    # ── 短期记忆管理（L5/L6） ───────────────────────────────────────────

    async def update_session_context(
        self,
        current_task: Optional[str] = None,
        user_state: Optional[Dict[str, Any]] = None,
        session_summary: Optional[str] = None,
    ) -> None:
        """更新 L5 会话级工作记忆"""
        store = self.session_store
        if store is None:
            return

        if current_task is not None:
            await store.write(self.PATH_CURRENT_TASK, current_task)
        if user_state is not None:
            import json
            await store.write(self.PATH_USER_STATE, json.dumps(user_state, ensure_ascii=False))
        if session_summary is not None:
            await store.write(self.PATH_SESSION_SUMMARY, session_summary)

    async def get_session_context(self) -> Dict[str, Any]:
        """读取 L5 会话上下文"""
        store = self.session_store
        if store is None:
            return {}

        result = {}
        for path, key in [
            (self.PATH_CURRENT_TASK, "current_task"),
            (self.PATH_USER_STATE, "user_state"),
            (self.PATH_SESSION_SUMMARY, "session_summary"),
        ]:
            entry = await store.read(path)
            if entry and entry.content:
                if key == "user_state":
                    try:
                        import json
                        result[key] = json.loads(entry.content)
                    except json.JSONDecodeError:
                        result[key] = entry.content
                else:
                    result[key] = entry.content
        return result

    def set_turn_context(self, **kwargs) -> None:
        """更新 L6 当轮上下文（虚拟层，不持久化）"""
        self._turn_context.update(kwargs)

    def get_turn_context(self) -> Dict[str, Any]:
        """获取 L6 当轮上下文"""
        return self._turn_context.copy()

    def clear_turn_context(self) -> None:
        """清空 L6 当轮上下文"""
        self._turn_context = {}

    # ── 语义检索（兼容已有 VectorStore） ─────────────────────────────────

    async def semantic_search(
        self,
        query: str,
        top_k: int = 5,
        min_importance: float = 0.3,
    ) -> List[Dict[str, Any]]:
        """向量语义检索（使用已有的 MemoryManager 向量能力）"""
        if not self._memory_manager or not self._toggles.vector_search:
            return []

        try:
            return self._memory_manager.retrieve_memories(
                user_id=self._user_id,
                query=query,
                n_results=top_k,
                min_importance=min_importance,
            )
        except Exception as e:
            logger.warning("语义检索失败: %s", e)
            return []

    # ── 蒸馏管道（每轮结束后调用） ──────────────────────────────────────

    async def on_turn_end(
        self,
        query: str,
        emotion: str = "neutral",
        emotion_intensity: float = 5.0,
        bot_empathy_score: float = 0.0,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        final_status: str = "success",
    ) -> Dict[str, bool]:
        """每轮对话结束后调用：触发蒸馏管道。

        Args:
            query: 用户消息
            emotion: 情绪标签
            emotion_intensity: 情绪强度 (0-10)
            bot_empathy_score: 共情评分 (0-1)
            tool_calls: 本轮工具调用记录
            final_status: 本轮状态

        Returns:
            蒸馏更新结果
        """
        if not self._toggles.is_enabled("activity_distillation"):
            return {"topics_updated": False, "emotion_baseline_updated": False, "patterns_updated": False}

        digest = TurnDigest(
            session_id=self._session_id,
            user_id=self._user_id,
            query=query,
            timestamp=time.time(),
            emotion=emotion,
            emotion_intensity=emotion_intensity,
            bot_empathy_score=bot_empathy_score,
            tool_calls=tool_calls or [],
            final_status=final_status,
        )

        # 记录到 L2 活动日志
        self._activity_log.append({
            "query": query,
            "emotion": emotion,
            "intensity": emotion_intensity,
            "timestamp": digest.timestamp,
        })

        result = await distill_turn(
            digest,
            user_store=self.user_store,
            agent_instance_store=self.agent_store,
        )

        # 清空 L6 当轮上下文
        self.clear_turn_context()

        return result

    # ── 系统 Prompt 注入 ────────────────────────────────────────────────

    def build_memory_prompt(self, query: str = "") -> str:
        """构建注入到 system prompt 的记忆摘要。

        优先级：
          1. L3 用户偏好（recent_topics + emotion_baseline）
          2. L4 Agent 模式（emotion_response）
          3. L5 会话上下文（current_task + user_state）
          4. 向量语义检索结果（对 query 最相关的记忆）

        Agent 在第一轮就能感知历史记忆，无需主动发起 memory_list。
        """
        if not self._toggles.is_enabled("memory_prompt_injection"):
            return ""

        parts: List[str] = ["## 记忆上下文"]

        # L3 用户偏好
        user_store = self.user_store
        if user_store:
            fragment = user_store.build_system_prompt_fragment()
            if fragment:
                parts.append(fragment)

        # L4 Agent 模式
        agent_store = self.agent_store
        if agent_store:
            fragment = agent_store.build_system_prompt_fragment()
            if fragment:
                parts.append(fragment)

        # L5 会话上下文
        session_store = self.session_store
        if session_store:
            fragment = session_store.build_system_prompt_fragment()
            if fragment:
                parts.append(fragment)

        return "\n\n".join(parts) if len(parts) > 1 else ""

    # ── 用户画像（兼容旧接口） ──────────────────────────────────────────

    async def get_user_profile(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """获取用户画像，综合 L3 记忆 + 数据库数据"""
        uid = user_id or self._user_id
        if not uid:
            return {}

        profile: Dict[str, Any] = {"user_id": uid}

        # 从 L3 Store 读取偏好
        user_store = self.user_store
        if user_store:
            # 话题偏好
            topics_entry = await user_store.read(PREFS_TOPICS_PATH)
            if topics_entry and topics_entry.content:
                try:
                    import json
                    profile["recent_topics"] = json.loads(topics_entry.content)
                except json.JSONDecodeError:
                    pass

            # 情绪基线
            emotion_entry = await user_store.read(PREFS_EMOTION_PATH)
            if emotion_entry and emotion_entry.content:
                try:
                    import json
                    profile["emotion_baseline"] = json.loads(emotion_entry.content)
                except json.JSONDecodeError:
                    pass

        # 从数据库补充基本信息
        try:
            if get_db is not None and User is not None:
                db = next(get_db())
                user = db.query(User).filter(User.user_id == uid).first()
                if user:
                    profile["username"] = user.username
                    profile["created_at"] = user.created_at.isoformat() if user.created_at else None
        except Exception as e:
            logger.warning("数据库查询用户画像失败: %s", e)

        return profile

    # ── 行为日志（兼容旧接口） ──────────────────────────────────────────

    async def get_action_log(
        self,
        user_id: Optional[str] = None,
        days: int = 7,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """获取用户行为日志"""
        uid = user_id or self._user_id
        if not uid:
            return []

        try:
            if get_db is None or ChatMessage is None:
                return []
            db_generator = get_db()
            db = next(db_generator)
            from datetime import datetime, timedelta
            since_date = datetime.now() - timedelta(days=days)

            messages = db.query(ChatMessage).filter(
                ChatMessage.user_id == uid,
                ChatMessage.created_at >= since_date,
            ).order_by(ChatMessage.created_at.desc()).limit(limit).all()

            return [
                {
                    "action": "message",
                    "content": msg.content[:100] if msg.content else "",
                    "role": msg.role,
                    "emotion": msg.emotion,
                    "timestamp": msg.created_at.isoformat() if msg.created_at else None,
                }
                for msg in messages
            ]
        except Exception as e:
            logger.warning("获取行为日志失败: %s", e)
            return []

    # ── 兼容旧接口 ────────────────────────────────────────────────────

    def encode(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """兼容旧接口：编码记忆。

        旧代码调用 memory_hub.encode({...})，现在映射到语义检索 + L3 写入。
        """
        content = data.get("content", "")
        emotion = data.get("emotion", {})
        user_id = data.get("user_id", self._user_id)
        role = data.get("role", "user")

        # 简化处理：直接返回结构化记忆
        emotion_label = emotion.get("emotion", "neutral") if isinstance(emotion, dict) else str(emotion)
        intensity = emotion.get("intensity", 5.0) if isinstance(emotion, dict) else 5.0

        importance = min(1.0, intensity / 10.0)

        return {
            "memory_type": "episodic",
            "content": content,
            "emotion": emotion,
            "importance": importance,
            "user_id": user_id,
            "role": role,
        }

    def retrieve(
        self,
        query: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """兼容旧接口：检索记忆（同步版本，优先使用 semantic_search）"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果已在 async 上下文中，无法直接 await
                # 回退到 InMemoryStore 的同步搜索
                results = []
                for scope_name in ["user", "agent_instance", "session"]:
                    store = self._stores.get(scope_name)
                    if store:
                        try:
                            entries = asyncio.ensure_future(store.search(query))
                        except RuntimeError:
                            continue
                return results[:top_k]
            else:
                return loop.run_until_complete(self.semantic_search(query, top_k))
        except RuntimeError:
            # 没有事件循环，使用 InMemoryStore 同步搜索
            results = []
            for scope_name in ["user", "agent_instance", "session"]:
                store = self._stores.get(scope_name)
                if store:
                    for path, entry in store._entries.items():
                        if entry.content and query.lower() in entry.content.lower():
                            results.append({
                                "content": entry.content,
                                "emotion": {},
                                "timestamp": entry.updated_at,
                                "importance": 0.5,
                                "path": entry.path,
                            })
            return results[:top_k]

    def get_working_memory(self) -> Dict[str, Any]:
        """兼容旧接口：获取工作记忆"""
        result: Dict[str, Any] = {
            "conversation": [],
            "active_tasks": [],
            "current_context": self._turn_context,
        }

        # 尝试从 L5 读取当前任务
        session_store = self.session_store
        if session_store:
            entry = session_store._entries.get(self.PATH_CURRENT_TASK)
            if entry and entry.content:
                result["active_tasks"].append(entry.content)

        return result

    # ── 内部辅助方法 ────────────────────────────────────────────────────

    async def _load_persistent_data(self) -> None:
        """从数据库加载已有记忆数据到 L3/L4 Store"""
        if not self._user_id:
            return

        try:
            if get_db is None or ChatMessage is None:
                return
            # 从数据库加载最近消息，重建 L3 偏好
            db = next(get_db())
            from datetime import datetime, timedelta

            since = datetime.now() - timedelta(days=30)
            messages = db.query(ChatMessage).filter(
                ChatMessage.user_id == self._user_id,
                ChatMessage.created_at >= since,
            ).order_by(ChatMessage.created_at.desc()).limit(100).all()

            if messages and self.user_store:
                # 重建话题偏好
                import json
                topics = []
                seen = set()
                for msg in messages:
                    if msg.content and msg.role == "user":
                        topic = msg.content[:50]
                        if topic not in seen:
                            seen.add(topic)
                            topics.append({
                                "topic": topic,
                                "freq": 1,
                                "last_seen": msg.created_at.timestamp() if msg.created_at else time.time(),
                            })
                if topics:
                    await self.user_store.write(
                        PREFS_TOPICS_PATH,
                        json.dumps(topics[:20], ensure_ascii=False, sort_keys=True, separators=(",", ":")),
                    )

                # 重建情绪基线
                emotion_counts = {}
                for msg in messages:
                    if msg.emotion:
                        emotion_counts[msg.emotion] = emotion_counts.get(msg.emotion, 0) + 1
                if emotion_counts:
                    dominant = max(emotion_counts.items(), key=lambda x: x[1])[0]
                    baseline = {
                        "dominant_emotion": dominant,
                        "avg_intensity": 5.0,
                        "distribution": emotion_counts,
                    }
                    await self.user_store.write(
                        PREFS_EMOTION_PATH,
                        json.dumps(baseline, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
                    )

        except Exception as e:
            logger.warning("加载持久化记忆数据失败: %s", e)
        finally:
            if "db_generator" in locals():
                db_generator.close()

    async def _sync_to_vector_store(self, path: str, content: str) -> None:
        """同步写入到向量数据库（用于语义检索）"""
        if MemoryManager is None or not self._memory_manager:
            return

        try:
            self._memory_manager.store_memory(
                user_id=self._user_id,
                session_id=self._session_id,
                memory={
                    "content": content,
                    "summary": content[:100],
                    "type": "knowledge",
                    "importance": 0.5,
                    "timestamp": datetime.now().isoformat(),
                },
            )
        except Exception as e:
            logger.warning("同步到向量存储失败: %s", e)


# ── 隔离注册表 ───────────────────────────────────────────────────────────────

_memory_hub_registry: Dict[Tuple[str, str, str], MemoryHub] = {}
_memory_hub_registry_lock = threading.RLock()


def get_memory_hub(
    user_id: str = "",
    session_id: str = "",
    agent_type: str = "xinyu",
) -> MemoryHub:
    """Return a MemoryHub isolated by user, session, and agent type.

    This function is synchronous for compatibility with Agent constructors.
    Call ``await hub.initialize()`` where persistent state must be loaded before
    the first turn.
    """
    key = (user_id or "", session_id or "", agent_type or "xinyu")
    with _memory_hub_registry_lock:
        hub = _memory_hub_registry.get(key)
        if hub is None:
            hub = MemoryHub(
                user_id=key[0],
                session_id=key[1],
                agent_type=key[2],
            )
            _memory_hub_registry[key] = hub
        return hub


async def get_memory_hub_async(
    user_id: str = "",
    session_id: str = "",
    agent_type: str = "xinyu",
) -> MemoryHub:
    """Return an isolated hub after loading its persistent state."""
    hub = get_memory_hub(user_id, session_id, agent_type)
    await hub.initialize()
    return hub


def reset_memory_hub(
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    agent_type: Optional[str] = None,
) -> None:
    """Reset matching hubs, or the complete registry when no filter is given."""
    with _memory_hub_registry_lock:
        if user_id is None and session_id is None and agent_type is None:
            _memory_hub_registry.clear()
            return

        keys = [
            key for key in _memory_hub_registry
            if (user_id is None or key[0] == user_id)
            and (session_id is None or key[1] == session_id)
            and (agent_type is None or key[2] == agent_type)
        ]
        for key in keys:
            _memory_hub_registry.pop(key, None)
