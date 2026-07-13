# -*- coding: utf-8 -*-
"""
Session lineage — 会话血缘追踪

追踪会话的创建、分叉、合并等血缘关系。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class SessionLineage:
    """会话血缘记录"""

    session_id: str
    parent_id: Optional[str] = None
    fork_point: Optional[str] = None  # 分叉点的消息 ID
    children: List[str] = field(default_factory=list)
    created_at: str = ""


class LineageTracker:
    """
    会话血缘追踪器

    追踪会话的创建和分叉关系，用于：
    - 会话恢复
    - 分叉对话追踪
    - 审计和调试
    """

    def __init__(self):
        self._lineages: Dict[str, SessionLineage] = {}

    def register(self, session_id: str, parent_id: Optional[str] = None) -> SessionLineage:
        """注册新会话"""
        lineage = SessionLineage(
            session_id=session_id,
            parent_id=parent_id,
        )
        self._lineages[session_id] = lineage

        if parent_id and parent_id in self._lineages:
            self._lineages[parent_id].children.append(session_id)

        return lineage

    def get_lineage(self, session_id: str) -> Optional[SessionLineage]:
        """获取会话血缘"""
        return self._lineages.get(session_id)

    def get_ancestors(self, session_id: str) -> List[str]:
        """获取所有祖先会话"""
        ancestors = []
        current = self._lineages.get(session_id)
        while current and current.parent_id:
            ancestors.append(current.parent_id)
            current = self._lineages.get(current.parent_id)
        return ancestors
