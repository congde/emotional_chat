# -*- coding: utf-8 -*-
"""
WorkspaceManager — 文件系统隔离管理

每个用户绑定一个独立的工作区目录，
所有文件操作、缓存、日志都限定在该目录内。
防止多用户/多会话之间的数据竞争。

Directory layout per workspace:
  {workspace_root}/
  ├── .runtime/           ← Session JSONL journals, temp files
  ├── sessions/           ← Session state files
  ├── memories/           ← Memory store files
  └── workspace/          ← Working directory for file operations
"""

from __future__ import annotations

import logging
import os
import threading
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Set

logger = logging.getLogger(__name__)


def _resolve_default_base() -> Path:
    """解析默认基础目录"""
    val = os.environ.get("EMOTIONAL_CHAT_WORKSPACE_BASE")
    if val:
        return Path(val)
    return Path.home() / ".emotional_chat"


@dataclass
class WorkspaceInfo:
    """工作区元数据"""

    workspace_id: str
    root: Path
    owner_id: str  # user_id or session_id
    name: Optional[str] = None
    state: str = "idle"
    created_at: Optional[str] = None


class WorkspaceManager:
    """
    工作区生命周期管理 — 创建、解析、清理隔离工作区

    Usage::

        mgr = WorkspaceManager()
        ws = mgr.create_workspace(user_id="user_123")
        # ws.root = Path("/home/user/.emotional_chat/users/user_123")
    """

    def __init__(self, base_dir: Optional[Path] = None):
        self._base = base_dir or _resolve_default_base()
        self._workspaces: Dict[str, WorkspaceInfo] = {}
        self._lock = threading.Lock()

    def create_workspace(
        self,
        user_id: str,
        workspace_id: Optional[str] = None,
        name: Optional[str] = None,
    ) -> WorkspaceInfo:
        """创建隔离工作区"""
        import uuid

        ws_id = workspace_id or f"ws_{uuid.uuid4().hex[:8]}"
        root = self._base / "users" / user_id

        self._ensure_dirs(root)

        info = WorkspaceInfo(
            workspace_id=ws_id,
            root=root,
            owner_id=user_id,
            name=name or ws_id,
            created_at=datetime.utcnow().isoformat(),
        )
        self._workspaces[ws_id] = info
        logger.info("Created workspace %s at %s", ws_id, root)
        return info

    def resolve_workspace(self, user_id: str) -> Path:
        """解析工作区根路径"""
        return self._base / "users" / user_id

    def get_workspace(self, workspace_id: str) -> Optional[WorkspaceInfo]:
        """获取工作区信息"""
        return self._workspaces.get(workspace_id)

    def cleanup_workspace(self, workspace_id: str) -> None:
        """清理工作区"""
        info = self._workspaces.pop(workspace_id, None)
        if info and info.root.exists():
            import shutil
            shutil.rmtree(info.root, ignore_errors=True)
            logger.info("Cleaned up workspace %s", workspace_id)

    def _ensure_dirs(self, root: Path) -> None:
        """确保目录结构存在"""
        for subdir in [".runtime", "sessions", "memories", "workspace"]:
            (root / subdir).mkdir(parents=True, exist_ok=True)
