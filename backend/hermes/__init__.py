"""
Hermes 风格本地工作区与自动化工具（对齐 Nous Hermes 的「工具 + 网关」思路）。

本包不嵌入 hermes-agent 仓库；在 Windows 上提供受控工作区内的文件、联网抓取、
Word(docx)、draw.io(XML)、Figma(只读) 等能力，供 Agent 或 HTTP 调用。

参考: https://github.com/nousresearch/hermes-agent
"""

from backend.hermes.settings import HermesSettings, get_hermes_settings

__all__ = ["HermesSettings", "get_hermes_settings"]
