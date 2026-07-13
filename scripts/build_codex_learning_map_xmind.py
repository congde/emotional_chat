#!/usr/bin/env python3
"""Generate Codex learning map XMind from codex_learning_map.md structure."""

import json
import uuid
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "codex_learning_map.xmind"


def new_id() -> str:
    return str(uuid.uuid4()).replace("-", "")[:24]


def topic(title: str, children=None, note: str | None = None, labels=None):
    t = {"id": new_id(), "class": "topic", "title": title}
    if note:
        t["notes"] = {
            "plain": {"content": note},
            "realHTML": {"content": f"<p>{note}</p>"},
        }
    if labels:
        t["labels"] = labels
    if children:
        t["children"] = {"attached": children}
    return t


def build_content():
    root = topic(
        "Codex 学习地图：从会问 AI 到工程交付",
        note="配套《Codex 快速入门》| 沿着「认知迁移 → Harness 工程 → 高频实战 → 团队落地」四段路径，建立可验证、可审查、可复用的 AI 编程能力。",
        children=[
            topic(
                "核心心智",
                note="Codex 不只是代码生成器，更是参与真实软件工程的智能交付工具。关键闭环：任务 → 上下文 → 执行 → 验证 → 审查 → 沉淀",
                children=[
                    topic("交付工具，不是聊天机器人"),
                    topic("能力边界：上下文不完整、会幻觉、会漏改、会误判"),
                    topic("心智模型：任务、上下文、验证、审查"),
                ],
            ),
            topic(
                "1. 认知迁移（第 1-2 章）",
                labels=["起点"],
                children=[
                    topic("第 1 章 Codex 不是聊天机器人，而是交付工具"),
                    topic("第 2 章 AI 编程的最小原理——知道边界在哪里"),
                    topic(
                        "要建立的能力",
                        children=[
                            topic("把 Codex 理解为交付工具"),
                            topic("理解 AI 编程能力边界"),
                            topic("建立「任务、上下文、验证、审查」心智"),
                        ],
                    ),
                    topic(
                        "学习检查点",
                        children=[
                            topic("能说清楚什么任务适合委托给 Codex"),
                            topic("能给出清晰任务目标和接受标准"),
                            topic("知道高风险任务需要人工判断和分级验证"),
                        ],
                    ),
                ],
            ),
            topic(
                "2. 个人工作流（第 3-8 章）",
                labels=["Harness 工程"],
                children=[
                    topic("第 3 章 第一次任务：跑通一条闭环"),
                    topic("第 4 章 从 Codex 的任务地图"),
                    topic("第 5 章 第一个可复用工作流（emotional_chat 项目）"),
                    topic("第 6 章 AGENTS.md：给 Agent 的项目说明书"),
                    topic("第 7 章 Rules、Hooks 与 Approvals：先约束，再放权"),
                    topic("第 8 章 Skill、Subagent 与 MCP：用 Harness 扩展能力"),
                    topic(
                        "学习检查点",
                        children=[
                            topic("打开项目 → 描述目标 → 观察修改 → 运行检查 → 复盘沉淀"),
                            topic("能为项目写出最小可用的 AGENTS.md"),
                            topic("能把成功经验沉淀成可复用工作流"),
                        ],
                    ),
                ],
            ),
            topic(
                "3. 高频实战（第 9-12 章）",
                labels=["场景实战"],
                children=[
                    topic("第 9 章 场景一：接手陌生代码库"),
                    topic("第 10 章 场景二：修 bug、补测试、做回归"),
                    topic("第 11 章 场景三：跨前后端功能开发"),
                    topic("第 12 章 场景四：PR、Review 与 CI/CD 自动化"),
                    topic(
                        "学习检查点",
                        children=[
                            topic("能让 Codex 产出项目地图和影响分析"),
                            topic("能把 bug 报告整理成可执行任务"),
                            topic("能要求最小变更、可审查提交和分层验证"),
                        ],
                    ),
                ],
            ),
            topic(
                "4. 团队落地（第 13-14 章）",
                labels=["终点"],
                children=[
                    topic("第 13 章 从个人助手到团队级研发流程"),
                    topic("第 14 章 Codex 的边界、风险与工程方法论"),
                    topic(
                        "学习检查点",
                        children=[
                            topic("能判断什么时候值得团队化"),
                            topic("能设计一条小团队试点主线"),
                            topic("能把 AI 编程能力沉淀为项目资产和组织能力"),
                        ],
                    ),
                ],
            ),
            topic(
                "按角色怎么读",
                children=[
                    topic("在职开发者：第 1-3 章打底，重点读第 5-12 章"),
                    topic("技术负责人/架构师：第 1-2 章共识，重点读第 6-8、12-14 章"),
                    topic("AI 编程探索者：第 3-8 章，升级稳定工作流"),
                    topic("非传统开发岗位：第 3、5、6、8 章，迁移「上下文 → 任务 → 验收」"),
                ],
            ),
            topic(
                "传播关键词",
                children=[
                    topic("场景实战"),
                    topic("交付闭环"),
                    topic("Harness 工程"),
                    topic("可验证 / 可审查 / 可复用"),
                ],
            ),
        ],
    )

    sheet_id = new_id()
    content = [
        {
            "id": sheet_id,
            "class": "sheet",
            "title": "Codex 学习地图",
            "rootTopic": root,
            "extensions": [
                {
                    "provider": "org.xmind.ui.skeleton.structure.style",
                    "content": {"centralTopic": "org.xmind.ui.map.clockwise"},
                }
            ],
        }
    ]
    return content


def write_xmind(path: Path):
    content = build_content()
    content_json = json.dumps(content, ensure_ascii=False, indent=2)
    metadata = {
        "dataStructureVersion": "2",
        "creator": {"name": "emotional_chat", "version": "1.0"},
        "layoutEngineVersion": "3",
    }
    manifest = [
        {"path": "content.json", "media-type": "application/vnd.xmind.content+json"},
        {"path": "metadata.json", "media-type": "application/vnd.xmind.metadata+json"},
    ]

    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("content.json", content_json.encode("utf-8"))
        zf.writestr("metadata.json", json.dumps(metadata, ensure_ascii=False).encode("utf-8"))
        zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False).encode("utf-8"))

    print(f"Created: {path} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    write_xmind(OUTPUT)
