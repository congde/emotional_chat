# Agent工具函数使用说明

本文档说明文档中提到的5个核心Agent工具函数的实现和使用方法。

## 工具函数列表

### 1. `get_user_mood_trend(user_id, days=7)`

**功能**: 获取近N天情绪变化曲线，判断是否需干预

**参数**:
- `user_id` (str, 必需): 用户ID
- `days` (int, 可选): 查询天数，默认7天

**返回**:
```python
{
    "trend": List[Dict],  # 每日情绪数据
    "average_intensity": float,  # 平均情绪强度
    "trend_direction": str,  # "improving" / "declining" / "stable"
    "needs_intervention": bool,  # 是否需要干预
    "intervention_reason": str,  # 干预原因
    "summary": str  # 趋势摘要
}
```

**使用示例**:
```python
from backend.agent.tools.agent_tools import get_user_mood_trend

result = get_user_mood_trend("user_123", days=7)
if result["needs_intervention"]:
    print(f"需要干预: {result['intervention_reason']}")
```

---

### 2. `play_meditation_audio(genre, user_id=None)`

**功能**: 播放冥想音频，缓解焦虑

**参数**:
- `genre` (str, 必需): 音频类型
  - `"sleep"`: 睡眠相关
  - `"anxiety"`: 焦虑缓解
  - `"relaxation"`: 放松
  - `"breathing"`: 呼吸练习
- `user_id` (str, 可选): 用户ID，用于记录播放历史

**返回**:
```python
{
    "success": bool,
    "audio": {
        "id": str,
        "title": str,
        "url": str,
        "duration": int,
        "description": str
    },
    "message": str
}
```

**使用示例**:
```python
from backend.agent.tools.agent_tools import play_meditation_audio

result = play_meditation_audio("sleep", user_id="user_123")
if result["success"]:
    print(f"正在播放: {result['audio']['title']}")
```

---

### 3. `set_daily_reminder(time, message, user_id)`

**功能**: 设置每日提醒，养成作息习惯

**参数**:
- `time` (str, 必需): 提醒时间，格式 "HH:MM" 或 "HH:MM:SS"
- `message` (str, 必需): 提醒消息内容
- `user_id` (str, 必需): 用户ID

**返回**:
```python
{
    "success": bool,
    "reminder_id": str,
    "scheduled_time": str,  # ISO格式
    "time": str,
    "message": str
}
```

**使用示例**:
```python
from backend.agent.tools.agent_tools import set_daily_reminder

result = set_daily_reminder(
    time="21:30",
    message="今晚早点放松哦，记得做睡前冥想",
    user_id="user_123"
)
if result["success"]:
    print(f"提醒已设置: {result['message']}")
```

---

### 4. `search_mental_health_resources(query, resource_type=None)`

**功能**: 检索专业心理文章，提供知识支持

**参数**:
- `query` (str, 必需): 搜索关键词
- `resource_type` (str, 可选): 资源类型
  - `"article"`: 文章
  - `"video"`: 视频
  - `"exercise"`: 练习

**返回**:
```python
{
    "count": int,
    "resources": List[Dict],  # 资源列表
    "query": str,
    "message": str
}
```

**使用示例**:
```python
from backend.agent.tools.agent_tools import search_mental_health_resources

result = search_mental_health_resources("焦虑", resource_type="article")
print(f"找到 {result['count']} 个相关资源")
for resource in result["resources"]:
    print(f"- {resource['title']}")
```

---

### 5. `send_follow_up_message(user_id, days_ago=1, custom_message=None)`

**功能**: 发送回访消息，验证效果

**参数**:
- `user_id` (str, 必需): 用户ID
- `days_ago` (int, 可选): 回访几天前的对话，默认1天前
- `custom_message` (str, 可选): 自定义消息内容

**返回**:
```python
{
    "success": bool,
    "reminder_id": str,
    "message": str,
    "scheduled_at": str,  # ISO格式
    "days_ago": int
}
```

**使用示例**:
```python
from backend.agent.tools.agent_tools import send_follow_up_message

result = send_follow_up_message(
    user_id="user_123",
    days_ago=1,
    custom_message="你好，距离我们上次聊天已经过去1天了。最近感觉怎么样？"
)
if result["success"]:
    print(f"回访消息已安排: {result['scheduled_at']}")
```

---

## 通过ToolCaller调用

这些工具函数已经注册到 `ToolCaller` 中，可以通过Agent系统调用：

```python
from backend.agent.tool_caller import get_tool_caller

tool_caller = get_tool_caller()

# 调用工具
result = await tool_caller.call(
    "get_user_mood_trend",
    {
        "user_id": "user_123",
        "days": 7
    }
)
```

## 工具注册信息

所有工具都已注册到 `ToolCaller`，工具名称如下：

1. `get_user_mood_trend` - 获取用户情绪趋势
2. `play_meditation_audio` - 播放冥想音频
3. `set_daily_reminder` - 设置每日提醒
4. `search_mental_health_resources` - 搜索心理健康资源
5. `send_follow_up_message` - 发送回访消息

## 测试

运行测试脚本验证工具函数：

```bash
python test_agent_tools.py
```

## 注意事项

1. **数据库连接**: `get_user_mood_trend` 需要数据库连接，确保MySQL服务正常运行
2. **音频资源**: `play_meditation_audio` 使用内存中的音频库，实际部署时需要对接真实的音频服务
3. **提醒系统**: `set_daily_reminder` 和 `send_follow_up_message` 使用内存存储，生产环境应使用APScheduler或Celery
4. **资源库**: `search_mental_health_resources` 使用内存中的资源库，实际应连接真实的知识库

## 集成到Agent系统

这些工具函数已经集成到Agent系统中，可以在以下场景使用：

1. **规划模块 (Planner)**: 根据用户情绪趋势决定是否需要干预
2. **工具调用模块 (Tool Caller)**: 执行具体的工具调用
3. **反思模块 (Reflector)**: 基于工具执行结果进行反思和优化

## 示例场景

### 场景1: 用户连续失眠

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

### 场景2: 用户表达焦虑

```python
# 1. 播放焦虑缓解音频
audio_result = play_meditation_audio("anxiety", "user_123")
# 2. 搜索相关资源
resources = search_mental_health_resources("焦虑", "article")
# 3. 推荐资源给用户
```

## 扩展

如需添加新的工具函数：

1. 在 `backend/agent/tools/agent_tools.py` 中实现函数
2. 在 `backend/agent/tool_caller.py` 的 `_register_builtin_tools()` 方法中注册
3. 更新本文档

