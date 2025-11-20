# 📡 API接口完整文档

本文档提供了心语情感陪伴机器人的完整API接口说明。

> **提示**: 交互式API文档可通过访问 `http://localhost:8000/docs` 查看（Swagger UI）

## 目录

- [系统信息接口](#系统信息接口)
- [聊天接口](#聊天接口)
- [会话管理](#会话管理)
- [用户情感分析](#用户情感分析)
- [RAG知识库](#rag知识库)
- [Agent智能核心](#agent智能核心)
- [记忆管理](#记忆管理)
- [反馈系统](#反馈系统)

---

## 系统信息接口

### 1. 根路径和系统信息

获取系统基本信息和功能列表。

```http
GET /
```

**响应示例:**
```json
{
  "name": "心语情感陪伴机器人",
  "version": "3.0.0",
  "status": "running",
  "features": [
    "情感分析",
    "记忆系统",
    "上下文管理",
    "向量数据库",
    "LangChain集成",
    "自动评估",
    "RAG知识库",
    "Agent智能核心"
  ],
  "architecture": "分层服务架构 + Agent核心",
  "agent_enabled": true
}
```

### 2. 健康检查

检查系统健康状态和各个组件的连接状态。

```http
GET /health
```

**响应示例:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-16T10:00:00.000000",
  "version": "3.0.0",
  "database": "connected",
  "vector_db": "ready",
  "memory_system": "enabled"
}
```

### 3. 系统架构信息

获取详细的系统架构信息。

```http
GET /system/info
```

**响应示例:**
```json
{
  "architecture": {
    "pattern": "分层服务架构 + Agent核心",
    "layers": ["路由层", "服务层", "核心层", "数据层"],
    "services": ["ChatService", "MemoryService", "ContextService", "AgentService"],
    "routers": ["chat", "memory", "feedback", "evaluation", "agent"]
  },
  "memory_system": {
    "enabled": true,
    "components": ["记忆提取器", "记忆管理器", "上下文组装器"],
    "storage": ["向量数据库 (ChromaDB)", "关系数据库 (MySQL)"]
  },
  "agent_system": {
    "enabled": true,
    "components": [
      "Agent Core - 核心控制器",
      "Memory Hub - 记忆中枢",
      "Planner - 任务规划器",
      "Tool Caller - 工具调用器",
      "Reflector - 反思优化器"
    ]
  }
}
```

---

## 聊天接口

### 4. 普通聊天接口

基础的聊天接口，支持情感分析和上下文理解。

```http
POST /chat
Content-Type: application/json

{
  "message": "你好，我今天心情很好！",
  "user_id": "test_user",
  "session_id": "optional-session-id"
}
```

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| message | string | 是 | 用户消息内容 |
| user_id | string | 否 | 用户ID，用于记忆管理 |
| session_id | string | 否 | 会话ID，不提供则自动创建 |

**响应示例:**
```json
{
  "response": "你好，听到你今天心情很好，真是太棒了！😊",
  "session_id": "0ccdde5c-8592-4e23-893a-8e1a8d8bbaf7",
  "emotion": "happy",
  "emotion_intensity": 8.5,
  "suggestions": [
    "很高兴看到你这么开心！",
    "有什么特别的事情想要分享吗？"
  ],
  "timestamp": "2025-10-10T16:57:50.584646"
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| response | string | AI回复内容 |
| session_id | string | 会话ID |
| emotion | string | 识别的情感类型 |
| emotion_intensity | float | 情感强度（0-10） |
| suggestions | array | 建议回复列表 |
| timestamp | string | 响应时间戳 |

---

## Agent智能核心

### 5. Agent聊天接口（智能模式）

使用Agent智能核心的增强聊天接口，支持任务规划、工具调用和主动服务。

```http
POST /agent/chat
Content-Type: application/json

{
  "user_id": "user_123",
  "message": "我最近睡不好，怎么办？"
}
```

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | string | 是 | 用户ID |
| message | string | 是 | 用户消息 |
| session_id | string | 否 | 会话ID |

**响应示例:**
```json
{
  "code": 200,
  "data": {
    "success": true,
    "response": "我理解你的困扰。睡眠问题确实很影响生活质量。我为你准备了几个科学有效的改善方法...",
    "emotion": "焦虑",
    "emotion_intensity": 7.5,
    "actions": [
      {
        "type": "tool_call",
        "tool": "recommend_meditation",
        "success": true,
        "result": "已推荐3个助眠冥想音频"
      },
      {
        "type": "rag_retrieval",
        "success": true,
        "result": "检索到5条相关睡眠改善知识"
      }
    ],
    "followup_scheduled": true,
    "response_time": 1.2
  }
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | 请求是否成功 |
| response | string | AI回复内容 |
| emotion | string | 识别的情感类型 |
| emotion_intensity | float | 情感强度 |
| actions | array | Agent执行的动作列表 |
| followup_scheduled | boolean | 是否安排了后续回访 |
| response_time | float | 响应时间（秒） |

### 6. 获取Agent可用工具列表

获取Agent系统可用的所有工具列表。

```http
GET /agent/tools
```

**响应示例:**
```json
{
  "tools": [
    {
      "name": "search_memory",
      "description": "检索用户历史记忆",
      "category": "memory",
      "parameters": {
        "query": "string",
        "top_k": "int"
      }
    },
    {
      "name": "recommend_meditation",
      "description": "推荐冥想音频",
      "category": "resource",
      "parameters": {
        "emotion": "string",
        "duration": "int"
      }
    },
    {
      "name": "set_reminder",
      "description": "设置提醒",
      "category": "scheduler",
      "parameters": {
        "message": "string",
        "time": "datetime"
      }
    }
  ]
}
```

---

## 会话管理

### 7. 获取会话历史

获取指定会话的对话历史记录。

```http
GET /sessions/{session_id}/history?limit=20
```

**路径参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| session_id | string | 会话ID |

**查询参数:**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| limit | int | 20 | 返回的消息数量限制 |

**响应示例:**
```json
{
  "session_id": "0ccdde5c-8592-4e23-893a-8e1a8d8bbaf7",
  "messages": [
    {
      "role": "user",
      "content": "你好，我今天心情很好！",
      "emotion": "happy",
      "emotion_intensity": 8,
      "timestamp": "2025-10-10T16:57:50.000000"
    },
    {
      "role": "assistant",
      "content": "你好，听到你今天心情很好，真是太棒了！😊",
      "emotion": "empathetic",
      "timestamp": "2025-10-10T16:57:52.000000"
    }
  ],
  "total": 10,
  "has_more": false
}
```

### 8. 获取会话摘要

获取会话的统计摘要信息。

```http
GET /sessions/{session_id}/summary
```

**响应示例:**
```json
{
  "session_id": "0ccdde5c-8592-4e23-893a-8e1a8d8bbaf7",
  "message_count": 10,
  "emotion_distribution": {
    "happy": 5,
    "neutral": 3,
    "anxious": 2
  },
  "average_intensity": 6.5,
  "created_at": "2025-10-10T16:57:50.000000",
  "updated_at": "2025-10-10T17:05:20.000000"
}
```

---

## 用户情感分析

### 9. 获取用户情感趋势

获取用户的情感变化趋势和统计数据。

```http
GET /users/{user_id}/emotion-trends
```

**路径参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| user_id | string | 用户ID |

**查询参数:**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| days | int | 30 | 统计天数 |
| limit | int | 100 | 返回记录数限制 |

**响应示例:**
```json
{
  "user_id": "test_user",
  "total_records": 50,
  "period": {
    "start": "2025-09-16T00:00:00.000000",
    "end": "2025-10-16T23:59:59.000000"
  },
  "recent_emotions": ["happy", "neutral", "anxious"],
  "average_intensity": 6.5,
  "emotion_counts": {
    "happy": 20,
    "neutral": 15,
    "anxious": 10,
    "sad": 5
  },
  "trend": "improving"
}
```

---

## RAG知识库

### 10. RAG知识库检索

在知识库中检索相关信息。

```http
POST /rag/search
Content-Type: application/json

{
  "query": "如何改善睡眠质量？",
  "top_k": 3
}
```

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| query | string | 是 | 检索查询内容 |
| top_k | int | 否 | 返回结果数量，默认3 |

**响应示例:**
```json
{
  "query": "如何改善睡眠质量？",
  "results": [
    {
      "content": "睡眠卫生的重要性：保持规律的作息时间，睡前避免使用电子设备...",
      "category": "睡眠改善",
      "relevance_score": 0.92,
      "metadata": {
        "source": "心理健康知识库",
        "topic": "睡眠管理",
        "created_at": "2025-10-01T00:00:00.000000"
      }
    },
    {
      "content": "正念冥想可以帮助改善睡眠质量...",
      "category": "正念减压",
      "relevance_score": 0.85,
      "metadata": {
        "source": "心理健康知识库",
        "topic": "冥想技巧"
      }
    }
  ],
  "total_found": 5
}
```

### 11. RAG知识库状态

获取知识库的状态信息。

```http
GET /rag/status
```

**响应示例:**
```json
{
  "status": "ready",
  "total_documents": 50,
  "categories": [
    "认知行为疗法",
    "正念减压",
    "积极心理学",
    "焦虑应对",
    "睡眠改善",
    "情绪调节"
  ],
  "last_updated": "2025-10-16T09:00:00.000000",
  "storage": {
    "type": "ChromaDB",
    "collection": "mental_health_kb"
  }
}
```

---

## 记忆管理

### 12. 获取用户记忆

检索用户的长期记忆信息。

```http
GET /memory/{user_id}?query=工作压力&top_k=5
```

**路径参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| user_id | string | 用户ID |

**查询参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| query | string | 检索关键词（可选） |
| top_k | int | 返回数量，默认5 |

**响应示例:**
```json
{
  "user_id": "test_user",
  "memories": [
    {
      "content": "用户提到工作压力大，经常加班",
      "type": "emotion",
      "relevance_score": 0.95,
      "created_at": "2025-10-10T10:00:00.000000"
    }
  ],
  "total": 10
}
```

---

## 反馈系统

### 13. 提交用户反馈

提交对AI回复的反馈。

```http
POST /feedback
Content-Type: application/json

{
  "session_id": "session_123",
  "message_id": 456,
  "rating": 5,
  "comment": "回复很温暖，很有帮助"
}
```

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| session_id | string | 是 | 会话ID |
| message_id | int | 否 | 消息ID |
| rating | int | 否 | 评分（1-5） |
| comment | string | 否 | 文字反馈 |
| feedback_type | string | 否 | 反馈类型（positive/negative） |

**响应示例:**
```json
{
  "success": true,
  "message": "反馈已记录",
  "feedback_id": 789
}
```

---

## 错误处理

所有API接口遵循统一的错误响应格式：

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": {}
  }
}
```

**常见错误码:**

| 错误码 | HTTP状态码 | 说明 |
|--------|-----------|------|
| INVALID_REQUEST | 400 | 请求参数错误 |
| UNAUTHORIZED | 401 | 未授权 |
| NOT_FOUND | 404 | 资源不存在 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |
| DATABASE_ERROR | 500 | 数据库错误 |
| LLM_ERROR | 500 | 大模型调用错误 |

---

## 交互式API文档

访问 `http://localhost:8000/docs` 查看完整的Swagger UI交互式文档，支持：
- 在线测试API接口
- 查看请求/响应示例
- 下载OpenAPI规范文件

---

## 相关文档

- [系统架构详解](系统架构详解.md)
- [Agent模块文档](../AGENT_README.md)
- [RAG系统文档](RAG实施步骤.md)
- [记忆系统文档](记忆系统架构.md)



