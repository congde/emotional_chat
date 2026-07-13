"""
从自然语言指令中调度 Hermes 原子操作（启发式 + 可扩展）。

后续可接 LLM function-calling 或外挂 MCP（与 Nous Hermes 文档中的 MCP 章节一致）。
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List

from backend.hermes import operations as op
from backend.hermes.settings import get_hermes_settings


def run_hermes_dispatch(instruction: str, **_: Any) -> Dict[str, Any]:
    """
    Agent 工具入口：根据 instruction 尽量执行联网 / docx / drawio / figma / 列目录 / 受控 shell 等。
    """
    settings = get_hermes_settings()
    if not settings.tools_enabled:
        return {"ok": False, "error": "HERMES_TOOLS_ENABLED 未开启"}
    if not settings.workspace_root or not os.path.isdir(settings.workspace_root):
        return {
            "ok": False,
            "error": "请设置有效的 HERMES_WORKSPACE_ROOT（例如书稿与 drawio 所在文件夹）",
        }

    text = (instruction or "").strip()
    steps: List[Dict[str, Any]] = []
    root = settings.workspace_root

    # 0) 受控 Shell（单行 cmd，cwd=工作区）
    m_shell = re.search(
        r"(?:执行命令|运行命令|shell|cmd)[:：]\s*(.+)$", text, re.I | re.M
    )
    if m_shell:
        cmd_line = m_shell.group(1).strip()
        steps.append(
            {
                "action": "shell",
                "result": op.run_shell_in_workspace(root, cmd_line, settings),
            }
        )

    # 1) 联网
    urls = op.extract_urls(text)
    if urls and settings.web_fetch_enabled:
        for u in urls[:2]:
            steps.append({"action": "web_fetch", "result": op.web_fetch_text(u, settings)})
    elif urls and not settings.web_fetch_enabled:
        steps.append({"action": "web_fetch", "skipped": True, "reason": "HERMES_WEB_FETCH_ENABLED=0"})

    # 2) Figma
    fig_keys = re.findall(r"figma\.com/(?:file|design)/([A-Za-z0-9]+)", text, re.I)
    for fk in fig_keys[:1]:
        steps.append({"action": "figma", "result": op.figma_file_summary(fk, settings.figma_token)})

    # 3) 路径集合
    paths = op.extract_paths(text)
    for m in re.finditer(r"([\w\-./\\]+\.(?:docx|drawio|xml))\b", text, re.I):
        p = m.group(1).strip().strip('"').strip("'")
        if p not in paths:
            paths.append(p)

    # 3a) 纯文本写入：写入\s*path\s*[:：]\s* 然后多行 或 内容[:：]
    m_w = re.search(
        r"写入文件\s+([\w\-./\\]+\.(?:txt|md|json))\s*[:：]\s*([\s\S]+)$",
        text,
        re.I,
    )
    if m_w:
        rel_w, body = m_w.group(1).strip(), m_w.group(2).strip()
        try:
            steps.append(
                {"action": "write_text", "path": rel_w, "result": op.write_text_file(root, rel_w, body)}
            )
        except Exception as e:
            steps.append({"action": "write_text", "path": rel_w, "error": str(e)})

    for rel in paths[:4]:
        rel_norm = rel.replace("\\", "/")
        low = rel_norm.lower()
        try:
            if low.endswith(".docx"):
                # 末尾追加
                if "追加" in text or "append" in text.lower():
                    m_ap = re.search(
                        r"(?:追加|append)(?:到|入)?[^:：\n]*[:：]\s*([\s\S]+)$", text, re.I
                    )
                    if m_ap:
                        chunk = m_ap.group(1).strip()
                        steps.append(
                            {
                                "action": "docx_append",
                                "path": rel_norm,
                                "result": op.docx_append_paragraph(root, rel_norm, chunk),
                            }
                        )
                elif "替换" in text or "改成" in text or "replace" in text.lower():
                    old_t, new_t = None, None
                    if "改成" in text:
                        left, right = text.split("改成", 1)
                        old_t = re.sub(r"^.*[把将]", "", left, flags=re.S).strip().strip("「\"'").strip()
                        new_t = right.strip().strip("」\"'").strip()
                    if not old_t or not new_t:
                        m = re.search(
                            r"[「\"']([^\"'」]{1,500})[」\"'](?:改为|换成|改成)[「\"']?([^\"'」\n]{1,500})[」\"']?",
                            text,
                        )
                        if m:
                            old_t, new_t = m.group(1), m.group(2)
                    if old_t and new_t:
                        steps.append(
                            {
                                "action": "docx_replace",
                                "path": rel_norm,
                                "result": op.docx_replace_text(root, rel_norm, old_t, new_t),
                            }
                        )
                    else:
                        steps.append(
                            {
                                "action": "docx_replace",
                                "skipped": True,
                                "hint": "请说明替换前后文本，例如：把「旧句」改成「新句」",
                            }
                        )
                else:
                    steps.append(
                        {"action": "docx_read", "path": rel_norm, "result": op.docx_get_text(root, rel_norm)}
                    )

            elif low.endswith(".drawio") or (
                low.endswith(".xml") and ("drawio" in text.lower() or "图表" in text)
            ):
                # 更新单元格：id 2 改为 xxx / cell 3 设为 yyy
                m_cell = re.search(
                    r"(?:id|cell|格子|图形)\s*[=为:：]?\s*([0-9A-Za-z_.-]+)\s*(?:改为|设为|改成|更新为)[:：\s]*[「\"']?([^」\"'\n]{1,2000})[」\"']?",
                    text,
                    re.I,
                )
                if m_cell:
                    cid, val = m_cell.group(1), m_cell.group(2).strip()
                    steps.append(
                        {
                            "action": "drawio_set_cell",
                            "path": rel_norm,
                            "result": op.drawio_set_cell_value(root, rel_norm, cid, val),
                        }
                    )
                elif "列出" in text or "结构" in text or "summary" in text.lower():
                    steps.append(
                        {
                            "action": "drawio_summary",
                            "path": rel_norm,
                            "result": op.drawio_summary(root, rel_norm),
                        }
                    )
                else:
                    steps.append(
                        {
                            "action": "drawio_summary",
                            "path": rel_norm,
                            "result": op.drawio_summary(root, rel_norm),
                        }
                    )

            elif any(low.endswith(ext) for ext in (".md", ".txt", ".json")) and any(
                k in text for k in ("读", "打开", "查看", "read", "show")
            ):
                steps.append(
                    {"action": "read_text", "path": rel_norm, "result": op.read_text_file(root, rel_norm)}
                )
        except Exception as e:
            steps.append({"action": "path_op", "path": rel_norm, "error": str(e)})

    # 4) 列目录
    if not paths and not m_w and any(
        k in text for k in ("列出", "有哪些文件", "目录", "ls", "list")
    ):
        steps.append({"action": "list_files", "result": op.list_workspace_files(root, "", "*", 300)})

    if not steps:
        return {
            "ok": True,
            "message": "未匹配到可执行操作。可尝试：shell:命令 ；https 链接；相对路径 .docx/.drawio；"
            "「写入文件 path:内容」；开启 HERMES_WEB_FETCH_ENABLED / HERMES_SHELL_ENABLED。",
            "steps": [],
        }

    errors: List[str] = []
    for st in steps:
        r = st.get("result")
        if isinstance(r, dict) and r.get("ok") is False:
            errors.append(str(r.get("error", "unknown")))
    return {"ok": not errors, "errors": errors, "steps": steps, "workspace": root}


def run_hermes_dispatch_json(instruction: str) -> str:
    """供日志或测试：返回 JSON 字符串。"""
    return json.dumps(run_hermes_dispatch(instruction), ensure_ascii=False, indent=2)
