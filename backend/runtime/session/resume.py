# -*- coding: utf-8 -*-
"""
Session resume — 从检查点恢复会话
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class SessionResumer:
    """
    会话恢复器 — 从检查点恢复会话状态

    Usage::

        resumer = SessionResumer(checkpoint_dir=Path("data/checkpoints"))
        state = resumer.load(session_id="session_123")
    """

    def __init__(self, checkpoint_dir: Optional[Path] = None):
        self._checkpoint_dir = checkpoint_dir or Path("data/checkpoints")

    def save(self, session_id: str, state: Dict[str, Any]) -> None:
        """保存会话状态到检查点"""
        try:
            self._checkpoint_dir.mkdir(parents=True, exist_ok=True)
            path = self._checkpoint_dir / f"{session_id}.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            logger.info("Saved session checkpoint: %s", session_id)
        except Exception as e:
            logger.warning("Failed to save checkpoint for %s: %s", session_id, e)

    def load(self, session_id: str) -> Optional[Dict[str, Any]]:
        """从检查点加载会话状态"""
        try:
            path = self._checkpoint_dir / f"{session_id}.json"
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.warning("Failed to load checkpoint for %s: %s", session_id, e)
        return None

    def delete(self, session_id: str) -> None:
        """删除检查点"""
        try:
            path = self._checkpoint_dir / f"{session_id}.json"
            if path.exists():
                path.unlink()
        except Exception as e:
            logger.warning("Failed to delete checkpoint for %s: %s", session_id, e)
