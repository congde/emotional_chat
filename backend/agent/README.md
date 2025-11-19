# Agent模块使用指南

## 概述

Agent模块提供完整的智能Agent功能，包括记忆管理、任务规划、工具调用和反思优化。

## 核心组件

### 1. Agent Core (agent_core.py)

Agent核心控制器，协调所有模块：

- **功能**: 整合Memory Hub、Planner、Tool Caller、Reflector
- **主要方法**:
  - `process()`: 处理用户输入（传统接口）
  - `process_with_mcp()`: 使用MCP协议处理（新接口）

### 2. Memory Hub (memory_hub.py)

记忆中枢，管理Agent的记忆系统：

- **功能**: 
  - 编码新经验为记忆
  - 检索相关记忆
  - 巩固工作记忆到长期记忆
  - 管理用户画像和行为日志

- **主要方法**:
  - `encode()`: 编码经验
  - `retrieve()`: 检索记忆
  - `consolidate()`: 巩固记忆
  - `get_user_profile()`: 获取用户画像

### 3. Planner (planner.py)

任务规划模块：

- **功能**:
  - 识别用户目标
  - 分解复杂任务
  - 选择执行策略
  - 生成执行计划

- **主要方法**:
  - `plan()`: 生成执行计划
  - `plan_with_mcp()`: 使用MCP协议规划

### 4. Tool Caller (tool_caller.py)

工具调用器：

- **功能**:
  - 注册和管理工具
  - 执行工具调用
  - 验证参数
  - 处理结果

- **主要方法**:
  - `call()`: 调用工具
  - `call_with_mcp()`: 使用MCP协议调用

### 5. Reflector (reflector.py)

反思模块：

- **功能**:
  - 评估交互效果
  - 分析成功/失败原因
  - 生成改进建议
  - 规划回访任务

- **主要方法**:
  - `evaluate()`: 评估交互
  - `plan_followup()`: 规划回访

## 工具 (tools/)

### calendar_api.py
日历服务，提供事件管理功能。

### audio_player.py
音频播放服务，提供冥想音频、白噪音等资源。

### psychology_db.py
心理资源数据库，提供文章、视频、练习等资源。

### scheduler_service.py
定时提醒服务，提供任务调度功能。

## 使用示例

### 基本使用

```python
from backend.agent import get_agent_core

agent = get_agent_core()
result = await agent.process(
    user_input="我最近心情很不好",
    user_id="user_123"
)
```

### 使用MCP协议

```python
agent = get_agent_core()
mcp_message = await agent.process_with_mcp(
    user_input="我最近心情很不好",
    user_id="user_123"
)
```

### 单独使用模块

```python
from backend.agent import get_memory_hub, get_tool_caller

# 使用记忆中枢
memory_hub = get_memory_hub()
memories = memory_hub.retrieve(query="睡眠", user_id="user_123")

# 使用工具调用器
tool_caller = get_tool_caller()
result = await tool_caller.call("search_memory", {"query": "睡眠", "user_id": "user_123"})
```

## 扩展

### 添加新工具

在 `tool_caller.py` 的 `_register_builtin_tools()` 方法中添加：

```python
self.registry.register(
    name="my_tool",
    description="工具描述",
    function=self._my_tool_impl,
    parameters={
        "param1": {"type": "string", "required": True}
    },
    category="custom"
)
```

### 自定义规划策略

在 `planner.py` 的 `_select_strategy()` 方法中添加新的策略选择逻辑。

## 注意事项

1. 所有模块都支持单例模式，使用 `get_*()` 函数获取实例
2. MCP协议是可选的，传统接口仍然可用
3. 工具调用是异步的，需要使用 `await`
4. 记忆巩固是自动的，但也可以手动调用
