# Agent核心模块实现总结

## 概述

本文档总结Agent核心模块的实现细节，包括架构设计、模块功能、使用方法和扩展指南。

## 架构设计

### 整体架构

```
┌─────────────────────────────────────────────────────┐
│                  Agent Core                         │
│  (核心控制器，协调所有模块)                          │
└─────────────────────────────────────────────────────┘
         │         │         │         │
         ▼         ▼         ▼         ▼
    ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
    │Memory  │ │Planner │ │Tool     │ │Reflector│
    │Hub     │ │        │ │Caller   │ │        │
    └────────┘ └────────┘ └────────┘ └────────┘
         │         │         │         │
         ▼         ▼         ▼         ▼
    ┌──────────────────────────────────────┐
    │          External Tools              │
    │  - Calendar API                       │
    │  - Audio Player                       │
    │  - Psychology DB                      │
    │  - Scheduler Service                  │
    └──────────────────────────────────────┘
```

### 模块职责

| 模块 | 职责 | 主要功能 |
|------|------|----------|
| Agent Core | 核心控制器 | 协调所有模块，管理完整交互流程 |
| Memory Hub | 记忆中枢 | 记忆编码、检索、巩固 |
| Planner | 任务规划 | 目标识别、任务分解、策略选择 |
| Tool Caller | 工具调用 | 工具注册、调用执行、结果处理 |
| Reflector | 反思优化 | 效果评估、策略优化、回访规划 |

## 核心模块详解

### 1. Agent Core

**文件**: `backend/agent/agent_core.py`

**主要类**: `AgentCore`

**核心方法**:

```python
async def process(user_input, user_id, conversation_id=None)
    """处理用户输入的完整流程"""
    # 1. 感知层：分析用户输入
    # 2. 记忆检索：获取相关记忆
    # 3. 任务规划：生成执行计划
    # 4. 执行计划：调用工具、生成回复
    # 5. 记忆巩固：保存新记忆
    # 6. 反思评估：评估交互效果
    # 7. 记录历史：保存执行记录

async def process_with_mcp(user_input, user_id, conversation_id=None)
    """使用MCP协议处理（新接口）"""
    # 支持标准化的MCP消息传递
```

**特点**:
- 支持传统接口和MCP协议
- 完整的错误处理和降级机制
- 可配置的模块组合

### 2. Memory Hub

**文件**: `backend/agent/memory_hub.py`

**主要类**: `MemoryHub`

**核心方法**:

```python
def encode(experience) -> Dict
    """编码：将新经验转换为记忆"""
    
def retrieve(query, user_id, context, top_k) -> List[Dict]
    """检索：基于查询和上下文检索相关记忆"""
    
def consolidate(memory) -> bool
    """巩固：将工作记忆转移到长期记忆"""
    
def get_user_profile(user_id) -> Dict
    """获取用户画像"""
```

**记忆类型**:
- 情景记忆 (Episodic): 事件、经历
- 语义记忆 (Semantic): 知识、概念
- 程序记忆 (Procedural): 技能、策略
- 对话记忆 (Conversation): 对话历史

### 3. Planner

**文件**: `backend/agent/planner.py`

**主要类**: `Planner`

**核心方法**:

```python
async def plan(user_input, context) -> ExecutionPlan
    """生成执行计划"""
    # 1. 目标识别
    # 2. 复杂度判断
    # 3. 目标分解
    # 4. 任务图构建
    # 5. 策略选择
    # 6. 执行计划生成
```

**目标类型**:
- INFORMATION_QUERY: 信息查询
- EMOTIONAL_SUPPORT: 情感支持
- PROBLEM_SOLVING: 问题解决
- BEHAVIOR_CHANGE: 行为改变
- CASUAL_CHAT: 闲聊

**执行策略**:
- DIRECT_RESPONSE: 直接回复
- EMPATHY_FIRST: 情感优先
- TOOL_USE: 工具调用
- SCHEDULED_FOLLOWUP: 定时回访
- CONVERSATIONAL: 对话引导

### 4. Tool Caller

**文件**: `backend/agent/tool_caller.py`

**主要类**: `ToolCaller`, `ToolRegistry`

**核心方法**:

```python
async def call(tool_name, parameters) -> Dict
    """调用工具"""
    
async def call_with_mcp(mcp_message) -> MCPMessage
    """使用MCP协议调用工具"""
```

**内置工具**:
- `search_memory`: 搜索记忆
- `get_emotion_log`: 获取情绪日志
- `set_reminder`: 设置提醒
- `recommend_meditation`: 推荐冥想
- `recommend_resource`: 推荐资源
- `psychological_assessment`: 心理评估
- `check_calendar`: 查看日历

### 5. Reflector

**文件**: `backend/agent/reflector.py`

**主要类**: `Reflector`

**核心方法**:

