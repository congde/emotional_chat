#!/usr/bin/env python3
"""Generate Codex use-cases XMind (broader audience, not only AI programming).

Reference: https://openai.com/zh-Hans-CN/index/codex-for-every-role-tool-workflow/
"""

import json
import uuid
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "codex_use_cases_map.xmind"
RED_TITLE_STYLE = {
    "properties": {
        "fo:color": "#D92D20",
        "fo:font-weight": "bold",
    }
}


def new_id(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:20]}" if prefix else uuid.uuid4().hex[:24]


def topic(title: str, children=None, note: str | None = None, labels=None, style=None):
    data = {"id": new_id(), "class": "topic", "title": title}
    if children:
        data["children"] = {"attached": children}
    if note:
        data["notes"] = {
            "plain": {"content": note},
            "realHTML": {"content": f"<p>{note}</p>"},
        }
    if labels:
        data["labels"] = labels
    if style:
        data["style"] = style
    return data


def red_topic(title: str, children=None, note: str | None = None):
    return topic(title, children=children, note=note, style=RED_TITLE_STYLE)


def build_root():
    return topic(
        "Codex 能做什么：从编程助手到多角色工作流工具",
        children=[
            topic(
                "核心能力：三种能力",
                children=[
                    red_topic(
                        "角色专属插件",
                        children=[
                            topic("连接团队已在用的工具与上下文"),
                            topic("让 Codex 按角色工作方式运作"),
                            topic("把应用、技能、说明和工作流打包成可复用能力"),
                        ],
                    ),
                    red_topic(
                        "站点（Sites）",
                        children=[
                            topic("客户评审页：产品更新、未解决问题、使用趋势、后续步骤"),
                            topic("情景规划器：基于财务模型比较假设"),
                            topic("发布中心：最新话术、里程碑、负责人、决策（细节变化时自动更新）"),
                            topic("图表 / 表单 / 跟踪器 / 决策辅助等交互形式"),
                        ],
                    ),
                    red_topic(
                        "批注（Annotations）",
                        children=[
                            topic("代码、Markdown、文档、幻灯片、表格、站点"),
                            topic("例：选中导航栏改字体；高亮论点查来源；标记图表改标签"),
                            topic("人负责判断与反馈，Codex 负责执行与迭代"),
                        ],
                    ),
                ],
            ),
            topic(
                "核心方法：上下文 → 任务 → 工具 → 验收",
                children=[
                    red_topic("给上下文：提供文档、代码、截图、表格、会议记录和业务材料"),
                    red_topic("定义任务：明确目标、交付物和验收标准"),
                    red_topic("选择工具：按任务选择插件、浏览器、文档、表格、站点或代码环境"),
                    red_topic("产出成果：生成报告、图表、页面、脚本、原型、PR 或工作流"),
                    red_topic("批注迭代：指出具体问题，让 Codex 继续修改"),
                    red_topic("沉淀复用：把有效做法整理成模板、规则、Skill、runbook 或团队流程"),
                ],
            ),
            topic(
                "角色入口：六款官方角色插件",
                children=[
                    red_topic(
                        "数据分析",
                        children=[
                            topic("适合：分析师、业务团队、运营、财务"),
                            topic("探索产品与业务数据，解释指标变化原因"),
                            topic("创建报告和仪表板"),
                            topic("工具：Snowflake、Databricks Genie、Hex、Tableau 等"),
                        ],
                    ),
                    red_topic(
                        "创意制作",
                        children=[
                            topic("适合：营销、创意、品牌、内容团队"),
                            topic("把简报转化为可供审阅的素材"),
                            topic("创建营销活动看板、展示广告变体"),
                            topic("工具：Figma、Canva、Shutterstock、Picsart、Fal 等"),
                        ],
                    ),
                    red_topic(
                        "销售",
                        children=[
                            topic("适合：销售、售前、客户成功"),
                            topic("查找高优先级客户和信号，准备客户会议"),
                            topic("完成跟进、更新客户记录、制定成交计划、审查风险交易"),
                            topic("工具：Salesforce、HubSpot、Slack、Outreach、Clay、Rox、Actively 等"),
                        ],
                    ),
                    red_topic(
                        "产品设计",
                        children=[
                            topic("适合：产品经理、设计师、创业者"),
                            topic("把早期想法转化为团队可审阅的原型"),
                            topic("探索产品方向、审查用户流程、从 URL 制作原型"),
                            topic("让静态截图具备交互性；Figma、Canva 等继续推进"),
                        ],
                    ),
                    red_topic(
                        "公开股票投资",
                        children=[
                            topic("适合：投资者、研究分析师"),
                            topic("审阅收益、比较公司、跟踪信号"),
                            topic("评估投资论点是在增强还是减弱"),
                            topic("工具：Moody's、Daloopa、Datasite、FactSet、LSEG、S&P、PitchBook、Hebbia 等"),
                        ],
                    ),
                    red_topic(
                        "投资银行",
                        children=[
                            topic("适合：银行家、并购、战略顾问"),
                            topic("准备推介材料、分析可比公司和交易"),
                            topic("把尽职调查转化为面向客户的建议"),
                            topic("工具：使用可信数据源生成面向客户的材料"),
                        ],
                    ),
                ],
            ),
            topic(
                "成果形态：Sites 可交付成果",
                children=[
                    topic(
                        "客户评审页",
                        children=[
                            topic("展示产品更新、未解决问题、使用趋势和后续步骤"),
                            topic("通过 URL 在工作空间内共享给客户或团队"),
                        ],
                    ),
                    topic(
                        "情景规划器",
                        children=[
                            topic("基于财务模型比较不同假设"),
                            topic("把静态模型变成可交互的决策辅助页面"),
                        ],
                    ),
                    topic(
                        "动态发布中心",
                        children=[
                            topic("汇总最新话术、里程碑、负责人和决策"),
                            topic("在细节变化时保持发布材料更新"),
                        ],
                    ),
                    topic(
                        "交互组件",
                        children=[
                            topic("用图表、表单、跟踪器和决策辅助组件呈现工作"),
                            topic("适合把分析、计划或原型变成可演示成果"),
                        ],
                    ),
                ],
            ),
            topic(
                "扩展场景：更多日常工作",
                children=[
                    red_topic(
                        "资料整理与摘要",
                        children=[
                            topic("整理文档、会议材料和团队知识"),
                            topic("生成摘要、问题清单、行动项和后续跟进"),
                            topic("适合把分散材料变成可阅读、可分发的结果"),
                        ],
                    ),
                    red_topic(
                        "报告、看板与业务复盘",
                        children=[
                            topic("解释业务数据和关键指标变化"),
                            topic("生成报告、仪表板和业务绩效分析"),
                            topic("把复盘材料整理成结论、证据和下一步行动"),
                        ],
                    ),
                    red_topic(
                        "内容改写与创意素材",
                        children=[
                            topic("把创意简报转化为可审阅素材"),
                            topic("生成营销活动看板、广告变体和电商图片方向"),
                            topic("通过批注迭代标题、视觉、论点和表达方式"),
                        ],
                    ),
                    red_topic(
                        "客户沟通与项目推进",
                        children=[
                            topic("准备客户会议，整理客户信号和上下文"),
                            topic("生成跟进计划、成交计划和风险交易审查材料"),
                            topic("用客户评审页呈现产品更新、使用趋势和后续步骤"),
                        ],
                    ),
                    red_topic(
                        "产品原型与内部应用",
                        children=[
                            topic("把早期想法、URL 或截图转化为可审阅原型"),
                            topic("审查用户流程，探索产品方向"),
                            topic("把分析、流程或计划做成可共享的轻量站点"),
                        ],
                    ),
                    red_topic(
                        "研究探索与实验支持",
                        children=[
                            topic("寻找研究想法，整理实验线索"),
                            topic("为机器学习基础设施编写脚本"),
                            topic("整理公司、行业、收益和尽调材料，形成结构化分析"),
                        ],
                    ),
                    red_topic(
                        "团队流程沉淀",
                        children=[
                            topic("把复盘结果转化为事件响应计划"),
                            topic("把团队知识整理成功能工单或执行清单"),
                            topic("将重复流程沉淀为模板、规则或工作流说明"),
                        ],
                    ),
                ],
            ),
            topic(
                "真实案例：团队怎么在用",
                children=[
                    topic(
                        "OpenAI 内部（非技术团队）",
                        children=[
                            topic("构建内部应用"),
                            topic("准备高管材料"),
                            topic("创建仪表板"),
                            topic("创意简报 → 符合品牌和设计约束的成果"),
                        ],
                    ),
                    topic(
                        "Zapier 各团队",
                        children=[
                            topic("从 Slack、Google Docs、Coda 中提取团队知识"),
                            topic("生成复盘报告、事件响应计划和功能工单"),
                        ],
                    ),
                    topic(
                        "NVIDIA 研究人员",
                        children=[
                            topic("寻找研究想法"),
                            topic("为机器学习基础设施编写脚本"),
                            topic("加速实验工作流"),
                        ],
                    ),
                ],
            ),
            topic(
                "深度主线：软件工程",
                children=[
                    topic("理解陌生代码库，修复 bug，补充测试，完成重构"),
                    topic("编写自动化脚本，参与 PR、Review 和 CI/CD"),
                    topic("沉淀 AGENTS.md、Rules、Hooks、Skill、Subagent 和 MCP"),
                    topic(
                        "对应《Codex 快速入门》",
                        children=[
                            topic("第 1-2 章：能力边界与认知迁移"),
                            topic("第 3-8 章：个人工作流与 Harness 工程"),
                            topic("第 9-12 章：高频工程实战"),
                            topic("第 13-14 章：团队落地与治理"),
                        ],
                    ),
                ],
            ),
            topic(
                "开始行动：不同角色的第一步",
                children=[
                    topic("非技术读者：先拿一份真实材料，让 Codex 整理成可检查成果"),
                    topic("数据/运营：从产品或业务数据开始，解释指标变化并生成报告"),
                    topic("市场/创意：从创意简报开始，生成可审阅素材或活动看板"),
                    topic("销售/客户成功：从客户上下文开始，准备会议、跟进和成交计划"),
                    topic("产品/设计：从早期想法、URL 或截图开始，生成可审阅原型"),
                    topic("投资/金融：从收益、公司信息或尽调材料开始，形成结构化分析"),
                    topic("开发者：从一个小 bug 或小功能开始，跑通修改和验证闭环"),
                    topic("团队负责人：从一个重复工作流开始，沉淀模板、权限和试点计划"),
                ],
            ),
        ],
    )


def write_xmind(path: Path):
    sheet_id = new_id("sheet-")
    content = [
        {
            "id": sheet_id,
            "class": "sheet",
            "title": "Codex 能做什么",
            "rootTopic": build_root(),
            "extensions": [
                {
                    "provider": "org.xmind.ui.skeleton.structure.style",
                    "content": {"centralTopic": "org.xmind.ui.map.clockwise"},
                }
            ],
        }
    ]
    metadata = {
        "dataStructureVersion": "2",
        "creator": {"name": "emotional_chat", "version": "2.0"},
        "layoutEngineVersion": "3",
        "activeSheetId": sheet_id,
    }
    manifest = [
        {"path": "content.json", "media-type": "application/vnd.xmind.content+json"},
        {"path": "metadata.json", "media-type": "application/vnd.xmind.metadata+json"},
    ]

    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("content.json", json.dumps(content, ensure_ascii=False, indent=2).encode("utf-8"))
        zf.writestr("metadata.json", json.dumps(metadata, ensure_ascii=False).encode("utf-8"))
        zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False).encode("utf-8"))

    print(f"Created: {path} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    write_xmind(OUT)
