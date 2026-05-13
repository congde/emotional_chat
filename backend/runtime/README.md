# Runtime — Emotional Chat Agent Runtime

从线性 Workflow 升级为 **Runtime + Skills** 架构。

## 架构概览

```
┌───────────────────────────────────────────────────────┐
│                   ConversationRuntime                  │
│  ┌─────────────┐  ┌──────────┐  ┌───────────────┐    │
│  │ Lifecycle   │  │  Turn    │  │  Snapshot     │    │
│  │ Mixin       │  │  Mixin   │  │  Mixin        │    │
│  └─────────────┘  └──────────┘  └───────────────┘    │
│                                                       │
│  ┌─────────────────────────────────────────────────┐  │
│  │              SkillRegistry                       │  │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌──────────┐ │  │
│  │  │Emotion │ │Memory  │ │Planning│ │Reflect   │ │  │
│  │  │Skill   │ │Skill   │ │Skill   │ │Skill     │ │  │
│  │  └────────┘ └────────┘ └────────┘ └──────────┘ │  │
│  │  ┌────────┐                                      │  │
│  │  │Tool    │                                      │  │
│  │  │Skill   │                                      │  │
│  │  └────────┘                                      │  │
│  └─────────────────────────────────────────────────┘  │
│                                                       │
│  ┌────────────┐  ┌────────────┐  ┌───────────────┐   │
│  │ PolicyEngine│  │SessionFSM  │  │ModuleToggles  │   │
│  └────────────┘  └────────────┘  └───────────────┘   │
│                                                       │
│  ┌────────────┐  ┌────────────┐  ┌───────────────┐   │
│  │HookDispatch│  │BudgetPress │  │FallbackManager│   │
│  └────────────┘  └────────────┘  └───────────────┘   │
└───────────────────────────────────────────────────────┘
          │                │                │
    ┌─────┴─────┐   ┌─────┴─────┐   ┌─────┴─────┐
    │ LLMClient │   │ToolExecutor│   │Permission │
    │  Protocol │   │  Protocol  │   │Prompter   │
    └───────────┘   └───────────┘   └───────────┘
```

## 目录结构

```
backend/runtime/
├── __init__.py               # 顶层导出
├── prompt_builder.py         # 动态系统提示构建
├── task_packet.py            # 结构化任务定义
│
├── protocols/                # 三协议抽象层
│   ├── __init__.py
│   ├── llm_client.py         # LLM 协议 (stream_turn / complete)
│   ├── tool_executor.py      # 工具执行协议
│   └── permission_prompter.py # 权限确认协议
│
├── session/                  # 会话管理
│   ├── __init__.py
│   ├── fsm.py                # 6 状态 FSM
│   ├── lineage.py            # 会话血缘追踪
│   └── resume.py             # 检查点恢复
│
├── config/                   # 配置管理
│   ├── __init__.py
│   ├── toggles.py            # ModuleToggles 特性开关
│   └── guards.py             # is_module_enabled / require_module
│
├── skills/                   # 技能系统
│   ├── __init__.py
│   ├── base.py               # Skill ABC + SkillRegistry
│   ├── emotion_skill.py      # 情感感知 (from AgentCore._perceive)
│   ├── memory_skill.py       # 记忆检索/编码/巩固
│   ├── planning_skill.py     # 意图规划 (from Planner)
│   ├── reflect_skill.py      # 反思评估 (from Reflector)
│   └── tool_skill.py         # 工具调用 (from ToolCaller)
│
├── policy/                   # 声明式策略引擎
│   ├── __init__.py
│   └── policy_engine.py      # 规则评估 + 危机干预
│
├── hooks/                    # 生命周期钩子
│   ├── __init__.py
│   └── base.py               # PluginHook + HookDispatcher
│
├── conversation/             # 对话运行时
│   ├── __init__.py           # ConversationRuntime (mixin 组合)
│   ├── _helpers.py           # TurnResult + SSE helpers
│   ├── _lifecycle.py         # 生命周期管理
│   ├── _turn.py              # ReAct 循环 (替代 7 阶段 workflow)
│   └── _snapshot.py          # 快照与健康检查
│
├── activity/                 # 活动追踪与蒸馏
│   ├── __init__.py
│   ├── tracker.py            # 活动记录器
│   └── distiller.py          # L2→L3/L4 记忆蒸馏
│
├── budget/                   # 预算管理
│   ├── __init__.py
│   ├── pressure.py           # 预算压力注入
│   └── warning.py            # 过期警告清理
│
├── fallback/                 # 降级管理
│   ├── __init__.py
│   └── manager.py            # 模型降级策略
│
├── workspace/                # 工作区隔离
│   ├── __init__.py
│   └── manager.py            # 用户级目录隔离
│
└── tools/                    # 工具辅助
    ├── __init__.py
    ├── dedup.py              # 工具调用去重
    └── repair.py             # 工具名模糊修复
```

