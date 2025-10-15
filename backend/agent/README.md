# Agent模块使用指南

## 概述

Agent模块为心语机器人提供智能核心能力，实现从被动响应到主动服务的升级。

## 架构

```
agent/
├── agent_core.py       # Agent核心控制器
├── memory_hub.py       # 记忆中枢
├── planner.py          # 任务规划器
├── tool_caller.py      # 工具调用器
├── reflector.py        # 反思模块
└── tools/              # 外部工具
    ├── calendar_api.py
    ├── audio_player.py
    ├── psychology_db.py
    └── scheduler_service.py
```

## 核心模块

### 1. Agent Core

Agent核心控制器，协调所有模块工作。

```python
from backend.agent import AgentCore

agent = AgentCore()
result = await agent.process(
    user_input="我最近睡不好",
    user_id="user_123"
)

print(result["response"])  # Agent的回复
print(result["actions"])   # 执行的行动
```

### 2. Memory Hub

记忆中枢，管理用户的长短期记忆。

```python
from backend.agent import MemoryHub

memory_hub = MemoryHub()

# 检索记忆
memories = memory_hub.retrieve(
    query="睡眠问题",
    user_id="user_123",
    context={"emotion": "焦虑"}
)

# 获取用户画像
profile = memory_hub.get_user_profile("user_123")
```

### 3. Planner

任务规划器，分解目标并制定执行计划。

```python
from backend.agent import Planner

planner = Planner()

# 生成执行计划
plan = await planner.plan(
    user_input="我怎么能睡得更好？",
    context={"user_id": "user_123", "perception": {...}}
)

print(plan.strategy)  # 执行策略
print(plan.steps)     # 执行步骤
```

### 4. Tool Caller

工具调用器，管理和调用外部工具。

```python
from backend.agent import ToolCaller

tool_caller = ToolCaller()

# 调用工具
result = await tool_caller.call(
    "recommend_meditation",
    {"theme": "sleep", "duration": 15}
)

print(result["result"])  # 工具返回结果
```

### 5. Reflector

反思模块，评估效果并规划回访。

```python
from backend.agent import Reflector

reflector = Reflector()

# 评估交互
evaluation = await reflector.evaluate(interaction)

# 规划回访
followup = await reflector.plan_followup("user_123", {})
```

## API使用

### 1. Agent聊天

```bash
POST /agent/chat
Content-Type: application/json

{
  "user_id": "user_123",
  "message": "我最近睡不好，怎么办？"
}
```

**响应：**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "success": true,
    "response": "我理解你的困扰。睡眠问题确实很影响生活质量。让我帮你...",
    "emotion": "焦虑",
    "actions": [
      {
        "type": "tool_call",
        "tool": "recommend_meditation",
        "success": true
      }
    ],
    "followup_scheduled": true
  }
}
```

### 2. 获取Agent状态

```bash
GET /agent/status
```

### 3. 查看执行历史

```bash
GET /agent/history/user_123?limit=10
```

### 4. 获取记忆摘要

```bash
GET /agent/memory/user_123
```

### 5. 查看可用工具

```bash
GET /agent/tools
```

## 工具库

### 记忆工具

- `search_memory`: 搜索历史记忆
- `get_emotion_log`: 获取情绪日志

### 定时任务工具

- `set_reminder`: 设置提醒
- `check_calendar`: 查看日历

### 资源推荐工具

- `recommend_meditation`: 推荐冥想音频
- `recommend_resource`: 推荐心理资源

### 评估工具

- `psychological_assessment`: 触发心理评估

## 集成到现有系统

### 1. 在路由中使用

```python
# backend/routers/chat.py

from backend.services.agent_service import get_agent_service

@router.post("/chat/agent")
async def chat_with_agent(
    request: ChatRequest,
    agent_service = Depends(get_agent_service)
):
    result = await agent_service.process_message(
        user_id=request.user_id,
        message=request.message
    )
    return result
