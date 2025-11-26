# Agent技术架构完整指南

> 本文档整合了情感聊天机器人项目中所有Agent相关的技术实现，帮助读者从技术角度深入理解Agent架构。

---

## 一、Agent整体架构

### 1.1 架构概览

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

### 1.2 模块职责

| 模块 | 职责 | 主要功能 |
|------|------|----------|
| Agent Core | 核心控制器 | 协调所有模块，管理完整交互流程 |
| Memory Hub | 记忆中枢 | 记忆编码、检索、巩固 |
| Planner | 任务规划 | 目标识别、任务分解、策略选择 |
| Tool Caller | 工具调用 | 工具注册、调用执行、结果处理 |
| Reflector | 反思优化 | 效果评估、策略优化、回访规划 |

---

## 二、核心模块详解

### 2.1 Agent Core

**文件**: `backend/agent/agent_core.py`

**核心处理流程**:

```python
async def process(user_input, user_id, conversation_id=None):
    """处理用户输入的完整流程"""
    # 1. 感知层：分析用户输入（情感分析、意图识别、实体提取）
    # 2. 记忆检索：获取相关记忆
    # 3. 任务规划：生成执行计划
    # 4. 执行计划：调用工具、生成回复
    # 5. 记忆巩固：保存新记忆
    # 6. 反思评估：评估交互效果
    # 7. 记录历史：保存执行记录
```

### 2.2 Memory Hub (记忆中枢)

**文件**: `backend/agent/memory_hub.py`

**记忆类型**:
- **情景记忆 (Episodic)**: 事件、经历，有时间戳和情感标签
- **语义记忆 (Semantic)**: 知识、概念，抽象通用
- **程序记忆 (Procedural)**: 技能、策略
- **对话记忆 (Conversation)**: 对话历史

**核心方法**:

```python
def encode(experience) -> Dict        # 编码：将新经验转换为记忆
def retrieve(query, user_id, context, top_k) -> List[Dict]  # 检索相关记忆
def consolidate(memory) -> bool       # 巩固：工作记忆转移到长期记忆
def get_user_profile(user_id) -> Dict # 获取用户画像
```

**检索策略**:
1. **语义检索**: 向量相似度搜索
2. **时间检索**: 近期优先
3. **情绪检索**: 情绪一致性匹配

### 2.3 Planner (规划模块)

**文件**: `backend/agent/planner.py`

**目标类型**:
- `INFORMATION_QUERY`: 信息查询
- `EMOTIONAL_SUPPORT`: 情感支持
- `PROBLEM_SOLVING`: 问题解决
- `BEHAVIOR_CHANGE`: 行为改变
- `CASUAL_CHAT`: 闲聊

**执行策略**:
- `DIRECT_RESPONSE`: 直接回复
- `EMPATHY_FIRST`: 情感优先
- `TOOL_USE`: 工具调用
- `SCHEDULED_FOLLOWUP`: 定时回访
- `CONVERSATIONAL`: 对话引导

### 2.4 Tool Caller (工具调用)

**文件**: `backend/agent/tool_caller.py`

**内置工具**:
- `search_memory`: 搜索记忆
- `get_emotion_log`: 获取情绪日志
- `set_reminder`: 设置提醒
- `recommend_meditation`: 推荐冥想
- `recommend_resource`: 推荐资源
- `psychological_assessment`: 心理评估

### 2.5 Reflector (反思模块)

**文件**: `backend/agent/reflector.py`

**评估指标**:
- 用户满意度
- 响应时间
- 目标达成度
- 情绪变化
- 工具使用效果

---

## 三、Agent工具函数实战

### 3.1 五大核心工具

#### 1. get_user_mood_trend - 情绪趋势分析

```python
from backend.agent.tools.agent_tools import get_user_mood_trend

result = get_user_mood_trend("user_123", days=7)
# 返回: {
#     "trend": [...],           # 每日情绪数据
#     "average_intensity": 6.5, # 平均强度
#     "trend_direction": "improving",  # 趋势方向
#     "needs_intervention": False,     # 是否需要干预
#     "summary": "..."         # 趋势摘要
# }
```

#### 2. play_meditation_audio - 冥想音频播放

```python
from backend.agent.tools.agent_tools import play_meditation_audio

result = play_meditation_audio("anxiety", user_id="user_123")
# genre可选: "sleep", "anxiety", "relaxation", "breathing"
```

#### 3. set_daily_reminder - 每日提醒

