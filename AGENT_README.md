# 🤖 心语Agent核心模块

> 将心语机器人从"被动响应"升级到"主动服务"

## ✨ 快速开始

### 1. 查看演示

```bash
cd /home/workSpace/emotional_chat
python demo_agent.py
```

### 2. 启动服务

```bash
python run_backend.py
```

### 3. 测试API

```bash
curl -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "message": "我最近睡不好，怎么办？"}'
```

## 📊 架构总览

```
                    ┌─────────────────────┐
                    │    用户交互层        │
                    └──────────┬──────────┘
                               │
          ┌────────────────────┴────────────────────┐
          │          Agent Core 智能核心             │
          │  ┌──────────┐ ┌──────────┐ ┌─────────┐ │
          │  │ Planner  │ │Tool Caller│ │Reflector│ │
          │  └──────────┘ └──────────┘ └─────────┘ │
          └────────────────────┬────────────────────┘
                               │
              ┌────────────────┴────────────────┐
              │                                 │
        ┌─────┴──────┐                  ┌──────┴──────┐
        │ Memory Hub │                  │External Tools│
        │  记忆中枢   │                  │  外部工具    │
        └────────────┘                  └─────────────┘
```

## 🎯 核心功能

### 1. 智能规划 (Planner)

自动分解目标，选择最优策略

```python
用户: "我怎么能睡得更好？"
Agent: 
  → 识别目标: 问题解决
  → 分解任务: 理解问题 → 搜索方案 → 推荐资源 → 安排回访
  → 选择策略: Tool-Use策略
```

### 2. 工具调用 (Tool Caller)

10+内置工具，自动调用

- 🔍 记忆工具: `search_memory`, `get_emotion_log`
- ⏰ 定时工具: `set_reminder`, `check_calendar`
- 🎵 资源工具: `recommend_meditation`, `recommend_resource`
- 📋 评估工具: `psychological_assessment`

### 3. 记忆管理 (Memory Hub)

长短期记忆，个性化服务

- 短期记忆: 当前对话上下文
- 长期记忆: 历史事件、情绪、偏好
- 用户画像: 性格特征、兴趣爱好、情绪基线

### 4. 主动回访 (Reflector)

定时关怀，持续支持

```python
今天: 用户提到睡眠问题
7天后: Agent主动询问 "你最近睡眠有改善吗？"
```

### 5. 反思优化

持续学习，不断进化

- 评估每次交互效果
- 分析成功/失败模式
- 优化规划策略

## 📁 文件结构

```
backend/
├── agent/                      # Agent核心模块
│   ├── __init__.py
│   ├── agent_core.py           # 总控制器 (650行)
│   ├── memory_hub.py           # 记忆中枢 (520行)
│   ├── planner.py              # 规划器 (450行)
│   ├── tool_caller.py          # 工具调用器 (680行)
│   ├── reflector.py            # 反思器 (580行)
│   ├── README.md               # 详细使用指南
│   └── tools/                  # 外部工具
│       ├── calendar_api.py     # 日历服务
│       ├── audio_player.py     # 音频播放
│       ├── psychology_db.py    # 心理资源库
│       └── scheduler_service.py # 定时提醒
│
├── routers/
│   └── agent.py                # Agent路由
│
├── services/
│   └── agent_service.py        # Agent服务层
│
└── app.py                      # 主应用（已集成）
```

## 🌐 API接口

### Agent聊天

```http
POST /agent/chat
Content-Type: application/json

{
  "user_id": "user_123",
  "message": "我最近睡不好，怎么办？"
}
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "success": true,
    "response": "我理解你的困扰。睡眠问题确实很影响生活质量...",
    "emotion": "焦虑",
    "emotion_intensity": 7.5,
    "actions": [
      {"type": "tool_call", "tool": "recommend_meditation", "success": true}
    ],
    "followup_scheduled": true,
    "response_time": 1.2
  }
}
```

### 其他接口

- `GET /agent/status` - 获取Agent状态
- `GET /agent/history/{user_id}` - 查看执行历史
- `GET /agent/memory/{user_id}` - 获取记忆摘要
- `GET /agent/tools` - 查看可用工具
- `POST /agent/followup` - 规划回访任务

## 🔥 使用示例

### 场景1: 问题解决

```python
from backend.agent import AgentCore

agent = AgentCore()

result = await agent.process(
    user_input="我最近睡不好，怎么办？",
    user_id="user_123"
)

print(result["response"])
# 输出: 我理解你的困扰。睡眠问题确实很影响生活质量...
#      我为你推荐了几个助眠冥想练习：
#      1. 深度睡眠引导冥想（15分钟）
#      2. 助眠白噪音（30分钟）
#      ...
```

### 场景2: 工具调用

```python
from backend.agent import ToolCaller

tool_caller = ToolCaller()

# 推荐冥想音频
result = await tool_caller.call(
    "recommend_meditation",
    {"theme": "sleep", "duration": 15}
)

for audio in result["result"]["recommendations"]:
    print(f"- {audio['title']} ({audio['duration']}分钟)")
```

### 场景3: 记忆管理