```

### 2. 在服务中使用

```python
# backend/services/chat_service.py

from backend.agent import get_agent_core

class ChatService:
    def __init__(self):
        self.agent = get_agent_core()
    
    async def chat(self, user_id, message):
        # 使用Agent处理
        result = await self.agent.process(
            user_input=message,
            user_id=user_id
        )
        return result
```

## 配置

### 启用/禁用Agent模式

在环境变量中配置：

```env
# config.env
ENABLE_AGENT=true
AGENT_MODE=smart  # smart/simple/hybrid
```

### 工具配置

```python
# 注册自定义工具
tool_caller = get_tool_caller()

tool_caller.registry.register(
    name="my_custom_tool",
    description="我的自定义工具",
    function=my_tool_function,
    parameters={...},
    category="custom"
)
```

## 性能优化

### 1. 缓存优化

```python
# 启用记忆缓存
memory_hub.enable_cache = True
```

### 2. 异步处理

```python
# 异步调用工具
import asyncio

tasks = [
    tool_caller.call("tool1", params1),
    tool_caller.call("tool2", params2)
]

results = await asyncio.gather(*tasks)
```

### 3. 批量操作

```python
# 批量检索记忆
memories = memory_hub.batch_retrieve(queries, user_id)
```

## 监控和日志

### 查看执行日志

```python
# 获取执行历史
history = agent.get_execution_history(user_id="user_123", limit=50)

# 分析性能
for record in history:
    print(f"响应时间: {record['response_time']}s")
    print(f"评估分数: {record['evaluation']['score']}")
```

### 获取性能摘要

```python
reflector = get_reflector()
summary = reflector.get_experience_summary(limit=100)

print(f"成功率: {summary['success_rate']}")
print(f"常见问题: {summary['common_issues']}")
```

## 故障排查

### 1. Agent响应慢

- 检查工具调用次数
- 优化记忆检索范围
- 启用缓存

### 2. 工具调用失败

- 检查工具参数
- 查看错误日志
- 验证工具权限

### 3. 回访未触发

- 检查reflector配置
- 验证时间计算逻辑
- 查看调度服务状态

## 扩展开发

### 添加新工具

```python
# 1. 实现工具函数
async def my_new_tool(param1: str, param2: int) -> dict:
    # 工具逻辑
    return {"result": "..."}

# 2. 注册工具
tool_caller.registry.register(
    name="my_new_tool",
    description="新工具的描述",
    function=my_new_tool,
    parameters={
        "param1": {"type": "string", "required": True},
        "param2": {"type": "int", "required": False, "default": 10}
    },
    category="custom"
)
```

### 自定义规划策略

```python
# 继承Planner并覆盖方法
class CustomPlanner(Planner):
    def _select_strategy(self, task_graph, context):
        # 自定义策略选择逻辑
        return Strategy.CUSTOM
```

## 测试

### 单元测试

```python
# tests/test_agent.py

import pytest
from backend.agent import AgentCore

@pytest.mark.asyncio
async def test_agent_process():
    agent = AgentCore()
    result = await agent.process(
        user_input="测试消息",
        user_id="test_user"
    )
    
    assert result["success"] == True
    assert "response" in result
```

### 集成测试

```bash
# 运行测试
pytest tests/test_agent.py -v
```

## 最佳实践

1. **渐进式采用**：先在部分功能中试用Agent模式
2. **降级策略**：准备非Agent模式的后备方案
3. **监控指标**：持续监控响应时间和成功率
4. **用户反馈**：收集用户对Agent交互的反馈
5. **定期优化**：根据反思模块的分析结果优化策略

## 版本历史

- v1.0.0 (2025-10-15): 初始版本
  - 实现核心Agent架构
  - 提供基础工具集
  - 集成到现有系统

## 联系支持

如有问题，请联系开发团队或查看在线文档。