```python
from backend.agent.tools.agent_tools import set_daily_reminder

result = set_daily_reminder(
    time="21:30",
    message="今晚早点放松哦，记得做睡前冥想",
    user_id="user_123"
)
```

#### 4. search_mental_health_resources - 心理资源搜索

```python
from backend.agent.tools.agent_tools import search_mental_health_resources

result = search_mental_health_resources("焦虑", resource_type="article")
# resource_type可选: "article", "video", "exercise"
```

#### 5. send_follow_up_message - 回访消息

```python
from backend.agent.tools.agent_tools import send_follow_up_message

result = send_follow_up_message(
    user_id="user_123",
    days_ago=1,
    custom_message="你好，距离我们上次聊天已经过去1天了。最近感觉怎么样？"
)
```

### 3.2 实战场景示例

**场景1: 用户连续失眠**

```python
# 1. 检查情绪趋势
mood_trend = get_user_mood_trend("user_123", days=7)
if mood_trend["needs_intervention"]:
    # 2. 播放助眠音频
    audio_result = play_meditation_audio("sleep", "user_123")
    # 3. 设置每日提醒
    reminder_result = set_daily_reminder(
        time="21:30",
        message="今晚早点放松哦",
        user_id="user_123"
    )
    # 4. 安排回访
    follow_up = send_follow_up_message("user_123", days_ago=1)
```

**场景2: 用户表达焦虑**

```python
# 1. 播放焦虑缓解音频
audio_result = play_meditation_audio("anxiety", "user_123")
# 2. 搜索相关资源
resources = search_mental_health_resources("焦虑", "article")
# 3. 推荐资源给用户
for resource in resources["resources"]:
    print(f"推荐: {resource['title']}")
```

---

## 四、MCP协议 (Model Context Protocol)

### 4.1 协议概述

MCP是专为大模型智能体设计的结构化通信协议，实现模块间标准化、低耦合、高内聚的协作。

### 4.2 消息结构

```json
{
    "message_id": "唯一消息ID",
    "message_type": "消息类型",
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
    "target_module": "目标模块"
}
```

### 4.3 消息类型

- `user_input`: 用户输入
- `planner_output`: Planner规划输出
- `tool_request`: 工具请求
- `tool_response`: 工具响应
- `agent_response`: Agent回复
- `reflector_evaluation`: Reflector评估结果

### 4.4 使用示例

```python
from backend.modules.agent.core.agent.agent_core import AgentCore

agent = AgentCore()

# 使用MCP协议处理
mcp_response = await agent.process_with_mcp(
    user_input="我最近睡不好，怎么办？",
    user_id="user_123"
)

# 获取回复
response = mcp_response.content
```

### 4.5 通信流程

```
用户输入
    ↓
Agent Core (创建user_input MCP消息)
    ↓
Planner (plan_with_mcp) → planner_output
    ↓
Tool Caller (call_with_mcp) → tool_response
    ↓
Agent Core (生成回复) → agent_response
    ↓
Reflector (evaluate_with_mcp) → reflector_evaluation
    ↓
返回最终回复
```

---

## 五、意图识别模块

### 5.1 混合式架构

```
用户输入
  ↓
输入预处理器 (InputProcessor)
  ├── 文本清洗
  ├── 风险检测
  └── 合规验证
  ↓
意图分类器 (IntentClassifier)
  ├── 规则引擎 (RuleEngine) - 关键词快速匹配
  └── ML分类器 (MLClassifier) - BERT模型处理复杂语义
  ↓
融合策略
  ├── 危机优先
  ├── 高置信度规则
  └── 模型预测
  ↓
意图结果 + 响应建议
```

### 5.2 六大意图类型

| 意图类型 | 说明 | 示例 |
|---------|------|------|
| **emotion** | 情感表达 | "我好难过"、"今天心情不好" |
| **advice** | 寻求建议 | "怎么办？"、"你有什么建议" |
| **conversation** | 普通对话 | "今天天气不错"、"我在看书" |
| **function** | 功能请求 | "提醒我吃药"、"记录今天的心情" |
| **crisis** | 危机干预 | "不想活了"、"撑不下去" |
| **chat** | 闲聊 | "你好"、"在吗"、"晚上好" |

### 5.3 API使用

```python
import requests

# 分析意图
response = requests.post(
    "http://localhost:8000/intent/analyze",
    json={
        "text": "我最近压力很大，睡不好觉",
        "user_id": "user_123"
    }
)
result = response.json()
print(f"意图: {result['data']['intent']['intent']}")
print(f"置信度: {result['data']['intent']['confidence']}")
```

