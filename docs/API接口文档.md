# 📡 API接口完整文档

本文档提供了心语情感陪伴机器人的完整API接口说明。

> **提示**: 交互式API文档可通过访问 `http://localhost:8000/docs` 查看（Swagger UI）

## 目录

- [系统信息接口](#系统信息接口)
- [聊天接口](#聊天接口)
- [增强版聊天](#增强版聊天)
- [流式聊天](#流式聊天)
- [会话管理](#会话管理)
- [用户情感分析](#用户情感分析)
- [RAG知识库](#rag知识库)
- [Agent智能核心](#agent智能核心)
- [意图识别](#意图识别)
- [记忆管理](#记忆管理)
- [反馈系统](#反馈系统)
- [评估系统](#评估系统)
- [个性化配置](#个性化配置)
- [性能监控](#性能监控)
- [A/B测试](#ab测试)

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

### 4.1 简单聊天接口（无记忆系统）

不使用记忆系统的简单聊天接口，用于对比测试。

```http
POST /chat/simple
Content-Type: application/json

{
  "message": "你好",
  "user_id": "test_user"
}
```

### 4.2 带附件的聊天接口

支持文件上传和URL内容的聊天接口。

```http
POST /chat/with-attachments
Content-Type: multipart/form-data

message: "请帮我分析这个文档"
user_id: "test_user"
session_id: "optional-session-id"
files: [文件1, 文件2...]
url_contents: "[{\"url\": \"https://example.com\", \"title\": \"标题\", \"content\": \"内容\"}]"
```

**支持的文件类型:**
- 图片: `.jpg`, `.jpeg`, `.png`, `.gif`
- 文档: `.pdf`, `.txt`, `.doc`, `.docx`

**文件限制:**
- 最大文件大小: 10MB
- 支持多文件上传

### 4.3 URL解析接口

解析URL内容并提取文本。

```http
POST /chat/parse-url
Content-Type: application/json

{
  "url": "https://example.com/article"
}
```

**响应示例:**
```json
{
  "url": "https://example.com/article",
  "title": "文章标题",
  "content": "文章内容...",
  "status": "success"
}
```

---

## Agent智能核心

### 5. Agent聊天接口（智能模式）

使用Agent智能核心的增强聊天接口，支持任务规划、工具调用和主动服务。

```http
POST /agent/chat
Content-Type: application/json

{
  "user_id": "user_123",
  "message": "我最近睡不好，怎么办？",
  "conversation_id": "optional-conversation-id"
}
```

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | string | 是 | 用户ID |
| message | string | 是 | 用户消息 |
| conversation_id | string | 否 | 会话ID |

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
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

### 5.1 获取Agent状态

获取Agent各模块的运行状态和统计信息。

```http
GET /agent/status
```

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "status": "running",
    "components": {
      "agent_core": "active",
      "memory_hub": "active",
      "planner": "active",
      "tool_caller": "active",
      "reflector": "active"
    },
    "statistics": {
      "total_conversations": 150,
      "total_tool_calls": 320,
      "average_response_time": 1.2
    }
  }
}
```

### 5.2 获取Agent可用工具列表

获取Agent系统可用的所有工具列表。

```http
GET /agent/tools
```

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
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
}
```

### 5.3 获取用户执行历史

查看用户与Agent的交互记录。

```http
GET /agent/history/{user_id}?limit=10
```

**查询参数:**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| limit | int | 10 | 返回记录数限制 |

### 5.4 获取用户记忆摘要

查看用户画像、工作记忆、行为日志等。

```http
GET /agent/memory/{user_id}
```

### 5.5 规划回访任务

为用户创建回访计划。

```http
POST /agent/followup
Content-Type: application/json

{
  "user_id": "user_123"
}
```

### 5.6 Agent健康检查

检查Agent服务是否正常运行。

```http
GET /agent/health
```

---

## 会话管理

### 7. 获取会话历史

获取指定会话的对话历史记录。

```http
GET /chat/sessions/{session_id}/history?limit=20
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
GET /chat/sessions/{session_id}/summary
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

### 8.1 获取用户所有会话

获取指定用户的所有会话列表。

```http
GET /chat/users/{user_id}/sessions?limit=50
```

**查询参数:**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| limit | int | 50 | 返回的会话数量限制 |

### 8.2 搜索用户会话

根据关键词搜索用户的会话。

```http
GET /chat/users/{user_id}/sessions/search?keyword=关键词&limit=50
```

**查询参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| keyword | string | 搜索关键词 |
| limit | int | 返回数量限制 |

### 8.3 删除会话

删除指定的会话。

```http
DELETE /chat/sessions/{session_id}
```

### 8.4 批量删除会话

批量删除多个会话。

```http
POST /chat/sessions/batch-delete
Content-Type: application/json

["session_id_1", "session_id_2", "session_id_3"]
```

---

## 用户情感分析

### 9. 情感分析接口

分析文本的情感。

```http
POST /api/emotion/analyze
Content-Type: application/json

{
  "text": "今天好累啊，工作压力太大了",
  "user_id": "user_123"
}
```

**响应示例:**
```json
{
  "emotion": "anxious",
  "confidence": 0.85,
  "intensity": 7.5,
  "polarity": -1,
  "emotion_scores": {
    "anxious": 0.85,
    "sad": 0.10,
    "neutral": 0.05
  },
  "keywords": ["累", "压力"],
  "suggestions": ["我理解你的压力...", "可以尝试放松..."],
  "method": "keywords"
}
```

### 9.1 快速情感分析

简化的快速分析接口。

```http
POST /api/emotion/quick_analyze?text=今天好开心
```

### 9.2 获取用户情感趋势

获取用户的情感变化趋势。

```http
GET /api/emotion/trend/{user_id}?window=10
```

**查询参数:**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| window | int | 10 | 分析窗口大小（最近N条消息） |

**响应示例:**
```json
{
  "trend": "improving",
  "average_intensity": 6.5,
  "dominant_emotion": "happy",
  "emotion_distribution": {
    "happy": 0.4,
    "neutral": 0.3,
    "anxious": 0.3
  },
  "warning": null,
  "sample_size": 10
}
```

### 9.3 生成用户情绪报告

生成完整的用户情绪报告。

```http
GET /api/emotion/report/{user_id}?days=7&include_visualization=true
```

**查询参数:**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| days | int | 7 | 分析天数（1-90） |
| include_visualization | bool | true | 是否包含可视化数据 |

### 9.4 获取用户情绪画像

获取多维度情绪画像。

```http
GET /api/emotion/profile/{user_id}?days=30
```

**响应示例:**
```json
{
  "user_id": "user_123",
  "analysis_period_days": 30,
  "sample_size": 45,
  "dimensions": {
    "stability": {"score": 0.65, "level": "中"},
    "complexity": {"score": 0.60, "unique_emotions": 6},
    "positivity": {"score": 0.35, "level": "中"},
    "stress": {"score": 0.45, "level": "高"},
    "social_connectedness": {"score": 0.55, "level": "中"},
    "resilience": {"score": 0.70, "level": "高"}
  },
  "overall_wellbeing_score": 0.58
}
```

### 9.5 获取用户情感趋势（聊天接口）

通过聊天接口获取用户情感趋势。

```http
GET /chat/users/{user_id}/emotion-trends
```

---

## RAG知识库

### 10. 获取知识库状态

获取知识库的状态信息。

```http
GET /api/rag/status
```

**响应示例:**
```json
{
  "success": true,
  "data": {
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
}
```

### 10.1 初始化示例知识库

加载内置的心理健康知识到向量数据库。

```http
POST /api/rag/init/sample
Content-Type: application/json

{
  "overwrite": false
}
```

**请求参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| overwrite | bool | 是否覆盖现有知识库 |

### 10.2 从知识库结构初始化

从 `knowledge_base` 目录加载分类知识文档。

```http
POST /api/rag/init/knowledge-base
Content-Type: application/json

{
  "overwrite": false
}
```

### 10.3 上传PDF文档

上传PDF文档到知识库。

```http
POST /api/rag/upload/pdf
Content-Type: multipart/form-data

file: [PDF文件]
```

### 10.4 向知识库提问

基于知识库内容生成专业的心理健康建议。

```http
POST /api/rag/ask
Content-Type: application/json

{
  "question": "我最近总是失眠，怎么办？",
  "search_k": 3
}
```

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| question | string | 是 | 问题内容 |
| search_k | int | 否 | 检索数量，默认3 |

**响应示例:**
```json
{
  "success": true,
  "data": {
    "answer": "针对失眠问题，建议您...",
    "knowledge_count": 3,
    "sources": [
      {
        "content": "睡眠卫生的重要性...",
        "relevance_score": 0.92,
        "metadata": {
          "source": "心理健康知识库",
          "topic": "睡眠管理"
        }
      }
    ]
  }
}
```

### 10.5 带上下文的问答

结合对话历史和用户情绪生成个性化回答。

```http
POST /api/rag/ask/context
Content-Type: application/json

{
  "question": "有什么具体的方法可以帮助我入睡吗？",
  "conversation_history": [
    {"role": "user", "content": "我最近压力很大"},
    {"role": "assistant", "content": "我理解你现在的压力..."}
  ],
  "user_emotion": "焦虑",
  "search_k": 3
}
```

### 10.6 搜索知识库

只返回相关知识片段，不生成回答。

```http
POST /api/rag/search
Content-Type: application/json

{
  "query": "焦虑应对方法",
  "k": 3
}
```

### 10.7 重置知识库

删除所有向量数据（谨慎使用）。

```http
DELETE /api/rag/reset
```

### 10.8 测试RAG功能

运行简单的测试查询。

```http
GET /api/rag/test
```

### 10.9 获取示例问题

获取可以测试的示例问题列表。

```http
GET /api/rag/examples
```

---

## 意图识别

### 11. 分析用户意图

分析用户输入的意图。

```http
POST /intent/analyze
Content-Type: application/json

{
  "text": "我最近总是睡不着，该怎么办？",
  "user_id": "user_123"
}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "意图识别成功",
  "data": {
    "success": true,
    "intent": {
      "intent": "advice",
      "confidence": 0.85,
      "source": "model"
    },
    "action_required": false,
    "suggestion": {
      "response_style": "建设性、实用、温和",
      "priority": "medium",
      "actions": ["分析问题", "提供多个选择", "分享相关知识"]
    }
  }
}
```

### 11.1 快速检测意图

快速检测意图（仅返回意图类型）。

```http
POST /intent/detect?text=我该怎么办？
```

### 11.2 构建Prompt

根据用户上下文构建大模型prompt。

```http
POST /intent/build_prompt
Content-Type: application/json

{
  "analysis": {
    "emotion": {"primary": "焦虑"},
    "intent": {
      "intent": "advice",
      "confidence": 0.85,
      "source": "model"
    }
  }
}
```

### 11.3 获取意图类型列表

获取所有支持的意图类型。

```http
GET /intent/types
```

**支持的意图类型:**
- `emotion`: 情感表达
- `advice`: 寻求建议
- `conversation`: 普通对话
- `function`: 功能请求
- `crisis`: 危机干预
- `chat`: 闲聊

### 11.4 获取服务状态

获取意图识别服务状态。

```http
GET /intent/status
```

### 11.5 批量分析意图

批量分析多条文本的意图。

```http
POST /intent/batch
Content-Type: application/json

["文本1", "文本2", "文本3"]
```

---

## 记忆管理

### 12. 获取用户记忆列表

获取用户的记忆列表。

```http
GET /memory/users/{user_id}/memories?memory_type=emotion&limit=50
```

**查询参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| memory_type | string | 记忆类型（event/relationship/commitment/preference/concern） |
| limit | int | 返回数量限制 |

### 12.1 获取重要记忆

获取用户最重要的记忆。

```http
GET /memory/users/{user_id}/memories/important?limit=5
```

### 12.2 搜索相关记忆

搜索与查询相关的记忆。

```http
GET /memory/users/{user_id}/memories/search?query=工作压力&n_results=3&days_limit=7
```

### 12.3 删除记忆

删除指定的记忆。

```http
DELETE /memory/users/{user_id}/memories/{memory_id}
```

### 12.4 获取用户情绪趋势

获取用户情绪趋势。

```http
GET /memory/users/{user_id}/emotion-trend?days=7
```

### 12.5 获取记忆统计信息

获取用户记忆统计信息。

```http
GET /memory/users/{user_id}/statistics
```

### 12.6 获取用户画像

获取用户画像。

```http
GET /memory/users/{user_id}/profile
```

### 12.7 更新用户画像

更新用户画像。

```http
PUT /memory/users/{user_id}/profile
Content-Type: application/json

{
  "key": "value"
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
  "user_id": "user_123",
  "message_id": 456,
  "rating": 5,
  "comment": "回复很温暖，很有帮助",
  "feedback_type": "positive",
  "user_message": "用户消息",
  "bot_response": "AI回复"
}
```

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| session_id | string | 是 | 会话ID |
| user_id | string | 否 | 用户ID |
| message_id | int | 否 | 消息ID |
| rating | int | 否 | 评分（1-5） |
| comment | string | 否 | 文字反馈 |
| feedback_type | string | 否 | 反馈类型（positive/negative） |
| user_message | string | 否 | 用户消息 |
| bot_response | string | 否 | AI回复 |

**响应示例:**
```json
{
  "feedback_id": 789,
  "session_id": "session_123",
  "feedback_type": "positive",
  "rating": 5,
  "created_at": "2025-10-10T16:57:50.000000"
}
```

### 13.1 获取反馈统计信息

获取反馈统计信息。

```http
GET /feedback/statistics
```

### 13.2 获取反馈列表

获取反馈列表。

```http
GET /feedback/list?feedback_type=positive&limit=100
```

**查询参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| feedback_type | string | 反馈类型过滤 |
| limit | int | 返回数量限制 |

### 13.3 获取会话反馈

获取特定会话的反馈。

```http
GET /feedback/session/{session_id}
```

### 13.4 标记反馈已解决

标记反馈已解决。

```http
PUT /feedback/{feedback_id}/resolve
```

---

## 评估系统

### 14. 评估单个回应

使用LLM作为裁判，从共情程度、自然度、安全性三个维度评分。

```http
POST /evaluation/evaluate
Content-Type: application/json

{
  "session_id": "session_123",
  "user_id": "user_123",
  "message_id": 456,
  "user_message": "我今天心情不好",
  "bot_response": "我理解你的感受...",
  "user_emotion": "sad",
  "emotion_intensity": 7.5,
  "prompt_version": "v1.0"
}
```

**响应示例:**
```json
{
  "evaluation_id": 123,
  "empathy_score": 8.5,
  "naturalness_score": 9.0,
  "safety_score": 10.0,
  "average_score": 9.17,
  "total_score": 27.5,
  "overall_comment": "回复表现出良好的共情能力...",
  "strengths": ["共情表达", "语言自然"],
  "weaknesses": [],
  "improvement_suggestions": [],
  "created_at": "2025-10-10T16:57:50.000000"
}
```

### 14.1 批量评估

批量评估会话中的对话。

```http
POST /evaluation/batch
Content-Type: application/json

{
  "session_id": "session_123",
  "limit": 10
}
```

### 14.2 对比不同Prompt

对比不同Prompt生成的回应。

```http
POST /evaluation/compare-prompts
Content-Type: application/json

{
  "user_message": "我今天心情不好",
  "responses": ["回复1", "回复2"],
  "user_emotion": "sad",
  "emotion_intensity": 7.5
}
```

### 14.3 获取评估列表

获取评估列表。

```http
GET /evaluation/list?session_id=session_123&limit=100
```

### 14.4 获取评估统计信息

获取评估统计信息。

```http
GET /evaluation/statistics?start_date=2025-10-01&end_date=2025-10-31
```

### 14.5 获取评估详情

获取评估详情。

```http
GET /evaluation/{evaluation_id}
```

### 14.6 人工验证评估结果

人工验证评估结果。

```http
POST /evaluation/{evaluation_id}/human-verify
Content-Type: application/json

{
  "empathy_score": 8.0,
  "naturalness_score": 9.0,
  "safety_score": 10.0
}
```

### 14.7 生成评估报告

生成评估报告。

```http
GET /evaluation/report/generate?session_id=session_123&limit=100
```

---

## 个性化配置

### 15. 获取所有角色模板

获取所有预设角色模板。

```http
GET /api/personalization/templates
```

**响应示例:**
```json
[
  {
    "id": "warm_listener",
    "name": "温暖倾听者",
    "role": "温暖倾听者",
    "personality": "温暖、耐心、善于倾听",
    "description": "一个温暖的陪伴者，善于倾听，给予理解和支持",
    "icon": "❤️"
  }
]
```

### 15.1 获取角色模板详情

获取特定角色模板的详细信息。

```http
GET /api/personalization/template/{template_id}
```

### 15.2 获取用户配置

获取用户的个性化配置。

```http
GET /api/personalization/config/{user_id}
```

### 15.3 创建或更新用户配置

创建或更新用户的个性化配置。

```http
POST /api/personalization/config/{user_id}
Content-Type: application/json

{
  "role": "智慧导师",
  "role_name": "智者",
  "tone": "沉稳",
  "empathy_level": 0.7,
  "use_emoji": true
}
```

### 15.4 应用角色模板

应用角色模板到用户配置。

```http
POST /api/personalization/config/{user_id}/apply-template?template_id=wise_mentor
```

### 15.5 删除用户配置

删除用户的个性化配置（重置为默认）。

```http
DELETE /api/personalization/config/{user_id}
```

### 15.6 预览Prompt

预览根据当前配置生成的Prompt。

```http
GET /api/personalization/preview/{user_id}?context=今天心情不太好&emotion=sad&intensity=7.5
```

### 15.7 记录反馈

记录用户对个性化配置的反馈。

```http
POST /api/personalization/feedback/{user_id}?feedback_type=positive
```

---

## 增强版聊天

### 16. 增强版聊天接口

使用增强版多轮对话系统，支持短期记忆滑动窗口、长期记忆向量检索、动态用户画像构建等。

```http
POST /enhanced-chat
Content-Type: application/json

{
  "message": "我最近压力很大",
  "user_id": "user_123",
  "session_id": "optional-session-id"
}
```

**功能特性:**
- 短期记忆滑动窗口 + 关键轮次保留
- 长期记忆向量检索 + 时间衰减
- 动态用户画像构建
- 主动回忆与情感追踪

### 16.1 获取会话历史

获取增强版聊天的会话历史。

```http
GET /enhanced-chat/sessions/{session_id}/history?limit=20
```

### 16.2 获取用户所有会话

获取用户的所有会话列表。

```http
GET /enhanced-chat/users/{user_id}/sessions?limit=50
```

### 16.3 删除会话

删除会话。

```http
DELETE /enhanced-chat/sessions/{session_id}
```

### 16.4 获取用户画像

获取用户画像（核心关注点、情绪趋势、沟通风格等）。

```http
GET /enhanced-chat/users/{user_id}/profile
```

### 16.5 获取用户重要记忆

获取用户重要记忆。

```http
GET /enhanced-chat/users/{user_id}/memories?limit=10
```

### 16.6 获取用户情绪洞察

获取用户情绪洞察（情绪趋势、当前状态、显著变化点等）。

```http
GET /enhanced-chat/users/{user_id}/emotion-insights
```

### 16.7 获取系统状态

获取增强版聊天系统的功能启用状态。

```http
GET /enhanced-chat/system/status
```

---

## 流式聊天

### 17. 流式聊天接口

使用Server-Sent Events (SSE)实现流式响应。

```http
POST /streaming/chat
Content-Type: application/json

{
  "message": "你好",
  "session_id": "session_123",
  "user_id": "user_123"
}
```

**响应格式:** Server-Sent Events (text/event-stream)

### 17.1 带元数据的流式聊天

包含元数据的流式聊天。

```http
POST /streaming/chat/with-metadata
Content-Type: application/json

{
  "message": "你好",
  "session_id": "session_123",
  "user_id": "user_123",
  "metadata": {}
}
```

### 17.2 获取流式服务状态

获取流式服务状态。

```http
GET /streaming/status
```

### 17.3 测试流式响应

测试流式响应。

```http
POST /streaming/test
```

### 17.4 WebSocket聊天

使用WebSocket进行实时双向通信。

```http
WS /streaming/ws
```

### 17.5 流式服务信息

获取流式服务相关信息。

```http
GET /streaming
```

---

## 性能监控

### 18. 获取性能指标

获取性能指标数据。

```http
GET /performance/metrics
```

### 18.1 健康检查

系统健康检查。

```http
GET /performance/health
```

### 18.2 获取缓存统计信息

获取缓存统计信息。

```http
GET /performance/cache/stats
```

### 18.3 清除缓存

清除缓存。

```http
POST /performance/cache/clear?pattern=*
```

**查询参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| pattern | string | 缓存键模式，为空则清除所有 |

### 18.4 获取活跃流信息

获取活跃流列表。

```http
GET /performance/streams/active
```

### 18.5 获取优化配置

获取当前优化配置。

```http
GET /performance/optimization/config
```

### 18.6 更新优化配置

更新优化配置。

```http
POST /performance/optimization/config
Content-Type: application/json

{
  "cache_enabled": true,
  "max_concurrent_requests": 10,
  "cache_ttl": 3600
}
```

### 18.7 运行性能基准测试

运行性能基准测试。

```http
GET /performance/benchmark
```

### 18.8 获取系统信息

获取系统信息（CPU、内存、磁盘等）。

```http
GET /performance/system/info
```

### 18.9 性能监控仪表板

获取综合性能信息。

```http
GET /performance
```

---

## A/B测试

### 19. 创建实验

创建新的A/B测试实验。

```http
POST /ab-testing/experiments
Content-Type: application/json

{
  "experiment_id": "prompt_v2_test",
  "name": "Prompt版本对比测试",
  "description": "测试新版本Prompt的效果",
  "groups": ["A", "B"],
  "weights": [0.5, 0.5],
  "start_date": "2025-10-01T00:00:00Z",
  "end_date": "2025-10-31T23:59:59Z",
  "enabled": true,
  "metadata": {}
}
```

### 19.1 列出所有实验

列出所有实验。

```http
GET /ab-testing/experiments?enabled=true
```

### 19.2 获取实验详情

获取实验详情。

```http
GET /ab-testing/experiments/{experiment_id}
```

### 19.3 为用户分配实验组

为用户分配实验组。

```http
POST /ab-testing/assign
Content-Type: application/json

{
  "user_id": "user_123",
  "experiment_id": "prompt_v2_test",
  "force_group": null
}
```

### 19.4 获取用户已分配的组

获取用户已分配的组。

```http
GET /ab-testing/assign/{experiment_id}/{user_id}
```

### 19.5 分析实验数据

分析实验数据。

```http
POST /ab-testing/analyze
Content-Type: application/json

{
  "experiment_id": "prompt_v2_test",
  "metrics": ["user_rating", "response_time"],
  "start_date": "2025-10-01",
  "end_date": "2025-10-31"
}
```

### 19.6 获取实验统计信息

获取实验统计信息。

```http
GET /ab-testing/experiments/{experiment_id}/stats
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



