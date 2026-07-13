"""识别「工作区 / 出书 / 图表 / 联网」类意图（优先于纯情绪路由）。"""

from __future__ import annotations

import re

from backend.hermes.settings import get_hermes_settings


def workspace_automation_intent(user_input: str) -> bool:
    if not get_hermes_settings().tools_enabled:
        return False
    t = (user_input or "").strip()
    if len(t) < 4:
        return False
    if re.search(r"https?://", t, re.I):
        return True
    keys = (
        "docx",
        "doc",
        "word",
        "drawio",
        "figma",
        "工作区",
        "出书",
        "书稿",
        "章节",
        "改写",
        "替换",
        "插图",
        "图表",
        "网页",
        "抓取",
        "下载页面",
        "mxgraph",
        "执行命令",
        "运行命令",
        "shell",
        "追加",
        "写入文件",
        "保存为",
    )
    tl = t.lower()
    return any(k in t for k in keys) or any(
        k in tl for k in ("drawio", "docx", "figma", "word", "append", "cmd")
    )
