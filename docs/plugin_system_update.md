# 插件系统更新说明

## 更新内容

本次更新为"心语"机器人添加了完整的插件系统支持，让AI能够从"情感陪伴"升级为"全能助手"。

### 新增功能

1. **插件基础框架**
   - `BasePlugin` - 插件基类，定义统一接口（execute、function_schema、validate_params）
   - `PluginManager` - 插件管理器，负责注册、调用、监控、历史追踪
   - `Function Calling` 集成 - 支持 LLM 自主调用插件，基于 OpenAI Function Calling 协议

2. **已实现插件**
   - **天气查询插件 (WeatherPlugin)** - 支持 OpenWeatherMap API 和和风天气 API，返回温度、湿度、风速等结构化数据
   - **新闻推送插件 (NewsPlugin)** - 支持多类别新闻查询（科技、健康、娱乐、科学等），可配置返回数量

3. **API 接口**
   - `GET /plugins/list` - 列出所有插件及其 Function Schema
   - `GET /plugins/stats` - 获取插件使用统计信息
   - `GET /plugins/{plugin_name}/history` - 查看特定插件的调用历史

### 文件变更

#### 新增文件

```
backend/
├── plugins/
│   ├── __init__.py          # 插件模块初始化
│   ├── base_plugin.py       # 插件基类
│   ├── weather_plugin.py    # 天气查询插件
│   ├── news_plugin.py       # 新闻推送插件
│   ├── plugin_manager.py    # 插件管理器
│   └── README.md            # 插件系统文档
└── modules/llm/core/
    └── llm_with_plugins.py  # 带插件支持的聊天引擎
```

#### 修改文件

- `backend/models.py` - 在 `ChatResponse` 中添加 `plugin_used` 和 `plugin_result` 字段
- `backend/main.py` - 集成 `EmotionalChatEngineWithPlugins`，新增插件管理接口，更新根路径显示插件统计

### 使用方式

#### 1. 配置 API 密钥

编辑 `config.env` 文件：

```bash
# 天气 API（二选一）
OPENWEATHER_API_KEY=your_key_here
# HEFENG_WEATHER_API_KEY=your_key_here

# 新闻 API
NEWS_API_KEY=your_key_here

# LLM API（必需）
LLM_API_KEY=your_llm_key_here
```

#### 2. 启动服务

```bash
python run_backend.py
```

#### 3. 测试插件

```bash
# 测试天气查询
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "明天北京天气怎么样？", "user_id": "test"}'

# 测试新闻推送
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "最近有什么科技新闻？", "user_id": "test"}'
```

### 技术特性

#### Function Calling 机制

插件系统基于 OpenAI Function Calling 协议：

1. **请求阶段**：AI 判断是否需要调用插件
2. **执行阶段**：自动调用相应插件执行任务
3. **融合阶段**：将插件结果自然融入对话回复

#### 插件自动调用示例

```python
# 用户输入
"明天去杭州出差，天气怎么样？"

# AI 自动决定调用插件
function_call: {
  "name": "get_weather",
  "arguments": {"location": "杭州"}
}

# 插件返回结果
{
  "location": "杭州",
  "temperature": 22,
  "description": "晴",
  "humidity": 50,
  "wind_speed": 3.5
}

# AI 生成融合回复
"我理解你出差前的小小紧张。我帮你查了杭州的天气，明天晴朗舒适，温度22℃，湿度适中，很适合出行。建议你带把晴雨伞以防万一，还有轻便外套。把需要的东西列个清单，一项项打勾会让你更有掌控感。祝你出差顺利~"

# 响应中包含插件信息
{
  "response": "...",
  "plugin_used": "get_weather",
  "plugin_result": {"location": "杭州", "temperature": 22, ...}
}
```

### 扩展性设计

#### 添加新插件只需3步

```python
# 1. 创建插件类
class MyPlugin(BasePlugin):
    def __init__(self, api_key: str = None):
        super().__init__(
            name="my_plugin",
            description="我的自定义插件功能描述",
            api_key=api_key
        )
    
    @property
    def function_schema(self) -> Dict[str, Any]:
        return {
            "name": "my_plugin",
            "description": "插件功能描述，告诉AI何时使用此插件",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "参数1的说明"
                    }
                },
                "required": ["param1"]
            }
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        param1 = kwargs.get("param1")
        return {"result": f"处理了: {param1}", "status": "success"}

# 2. 在 EmotionalChatEngineWithPlugins 中注册插件
my_plugin = MyPlugin(api_key="your-key")
self.plugin_manager.register(my_plugin)

# 3. 无需修改其他代码，自动生效
```

### 安全与监控

- **调用历史追踪**：记录所有插件调用记录
- **使用统计**：实时监控插件使用情况
- **错误处理**：优雅降级，不中断用户体验
- **权限控制**：未来支持插件级别的权限管理

### 性能优化

- **失败降级**：API 调用失败时返回模拟数据，确保用户体验不中断
- **参数验证**：插件执行前进行参数验证，避免无效调用
- **错误处理**：统一的异常处理机制，优雅处理各种错误情况
- **调用历史**：记录插件调用历史，便于调试和监控（未来：缓存策略、异步调用）

### 兼容性说明

- ✅ 向后兼容：不影响现有聊天功能
- ✅ 可选功能：插件功能可选择性启用
- ✅ 降级机制：无 API 密钥时自动降级

### 已知限制

1. **API 依赖**：需要配置外部 API 密钥才能使用真实数据（天气、新闻）
2. **模型支持**：Function Calling 需要 LLM 模型支持（OpenAI GPT-4+ 或兼容接口）
3. **同步调用**：插件调用为同步模式，并发性能有待优化
4. **权限控制**：当前为简化实现，暂未实现细粒度权限控制
5. **沙箱隔离**：插件在相同进程中运行，未实现沙箱隔离（未来计划）

### 未来规划

1. **更多实用插件**：
   - 日程管理插件 - 提醒用户重要事项
   - 邮件发送插件 - 帮助用户发送邮件
   - 音乐播放插件 - 根据情绪推送音乐
   - 心理咨询插件 - 提供 CBT 等心理干预

2. **插件市场**：第三方开发者贡献插件，用户按需安装

3. **智能编排**：多插件组合调用，条件触发机制

4. **权限系统**：细粒度权限控制，用户授权机制

5. **性能优化**：异步调用、批量处理、缓存策略

6. **沙箱隔离**：Docker 容器或函数计算环境运行插件

### 问题反馈

如有问题或建议，请提交 Issue 或联系开发团队。

### 相关文档

- [插件系统完整文档](./plugin_system_guide.md)
- [插件开发指南](../backend/plugins/README.md)
- [API 文档](http://localhost:8000/docs)
