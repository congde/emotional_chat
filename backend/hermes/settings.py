"""Hermes 工作区与联网开关（环境变量）。"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Optional


def _truthy(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class HermesSettings:
    tools_enabled: bool
    workspace_root: str
    web_fetch_enabled: bool
    web_allowlist: List[str]  # 空表示不限制域名（仍限制大小与 https）
    web_max_bytes: int
    figma_token: Optional[str]
    shell_enabled: bool
    shell_timeout_sec: int


def get_hermes_settings() -> HermesSettings:
    raw = os.getenv("HERMES_WEB_ALLOWLIST", "").strip()
    allow = [x.strip().lower() for x in raw.split(",") if x.strip()]
    max_bytes = int(os.getenv("HERMES_WEB_MAX_BYTES", "524288"))
    shell_timeout = int(os.getenv("HERMES_SHELL_TIMEOUT_SEC", "60"))
    return HermesSettings(
        tools_enabled=_truthy("HERMES_TOOLS_ENABLED"),
        workspace_root=os.getenv("HERMES_WORKSPACE_ROOT", "").strip(),
        web_fetch_enabled=_truthy("HERMES_WEB_FETCH_ENABLED"),
        web_allowlist=allow,
        web_max_bytes=max(4096, min(max_bytes, 5_000_000)),
        figma_token=os.getenv("FIGMA_ACCESS_TOKEN", "").strip() or None,
        shell_enabled=_truthy("HERMES_SHELL_ENABLED"),
        shell_timeout_sec=max(5, min(shell_timeout, 300)),
    )


def hermes_ready() -> bool:
    s = get_hermes_settings()
    if not s.tools_enabled or not s.workspace_root:
        return False
    return os.path.isdir(s.workspace_root)
