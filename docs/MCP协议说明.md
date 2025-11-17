# MCP (Model Context Protocol) 协议说明

## 概述

MCP（Model Context Protocol，模型上下文协议）是一种专为大模型智能体设计的结构化通信协议。通过MCP，Agent系统的各个模块（Planner、Tool Caller、Reflector等）可以实现标准化、低耦合、高内聚的协作。

## 核心优势

1. **标准化通信**：所有模块遵循同一协议，降低集成复杂度
2. **上下文完整**：结构化上下文确保信息不丢失
3. **可追溯性**：完整的交互链记录，支持调试和重放
4. **可扩展性**：易于添加新模块和功能
5. **多智能体支持**：为未来多智能体协作奠定基础

## 协议结构

MCP消息采用JSON格式，包含以下核心要素：

```json
{
    "message_id": "唯一消息ID",
    "message_type": "消息类型（user_input/planner_output/tool_response等）",
    "content": "自然语言内容",
    "context": {
        "user_profile": {},
        "emotion_state": {},
        "task_goal": {},
        "memory_summary": {},
        "conversation_history": []
    },
    "tool_calls": [],
    "tool_responses": [],
    "timestamp": "时间戳",
    "source_module": "来源模块",
    "target_module": "目标模块",
    "metadata": {}
}
```

## 消息类型

- `user_input`: 用户输入
- `planner_output`: Planner规划输出
- `tool_request`: 工具请求
- `tool_response`: 工具响应
- `agent_response`: Agent回复
- `reflector_evaluation`: Reflector评估结果
- `internal_communication`: 内部通信

## 使用示例

### 1. 基本使用

```python
from backend.modules.agent.protocol.mcp import MCPProtocol, get_mcp_logger

# 创建协议处理器
protocol = MCPProtocol()
logger = get_mcp_logger()

# 创建用户输入消息
user_msg = protocol.create_user_input(
    content="我最近心情很不好，感觉很焦虑",
    emotion_state={"emotion": "焦虑", "intensity": 7.5}
)

# 记录消息
logger.log(user_msg)
```

### 2. 在Agent Core中使用

```python
from backend.modules.agent.core.agent.agent_core import AgentCore

# 创建Agent Core
agent = AgentCore()

# 使用MCP协议处理用户输入
mcp_response = await agent.process_with_mcp(
    user_input="我最近睡不好，怎么办？",
    user_id="user_123"
)

# 获取回复内容
response_content = mcp_response.content
```

### 3. 模块间通信流程

```
用户输入
    ↓
Agent Core (创建user_input MCP消息)
    ↓
Planner (接收MCP消息，输出plan_with_mcp)
    ↓
Tool Caller (接收MCP消息，执行工具，输出tool_response)
    ↓
Agent Core (生成回复，创建agent_response MCP消息)
    ↓
Reflector (接收MCP消息，评估，输出evaluation MCP消息)
    ↓
返回最终回复
```

## 模块集成

### Planner模块

```python
# 传统接口（保持兼容）
plan = await planner.plan(user_input, context)

# MCP接口（新接口）
mcp_message = await planner.plan_with_mcp(mcp_input_message)
```

### Tool Caller模块

```python
# 传统接口
result = await tool_caller.call("search_memory", {"query": "..."})

# MCP接口
mcp_response = await tool_caller.call_with_mcp(mcp_request_message)
```

### Reflector模块

```python
# 传统接口
evaluation = await reflector.evaluate(interaction)

# MCP接口
mcp_evaluation = await reflector.evaluate_with_mcp(mcp_message)
```

## 日志和可追溯性

MCP协议自动记录所有消息，支持：

1. **完整交互链追踪**：通过`interaction_id`追踪完整交互流程
2. **消息查询**：按类型、模块、时间等条件查询
3. **日志导出**：导出为JSON格式，支持重放和分析

```python
# 获取交互链
trace = logger.get_interaction_trace(interaction_id)

# 查询特定类型的消息
planner_messages = logger.get_logs(
    message_type=MCPMessageType.PLANNER_OUTPUT,
    limit=10
)

# 导出日志
logger.export_logs("mcp_logs.json")
```

## 最佳实践

1. **始终使用MCP协议**：新代码优先使用MCP接口
2. **保持上下文完整**：在传递MCP消息时，尽量保留和合并上下文
3. **记录关键消息**：所有MCP消息会自动记录，无需手动记录
4. **错误处理**：使用MCP消息的错误字段传递错误信息
5. **元数据利用**：使用metadata字段传递额外的业务信息

## 未来扩展

MCP协议为以下功能奠定基础：

1. **多智能体协作**：不同Agent之间可以通过MCP协议通信
2. **跨平台部署**：MCP消息可以跨网络传输，支持分布式部署
3. **可观测性**：完整的日志支持监控和分析
4. **A/B测试**：可以重放历史交互，进行策略对比
5. **调试工具**：可视化交互流程，快速定位问题

## 相关文件

- 核心实现：`backend/modules/agent/protocol/mcp.py`
- Planner集成：`backend/modules/agent/core/agent/planner.py`
- Tool Caller集成：`backend/modules/agent/core/agent/tool_caller.py`
- Reflector集成：`backend/modules/agent/core/agent/reflector.py`
- Agent Core集成：`backend/modules/agent/core/agent/agent_core.py`

