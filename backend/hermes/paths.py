"""工作区内路径解析（防止路径穿越）。"""

from __future__ import annotations

from pathlib import Path
from typing import Union

PathLike = Union[str, Path]


def get_workspace_root(root: str) -> Path:
    r = Path(root).expanduser().resolve()
    if not r.is_dir():
        raise ValueError("HERMES_WORKSPACE_ROOT 不是有效目录: {}".format(root))
    return r


def resolve_workspace_path(workspace_root: Path, user_path: str) -> Path:
    """
    将用户给出的路径解析为工作区内绝对路径。
    允许：相对路径；或以 workspace 为前缀的绝对路径。
    """
    raw = (user_path or "").strip().strip('"').strip("'")
    if not raw:
        raise ValueError("路径为空")

    p = Path(raw).expanduser()
    if not p.is_absolute():
        out = (workspace_root / p).resolve()
    else:
        out = p.resolve()

    workspace_root = workspace_root.resolve()
    try:
        out.relative_to(workspace_root)
    except ValueError:
        raise ValueError("路径必须位于 HERMES_WORKSPACE_ROOT 内")
    return out