## 核心概念

### 1. Protocol-first 三协议

| 协议 | 方法 | 职责 |
|------|------|------|
| `LLMClient` | `stream_turn()`, `complete()` | LLM 调用抽象 |
| `ToolExecutor` | `execute()`, `list_tools()` | 工具执行抽象 |
| `PermissionPrompter` | `confirm()` | 权限确认抽象 |

所有核心逻辑依赖 Protocol 而非具体实现，方便测试和替换。

### 2. Skill-based 技能系统

每个旧的 workflow 阶段变成独立的 Skill：

| 旧模块 | 新 Skill | execute 模式 |
|--------|----------|-------------|
| AgentCore._perceive | EmotionSkill | analyze |
| MemoryManager.retrieve/encode | MemorySkill | retrieve/encode/consolidate |
| Planner.plan | PlanningSkill | plan |
| ToolCaller.execute | ToolSkill | execute |
| Reflector.reflect | ReflectSkill | evaluate/followup |

### 3. SessionFSM 6 状态机

```
idle → running → (requires_approval → running) → compacted/forked → terminated
                                         ↘ failed → terminated
```

### 4. ModuleToggles 特性开关

环境变量覆盖：`EMOTIONAL_CHAT__MODULES__<MODULE>__ENABLED=true/false`

### 5. PolicyEngine 声明式策略

默认策略：
- `crisis_intervention` (priority 100): 情感危机自动触发干预
- `high_intensity_emotion` (priority 80): 高强度情感降级处理
- `sensitive_assessment` (priority 60): 敏感内容评估
- `tool_rate_limit` (priority 40): 工具调用频率限制

## 快速开始

```python
from runtime import (
    ConversationRuntime,
    LLMClient,
    ToolExecutor,
    PermissionPrompter,
)

# 1. 创建协议实现
llm: LLMClient = MyLLMClient(api_key="...")
tools: ToolExecutor = MyToolExecutor()
permission: PermissionPrompter = MyPermissionPrompter()

# 2. 创建运行时
runtime = ConversationRuntime(
    llm=llm,
    tools=tools,
    permission=permission,
    user_id="user_123",
    session_id="session_456",
)

# 3. 启动会话
await runtime.start()

# 4. 处理对话轮次
result = await runtime.process_turn(user_input="我今天感觉很焦虑")
print(result.text)  # AI 的回复
print(result.emotion_tag)  # 情感标签
print(result.metadata)  # 元数据

# 5. 结束会话
await runtime.stop()
```

## 从旧架构迁移

| 旧代码 | 新代码 |
|--------|--------|
| `AgentCore.process(query)` | `ConversationRuntime.process_turn(user_input)` |
| `AgentCore._perceive()` | `EmotionSkill.execute(mode="analyze")` |
| `Planner.plan()` | `PlanningSkill.execute(mode="plan")` |
| `ToolCaller.execute()` | `ToolSkill.execute(mode="execute")` |
| `Reflector.reflect()` | `ReflectSkill.execute(mode="evaluate")` |
| `sys.path.insert(0, ...)` | Protocol 依赖注入 |
| 7 阶段线性 workflow | Skill-based ReAct 循环 |

## 设计原则

1. **Protocol-first**: 核心逻辑依赖 Protocol，不依赖具体实现
2. **Skill-based composition**: 每个阶段是独立 Skill，可插拔
3. **FSM-governed**: 会话状态由 FSM 严格管理
4. **Toggle-gated**: 每个模块可独立开关，支持灰度
5. **Hook-extensible**: 生命周期钩子支持注入行为
6. **Policy-driven**: 声明式策略替代硬编码逻辑
7. **Fail-safe**: 任何模块失败不应导致整体崩溃
8. **Idempotent distiller**: 相同输入产生相同输出
