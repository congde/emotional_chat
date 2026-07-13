# -*- coding: utf-8 -*-
"""
Workspace — 工作区隔离管理

每个用户/会话有独立的工作区，防止数据竞争。
"""

from backend.runtime.workspace.manager import WorkspaceManager, WorkspaceInfo

__all__ = [
    "WorkspaceManager",
    "WorkspaceInfo",
]
