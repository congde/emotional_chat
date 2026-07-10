# MCP 上下文处理集成说明

## 概述

MCP (Model Context Protocol) 协议现已集成上下文处理功能（CPM - Context Processing Module），可以自动从 `ContextService` 获取并填充上下文信息。

## 功能特性

1. **自动上下文填充**：创建 MCP 消息时，可以自动从上下文服务获取用户画像、记忆、情绪状态等信息
2. **向后兼容**：保留了原有的静态方法，不影响现有代码
3. **灵活配置**：可以选择使用自动填充或手动提供上下文

## 使用方法

### 1. 创建带上下文服务的 MCP 协议处理器

```python
from backend.modules.agent.protocol.mcp import create_mcp_protocol_with_context

# 方式1：自动创建上下文服务
protocol = create_mcp_protocol_with_context()

# 方式2：使用自定义上下文服务
from backend.services.context_service import ContextService
context_service = ContextService()
protocol = create_mcp_protocol_with_context(context_service)

# 方式3：直接实例化
from backend.modules.agent.protocol.mcp import MCPProtocol
protocol = MCPProtocol()  # 会自动尝试创建 ContextService
```

### 2. 创建带自动上下文填充的用户输入消息

```python
# 异步方法，需要 await
user_msg = await protocol.create_user_input_with_context(
    content="我最近心情很不好，感觉很焦虑",
    user_id="user_123",
    session_id="session_456",
    emotion="焦虑",
    emotion_intensity=7.5
)

# 返回的 MCPMessage 会自动包含：
# - user_profile: 从 ContextService 获取的用户画像
# - emotion_state: 当前情绪状态和趋势
# - memory_summary: 相关记忆摘要
# - conversation_history: 对话历史
```

### 3. 手动覆盖自动填充的上下文

```python
# 如果提供了显式参数，会优先使用显式参数
user_msg = await protocol.create_user_input_with_context(
    content="我最近心情很不好",
    user_id="user_123",
    session_id="session_456",
    # 以下参数会覆盖自动填充的内容
    user_profile={"name": "张三", "age": 25},
    emotion_state={"emotion": "焦虑", "intensity": 8.0}
)
```

### 4. 使用静态方法（不自动填充上下文）

```python
# 原有的静态方法仍然可用，不自动填充上下文
from backend.modules.agent.protocol.mcp import MCPProtocol

user_msg = MCPProtocol.create_user_input(
    content="我最近心情很不好",
    emotion_state={"emotion": "焦虑", "intensity": 7.5}
)
```

## 上下文数据结构

自动填充的上下文包含以下信息：

```python
{
    "user_profile": {
        "user_id": "user_123",
        "name": "张三",
        "age": 25,
        "personality_traits": ["内向", "敏感"],
        "interests": ["阅读", "音乐"],
        "concerns": ["工作压力", "人际关系"],
        "communication_style": "默认",
        "emotional_baseline": "稳定"
    },
    "emotion_state": {
        "emotion": "焦虑",
        "intensity": 7.5,
        "trend": {
            "trend": "上升",
            "emotions": [
                {"emotion": "焦虑", "count": 5},
                {"emotion": "压力", "count": 3}
            ]
        }
    },
    "memory_summary": {
        "recent_events": [...],
        "concerns": [...],
        "relationships": [...],
        "count": 5
    },
    "conversation_history": [
        {"role": "user", "content": "...", "emotion": "焦虑"},
        {"role": "assistant", "content": "..."}
    ]
}
```

## 集成到 Agent Core

在 Agent Core 中使用带上下文填充的 MCP 协议：

```python
from backend.modules.agent.protocol.mcp import create_mcp_protocol_with_context

class AgentCore:
    def __init__(self):
        # 创建带上下文服务的 MCP 协议处理器
        self.mcp_protocol = create_mcp_protocol_with_context()
    
    async def process_with_mcp(self, user_input: str, user_id: str, session_id: str):
        # 自动填充上下文
        mcp_message = await self.mcp_protocol.create_user_input_with_context(
            content=user_input,
            user_id=user_id,
            session_id=session_id
        )
        
        # 处理消息...
        return mcp_message
```

## 错误处理

如果上下文服务不可用或调用失败：

1. **自动降级**：如果 `ContextService` 无法创建或调用失败，会返回空的 `MCPContext`，不会抛出异常
2. **日志记录**：错误信息会打印到控制台（可以通过日志系统配置）
3. **向后兼容**：如果上下文服务不可用，可以继续使用静态方法手动提供上下文

## 注意事项

1. **异步方法**：`create_user_input_with_context` 是异步方法，必须在 `async` 函数中使用 `await`
2. **性能考虑**：自动上下文填充会调用数据库和向量数据库，可能有一定延迟
3. **缓存机制**：`ContextService` 内部有缓存机制，相同用户的多次调用会复用缓存
4. **可选依赖**：如果 `ContextService` 不可用，代码会自动降级，不会影响基本功能

## 相关文件

- 核心实现：`backend/modules/agent/protocol/mcp.py`
- 上下文服务：`backend/services/context_service.py`
- 上下文组装器：`backend/context_assembler.py`
- 增强版上下文组装器：`backend/services/enhanced_context_assembler.py`

## 未来扩展

1. 支持 `EnhancedContextAssembler`（更高级的上下文处理）
2. 支持自定义上下文处理策略
3. 支持上下文缓存和预加载
4. 支持批量上下文填充

