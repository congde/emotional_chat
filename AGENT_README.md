# Agent模块快速开始指南

## 概述

Agent模块是情感聊天系统的智能核心，提供完整的Agent功能，包括记忆管理、任务规划、工具调用和反思优化。

## 目录结构

```
backend/agent/
├── agent_core.py          # Agent核心控制器
├── memory_hub.py          # 记忆中枢
├── planner.py             # 规划模块
├── tool_caller.py         # 工具调用器
├── reflector.py           # 反思模块
├── README.md              # 使用指南
└── tools/                 # 外部工具
    ├── calendar_api.py
    ├── audio_player.py
    ├── psychology_db.py
    └── scheduler_service.py

backend/routers/
└── agent.py               # Agent路由

backend/services/
└── agent_service.py       # Agent服务
```

## 快速开始

### 1. 基本使用

```python
import asyncio
from backend.agent import get_agent_core

async def main():
    # 获取Agent实例
    agent = get_agent_core()
    
    # 处理用户消息
    result = await agent.process(
        user_input="我最近心情很不好，感觉很焦虑",
        user_id="user_123"
    )
    
    print(f"回复: {result['response']}")
    print(f"情绪: {result['emotion']}")

asyncio.run(main())
```

### 2. 运行演示

```bash
# 运行演示脚本
python demo_agent.py
```

### 3. 运行测试

```bash
# 运行测试脚本
python test_agent.py
```

## API接口

### 聊天接口

```bash
POST /agent/chat
{
    "user_id": "user_123",
    "message": "我最近心情很不好",
    "conversation_id": "session_123"  # 可选
}
```

### 获取状态

```bash
GET /agent/status
```

### 获取执行历史

```bash
GET /agent/history/{user_id}?limit=10
```

### 获取记忆摘要

```bash
GET /agent/memory/{user_id}
```

### 获取可用工具

```bash
GET /agent/tools
```

## 核心模块

### Agent Core

Agent核心控制器，协调所有模块：

```python
from backend.agent import AgentCore

agent = AgentCore()
result = await agent.process(user_input, user_id)
```

### Memory Hub

记忆中枢，管理短期和长期记忆：

```python
from backend.agent import get_memory_hub

memory_hub = get_memory_hub()
memories = memory_hub.retrieve(query="睡眠", user_id="user_123", top_k=5)
```

### Planner

任务规划模块，生成执行计划：

```python
from backend.agent import Planner

planner = Planner()
plan = await planner.plan(user_input, context)
```

### Tool Caller

工具调用器，执行外部工具：

```python
from backend.agent import get_tool_caller

tool_caller = get_tool_caller()
result = await tool_caller.call("search_memory", {"query": "睡眠", "user_id": "user_123"})
```

### Reflector

反思模块，评估和优化：

```python
from backend.agent import get_reflector

reflector = get_reflector()
evaluation = await reflector.evaluate(interaction)
```

## 工具列表

Agent支持以下工具：

- **记忆相关**
  - `search_memory`: 搜索用户历史记忆
  - `get_emotion_log`: 获取情绪日志

- **定时任务**
  - `set_reminder`: 设置提醒

- **资源推荐**
  - `recommend_meditation`: 推荐冥想音频
  - `recommend_resource`: 推荐心理健康资源

- **评估工具**
  - `psychological_assessment`: 心理健康评估

- **日历工具**
  - `check_calendar`: 查看日历事件

## 配置

Agent模块使用系统默认配置，可以通过环境变量调整：

- `DATABASE_URL`: 数据库连接
- `VECTOR_STORE_PATH`: 向量数据库路径

## 故障排除

### 常见问题

1. **导入错误**
   - 确保项目根目录在Python路径中
   - 检查所有依赖是否已安装

2. **数据库连接失败**
   - 检查数据库配置
   - 确保数据库服务正在运行

3. **工具调用失败**
   - 检查工具参数是否正确
   - 查看工具实现是否完整

## 更多信息

- 详细文档: `docs/Agent核心模块实现总结.md`
- 架构说明: `docs/记忆系统架构.md`

## 许可证

MIT License