```python
async def evaluate(interaction) -> Dict
    """评估交互效果"""
    # 1. 收集指标
    # 2. 判断结果
    # 3. 分析原因
    # 4. 生成改进建议
    # 5. 更新经验库

async def plan_followup(user_id, context) -> Optional[Dict]
    """规划回访任务"""
```

**评估指标**:
- 用户满意度
- 响应时间
- 目标达成度
- 情绪变化
- 工具使用效果

## 使用流程

### 完整交互流程

```
用户输入
    ↓
[Agent Core] 感知层
    ├─→ 情感分析
    ├─→ 意图识别
    └─→ 实体提取
    ↓
[Memory Hub] 记忆检索
    ├─→ 语义检索
    ├─→ 时间检索
    └─→ 情绪检索
    ↓
[Planner] 任务规划
    ├─→ 目标识别
    ├─→ 任务分解
    └─→ 策略选择
    ↓
[Tool Caller] 工具调用 (可选)
    ├─→ 参数验证
    ├─→ 执行调用
    └─→ 结果处理
    ↓
[Agent Core] 生成回复
    ├─→ 上下文组装
    ├─→ LLM调用
    └─→ 回复生成
    ↓
[Memory Hub] 记忆巩固
    ├─→ 编码新记忆
    └─→ 更新工作记忆
    ↓
[Reflector] 反思评估
    ├─→ 效果评估
    ├─→ 原因分析
    └─→ 改进建议
    ↓
返回结果
```

## MCP协议支持

所有模块都支持MCP (Message Communication Protocol) 协议，实现标准化的模块间通信。

### MCP消息类型

- `USER_INPUT`: 用户输入
- `PLANNER_OUTPUT`: 规划输出
- `TOOL_REQUEST`: 工具请求
- `TOOL_RESPONSE`: 工具响应
- `AGENT_RESPONSE`: Agent回复
- `REFLECTOR_EVALUATION`: 反思评估
- `INTERNAL_COMMUNICATION`: 内部通信

### 使用MCP协议

```python
# 使用MCP协议处理
mcp_message = await agent.process_with_mcp(
    user_input="我最近心情很不好",
    user_id="user_123"
)

# MCP消息包含完整的上下文和元数据
print(mcp_message.content)  # 回复内容
print(mcp_message.context)  # 上下文信息
print(mcp_message.metadata)  # 元数据
```

## 扩展指南

### 添加新工具

1. 在 `tool_caller.py` 中实现工具函数：

```python
async def _my_tool_impl(self, param1: str, param2: int) -> Dict:
    """工具实现"""
    # 实现逻辑
    return {"result": "success"}
```

2. 注册工具：

```python
self.registry.register(
    name="my_tool",
    description="工具描述",
    function=self._my_tool_impl,
    parameters={
        "param1": {"type": "string", "required": True},
        "param2": {"type": "int", "required": False, "default": 0}
    },
    category="custom"
)
```

### 自定义规划策略

在 `planner.py` 的 `_select_strategy()` 方法中添加：

```python
def _select_strategy(self, task_graph, context):
    # 添加自定义策略选择逻辑
    if custom_condition:
        return Strategy.CUSTOM_STRATEGY
    # ...
```

### 扩展记忆类型

在 `memory_hub.py` 中添加新的记忆类型：

```python
def _infer_memory_type(self, experience):
    # 添加新的记忆类型判断逻辑
    if new_condition:
        return "new_memory_type"
    # ...
```

## 性能优化

### 1. 缓存策略

- 用户画像缓存（1小时）
- 工作记忆缓存（会话期间）
- 工具结果缓存（5分钟）

### 2. 异步处理

所有I/O操作都使用异步：

```python
async def process(...):
    # 异步调用
    result = await tool_caller.call(...)
```

### 3. 批量处理

记忆检索和工具调用支持批量处理。

## 测试

### 运行测试

```bash
python test_agent.py
```

### 测试覆盖

- 单元测试：各模块独立测试
- 集成测试：模块间协作测试
- 端到端测试：完整流程测试

## 故障排除

### 常见问题

1. **导入错误**
   - 检查Python路径
   - 确认所有依赖已安装

2. **数据库连接失败**
   - 检查数据库配置
   - 确认数据库服务运行

3. **工具调用失败**
   - 检查工具参数
   - 查看工具实现

4. **记忆检索为空**
   - 检查向量数据库
   - 确认记忆已保存

## 未来规划

1. **多模态支持**: 图像、音频记忆
2. **强化学习**: 策略优化
3. **分布式部署**: 支持多实例
4. **可视化工具**: 记忆图谱、执行流程

## 参考

- [记忆系统架构](./记忆系统架构.md)
- [Agent README](../AGENT_README.md)
- [代码仓库](https://github.com/congde/emotional_chat)