---

## 六、记忆系统架构

### 6.1 分层架构

```
┌──────────────────────────────────────────────────┐
│              Memory Hub (记忆中枢)                │
│  ┌──────────────┐      ┌──────────────────────┐  │
│  │  工作记忆    │      │     长期记忆          │  │
│  │ (Working     │      │  ┌──────────────────┐ │  │
│  │  Memory)     │      │  │   情景记忆       │ │  │
│  │              │      │  │ (Episodic)       │ │  │
│  │ - 对话上下文  │      │  └──────────────────┘ │  │
│  │ - 激活任务    │      │  ┌──────────────────┐ │  │
│  │ - 临时变量    │      │  │   语义记忆       │ │  │
│  └──────────────┘      │  │ (Semantic)       │ │  │
│                         │  └──────────────────┘ │  │
│                         │  ┌──────────────────┐ │  │
│                         │  │   对话记忆       │ │  │
│                         │  │ (Conversation)   │ │  │
│                         │  └──────────────────┘ │  │
│                         └──────────────────────┘  │
└──────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
    ┌─────────┐         ┌─────────┐         ┌─────────┐
    │  MySQL  │         │ ChromaDB │         │ Memory  │
    │ 数据库   │         │ 向量数据库│         │ Manager │
    └─────────┘         └─────────┘         └─────────┘
```

### 6.2 检索流程

```
用户查询
    ↓
多路径检索
    ├─→ 向量语义检索 (相似度)
    ├─→ 时间序列检索 (近期优先)
    └─→ 情绪关联检索 (情绪一致性)
    ↓
合并去重 → 按重要性排序 → 返回Top-K记忆
```

### 6.3 重要性计算

- 情绪强度 (30%)
- 关键词匹配 (20%)
- 内容长度 (10%)
- 用户反馈 (40%)

---

## 七、扩展指南

### 7.1 添加新工具

```python
# 1. 在 tool_caller.py 中实现工具函数
async def _my_tool_impl(self, param1: str, param2: int) -> Dict:
    """工具实现"""
    return {"result": "success"}

# 2. 注册工具
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

### 7.2 自定义规划策略

在 `planner.py` 的 `_select_strategy()` 方法中添加自定义逻辑。

### 7.3 扩展记忆类型

在 `memory_hub.py` 的 `_infer_memory_type()` 方法中添加新的记忆类型判断。

---

## 八、性能优化

### 8.1 缓存策略

- 用户画像缓存（1小时）
- 工作记忆缓存（会话期间）
- 工具结果缓存（5分钟）

### 8.2 性能指标

- 检索速度: < 100ms (Top-5)
- 编码速度: < 50ms
- 巩固速度: < 200ms
- 内存占用: < 100MB (工作记忆)

---

## 九、场景延伸

Agent架构不仅适用于情感聊天机器人，还可以延伸到以下场景：

### 9.1 智能客服
- **Memory Hub**: 存储用户历史工单、购买记录
- **Planner**: 识别问题类型，规划解决路径
- **Tool Caller**: 调用订单查询、退款处理等API

### 9.2 个人助理
- **Memory Hub**: 日程、偏好、联系人
- **Planner**: 任务优先级排序
- **Tool Caller**: 日历、邮件、提醒等工具

### 9.3 教育辅导
- **Memory Hub**: 学习进度、知识掌握情况
- **Planner**: 个性化学习路径规划
- **Reflector**: 学习效果评估与调整

### 9.4 医疗问诊
- **Memory Hub**: 病史、用药记录
- **Planner**: 症状分析、就诊建议
- **Tool Caller**: 知识库检索、预约挂号

---

## 十、相关文件索引

| 文件 | 说明 |
|------|------|
| `backend/agent/agent_core.py` | Agent核心控制器 |
| `backend/agent/memory_hub.py` | 记忆中枢 |
| `backend/agent/planner.py` | 任务规划模块 |
| `backend/agent/tool_caller.py` | 工具调用模块 |
| `backend/agent/reflector.py` | 反思优化模块 |
| `backend/agent/tools/agent_tools.py` | Agent工具函数 |
| `backend/modules/agent/protocol/mcp.py` | MCP协议实现 |
| `backend/modules/intent/` | 意图识别模块 |

---

**版本**: v1.0.0  
**最后更新**: 2025-11-26  
**整合自**: Agent核心模块实现总结.md, MCP协议说明.md, MCP集成总结.md, 记忆系统架构.md, 意图识别模块说明.md, README_AGENT_TOOLS.md