```python
from backend.agent import MemoryHub

memory_hub = MemoryHub()

# 检索相关记忆
memories = memory_hub.retrieve(
    query="睡眠问题",
    user_id="user_123",
    context={"emotion": "焦虑"}
)

# 获取用户画像
profile = memory_hub.get_user_profile("user_123")
print(f"主导情绪: {profile['emotion_baseline']['dominant_emotion']}")
```

## 📈 对比优势

### 传统模式 vs Agent模式

| 特性 | 传统模式 | Agent模式 |
|------|---------|----------|
| 响应方式 | 被动回复 | 主动服务 |
| 任务规划 | 单一回复 | 智能分解 |
| 工具使用 | 手动调用 | 自动调用 |
| 记忆管理 | 简单存储 | 智能检索 |
| 后续跟进 | ❌ 无 | ✅ 主动回访 |
| 效果评估 | ❌ 无 | ✅ 反思优化 |

### 实际效果对比

**传统模式**:
```
用户: "我最近睡不好"
机器人: "你可以试试冥想。"
（对话结束）
```

**Agent模式**:
```
用户: "我最近睡不好"
Agent: 
  1. 分析情况（检测到焦虑情绪）
  2. 检索记忆（发现连续7天睡眠质量差）
  3. 制定方案（推荐冥想 + 设置提醒 + 安排回访）
  4. 执行行动（推荐3个音频 + 21:30提醒）
  5. 主动跟进（7天后询问改善情况）
```

## 📊 实现统计

```
新增文件:    20+ 个
新增代码:    ~4,500 行
核心模块:    5 个
外部工具:    4 个
内置工具:    10+ 个
API接口:     7 个
```

## 📚 相关文档

- **架构文档**: [docs/记忆系统架构.md](docs/记忆系统架构.md)
- **使用指南**: [backend/agent/README.md](backend/agent/README.md)
- **实现总结**: [docs/Agent核心模块实现总结.md](docs/Agent核心模块实现总结.md)
- **API文档**: http://localhost:8000/docs

## 🚀 部署

### 开发环境

```bash
# 1. 启动服务
python run_backend.py

# 2. 验证Agent模块
curl http://localhost:8000/
# 看到 "agent_enabled": true 表示成功

# 3. 查看API文档
open http://localhost:8000/docs
```

### 生产环境

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
export ENABLE_AGENT=true
export AGENT_MODE=smart

# 3. 启动服务
gunicorn backend.app:app --workers 4 --bind 0.0.0.0:8000
```

## 🔧 配置

### 环境变量

```env
# config.env

# Agent模块配置
ENABLE_AGENT=true           # 启用Agent模块
AGENT_MODE=smart            # smart/simple/hybrid

# 工具配置
ENABLE_TOOLS=true           # 启用工具调用
TOOL_TIMEOUT=30             # 工具调用超时（秒）

# 回访配置
ENABLE_FOLLOWUP=true        # 启用主动回访
FOLLOWUP_INTERVAL=7         # 默认回访间隔（天）
```

## 🧪 测试

### 运行演示

```bash
python demo_agent.py
```

### 单元测试

```bash
pytest tests/test_agent.py -v
```

### API测试

```bash
# 测试聊天接口
curl -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user", "message": "测试消息"}'

# 查看Agent状态
curl http://localhost:8000/agent/status
```

## 💡 最佳实践

1. **渐进式采用**: 先在部分功能中试用Agent模式
2. **降级策略**: 准备非Agent模式的后备方案
3. **监控指标**: 持续监控响应时间和成功率
4. **用户反馈**: 收集用户对Agent交互的反馈
5. **定期优化**: 根据反思模块的分析结果优化策略

## 🔮 未来计划

### 短期（1个月）
- [ ] 集成真实的LLM服务（GPT-4等）
- [ ] 完善工具调用参数生成
- [ ] 添加更多心理资源
- [ ] 优化回访时间算法

### 中期（3个月）
- [ ] 实现真实的定时任务系统（APScheduler）
- [ ] 对接Google Calendar等外部API
- [ ] 添加语音转文字支持
- [ ] 实现用户偏好学习

### 长期（6个月+）
- [ ] 多模态支持（语音、图片）
- [ ] 群组聊天支持
- [ ] 专业咨询师对接
- [ ] A/B测试框架

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

### 添加新工具

```python
# 1. 在 backend/agent/tools/ 创建新工具文件
# 2. 实现工具类
class MyNewTool:
    def execute(self, **params):
        # 工具逻辑
        pass

# 3. 注册工具
tool_caller = get_tool_caller()
tool_caller.registry.register(
    name="my_new_tool",
    description="新工具描述",
    function=my_tool_function,
    parameters={...},
    category="custom"
)
```

## 📝 更新日志

### v1.0.0 (2025-10-15)
- ✨ 初始版本发布
- ✅ 实现完整的Agent架构
- ✅ 提供5个核心模块
- ✅ 内置10+工具
- ✅ 提供7个API接口
- ✅ 完善的文档

## 📞 联系方式

如有问题或建议，请联系开发团队或提交Issue。

---

**Made with ❤️ by 心语团队**

*从被动响应到主动服务，我们一直在进化。*

