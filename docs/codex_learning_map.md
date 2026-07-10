# Codex 学习地图：每个角色都能用 Codex 做什么

## 结论

这张学习地图可以做，但必须把“官方明确能力”和“我们基于方法论做的迁移表达”分开。推荐主线是：

> Codex 不只用于写代码。它正在通过角色插件、Sites 和 Annotations，进入更多知识工作流程。读者可以从自己的角色出发，把真实材料交给 Codex，产出可检查、可迭代、可复用的工作成果。

## 主要依据

- OpenAI 官方文章：[Codex for every role, tool, and workflow](https://openai.com/index/codex-for-every-role-tool-workflow/) / [中文版](https://openai.com/zh-Hans-CN/index/codex-for-every-role-tool-workflow/)
- OpenAI Help Center：[Plugins in Codex](https://help.openai.com/en/articles/20001256-plugins-in-codex)
- OpenAI Help Center：[Using Codex with your ChatGPT plan](https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan)
- OpenAI Help Center：[ChatGPT Business release notes](https://help.openai.com/en/articles/11391654-chatgpt-business-release-notes)
- OpenAI Help Center：[ChatGPT Enterprise & Edu release notes](https://help.openai.com/en/articles/10128477-chatgpt-enterprise-edu-release-notes)

## 需要修正或避免的点

### 1. 非开发者比例

可以写：

- 每周有 500 万+ 人使用 Codex。
- 非开发者约占整体 Codex 用户 20%，增长速度超过开发者 3 倍。

不要写：

- “近一个月新用户中约 40% 为非开发者。”这个说法没有在当前官方材料中得到确认。

### 2. 六款角色插件

可以写成官方明确列出的六类：

| 插件 | 官方可支撑的用途 | 代表工具/数据源 |
|---|---|---|
| 数据分析 | 探索产品和业务数据，解释指标变化，创建报告和仪表板 | Snowflake、Databricks Genie、Hex、Tableau |
| 创意制作 | 把简报转化为可审阅素材，创建营销活动看板，展示广告变体、电商图片 | Figma、Canva、Shutterstock、Picsart、Fal |
| 销售 | 查找高优先级客户和信号，准备会议，跟进客户，更新记录，制定成交计划，审查风险交易 | Salesforce、HubSpot、Slack、Outreach、Clay、Rox、Actively |
| 产品设计 | 把早期想法转化为可审阅原型，探索产品方向，审查用户流程，从 URL 或截图制作原型 | Figma、Canva 等 |
| 公开股票投资 | 审阅收益，比较公司，跟踪信号，评估投资论点 | Moody's、Daloopa、Datasite、FactSet、LSEG、S&P、PitchBook、Hebbia |
| 投资银行 | 准备推介材料，分析可比公司和交易，把尽调转化为面向客户的建议 | 可信数据源 |

不要额外展开：

- 企业财务、私募、营销策略、战略咨询、法律。官方文章只说这些插件即将推出，没有展开具体任务。

### 3. Sites

可以写：

- Sites 可以把 Codex 的工作转成托管的交互式网站或应用，并通过 URL 在工作空间共享。
- 示例包括客户评审页、情景规划器、发布中心，以及图表、表单、跟踪器、决策辅助等交互组件。
- Help Center 补充说明：Sites 可用于创建、迭代和部署轻量级 JavaScript/TypeScript 内部应用，访问范围保持在工作空间内。

注意：

- Sites 是预览能力，面向符合条件的 Business、Enterprise、Edu 工作空间；不要写成所有用户都立即可用。

### 4. Annotations

可以写：

- Annotations 支持对代码、Markdown、文档、幻灯片、表格和 Codex 创建的网站进行局部批注。
- 用户指出具体位置后，Codex 聚焦修改，不需要从头重做。

注意：

- 这适合表达为“人负责判断和反馈，Codex 负责执行和迭代”。

### 5. 插件权限与可用性

可以写：

- 插件会把 skills、apps、app templates、workflow guidance 等能力打包到一个角色工作流里。
- 插件依赖的 app 仍受工作空间权限控制；用户不能通过插件访问自己在源系统中无权访问的文件、记录或频道。
- 管理员可以控制插件可用性、app 权限和角色访问。

不要写：

- “装了插件就能访问所有团队数据。”
- “所有用户都能马上使用这些插件。”

## 推荐 XMind 主干

```text
Codex 能做什么：每个角色都能用的智能工作台
  三种核心能力
    角色专属插件
    Sites
    Annotations
  通用方法：上下文 -> 任务 -> 工具 -> 验收
  六款官方角色插件
    数据分析
    创意制作
    销售
    产品设计
    公开股票投资
    投资银行
  Sites 可交付成果（官方示例）
    客户评审页
    情景规划器
    动态发布中心
    交互组件
  更多日常场景（基于官方能力迁移）
    资料整理与摘要
    报告、看板与业务复盘
    内容改写与创意素材
    客户沟通与项目推进
    产品原型与内部应用
    研究探索与实验支持
    团队流程沉淀
  真实团队怎么在用
    OpenAI 内部非技术团队
    Zapier 团队案例
    NVIDIA 研究团队案例
  软件工程（本书主线）
  不同角色的第一步
  传播要点与边界
```

## 与《Codex 快速入门》的关系

本书主线仍应放在“软件工程（本书主线）”分支：

- 第 1-2 章：能力边界与认知迁移。
- 第 3-8 章：个人工作流与 Harness 工程。
- 第 9-12 章：高频工程实战。
- 第 13-14 章：团队落地与治理。

非编程角色的表达用于扩大入口，不应反客为主。

## 更多日常场景怎么写才严谨

可以加“更多日常场景”，但必须标明它们是基于官方能力的迁移表达，而不是官方逐条列出的角色插件。建议只放以下几类：

| 场景 | 可以写 | 依据 |
|---|---|---|
| 资料整理与摘要 | 整理文档、会议材料、团队知识，生成摘要、问题清单和行动项 | Annotations 支持文档/Markdown/幻灯片/表格；Zapier 从 Slack、Google Docs、Coda 提取知识 |
| 报告、看板与业务复盘 | 解释指标变化，生成报告、仪表板和复盘材料 | 数据分析插件；OpenAI 内部创建仪表板；Zapier 生成复盘报告 |
| 内容改写与创意素材 | 将创意简报转成可审阅素材，迭代标题、论点和表达 | 创意制作插件；OpenAI 内部创意简报案例；Annotations 局部批注 |
| 客户沟通与项目推进 | 准备客户会议，整理客户信号、跟进计划和风险交易审查材料 | 销售插件；客户评审页 Sites 示例 |
| 产品原型与内部应用 | 从想法、URL 或截图生成可审阅原型，把流程做成轻量站点 | 产品设计插件；Sites；OpenAI 内部构建内部应用 |
| 研究探索与实验支持 | 寻找研究想法，整理实验线索，生成脚本或结构化分析 | NVIDIA 研究案例；公开股票投资插件；投资银行插件 |
| 团队流程沉淀 | 把复盘结果、团队知识和重复流程整理成计划、工单、模板或规则 | Zapier 事件响应计划/功能工单案例；插件打包 workflow guidance |

不建议加入尚无依据的泛化场景，例如“人力招聘全流程”“行政制度管理”“法务合同审查结论”“个人时间管理”等。除非后续有官方材料、书中案例或真实客户案例支撑。

## 传播边界

- 不说“万能办公助手”。
- 不说“一键完成所有工作”。
- 不说“所有用户立即可用”。
- 不把“即将推出”的插件写成已上线能力。
- 不给法务、财务、投资等专业场景下最终判断背书，只说“整理、分析、辅助生成材料”。
- “更多日常场景”要标注依据层级：官方明确示例、团队案例、或基于官方能力的迁移表达。

## 配套文件

- 推荐导图：[codex_use_cases_map.xmind](./codex_use_cases_map.xmind)
- 生成脚本：`python scripts/build_codex_use_cases_xmind.py`
- 工程向学习路径图：[codex_learning_map.xmind](./codex_learning_map.xmind)
- 工程向一页图：[codex_learning_map.svg](./codex_learning_map.svg)
