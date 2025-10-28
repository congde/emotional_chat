# 心语机器人插件系统

## 概述

心语机器人插件系统为AI机器人提供了强大的可扩展能力，使其从"情感陪伴"升级为"全能助手"。通过插件，机器人可以：

- **查询实时信息**：天气、新闻、股价等
- **执行实际操作**：发送邮件、设置提醒、管理日程
- **提供专业服务**：心理咨询、学习辅导、健康建议

## 架构设计

### 核心组件

1. **BasePlugin（插件基类）**
   - 定义所有插件必须实现的接口
   - 提供统一的生命周期管理
   - 支持参数验证和错误处理

2. **PluginManager（插件管理器）**
   - 负责插件的注册、注销、调用
   - 管理调用历史和权限控制
   - 提供使用统计和监控

3. **Function Calling 集成**
   - 基于 OpenAI Function Calling 协议
   - 模型自主决定何时调用插件
   - 无缝融合自然语言对话与工具调用

## 已实现插件

### 1. 天气查询插件 (WeatherPlugin)

**功能**：根据城市名称查询实时天气信息

**使用示例**：
- 用户："明天去杭州，天气怎么样？"
- 插件调用：`get_weather(location="杭州")`
- 返回：`{"location": "杭州", "temperature": 22, "description": "晴", "humidity": 50}`

**配置**：
```bash
# 使用 OpenWeatherMap API
export OPENWEATHER_API_KEY="your-api-key"

# 或使用和风天气 API
export HEFENG_WEATHER_API_KEY="your-api-key"
```

### 2. 新闻推送插件 (NewsPlugin)

**功能**：根据用户兴趣推送最新新闻

**使用示例**：
- 用户："最近有什么科技新闻？"
- 插件调用：`get_latest_news(category="technology", count=3)`
- 返回：`{"category": "technology", "articles": [...]}`

**支持的类别**：
- `general` - 综合新闻
- `technology` - 科技
- `health` - 健康
- `entertainment` - 娱乐
- `science` - 科学
- `sports` - 体育
- `business` - 商业

**配置**：
```bash
export NEWS_API_KEY="your-api-key"
```

## 如何开发新插件

### 步骤1：创建插件类

```python
from backend.plugins.base_plugin import BasePlugin
from typing import Dict, Any

class MyCustomPlugin(BasePlugin):
    """自定义插件示例"""
    
    def __init__(self, api_key: str = None):
        super().__init__(
            name="my_plugin",
            description="我的自定义插件功能描述",
            api_key=api_key
        )
    
    @property
    def function_schema(self) -> Dict[str, Any]:
        """定义 Function Calling Schema"""
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
        """执行插件逻辑"""
        param1 = kwargs.get("param1")
        
        # 实现你的插件功能
        result = self._do_something(param1)
        
        return {
            "result": result,
            "status": "success"
        }
    
    def _do_something(self, param: str) -> str:
        """实际的插件逻辑"""
        return f"处理了: {param}"
```

### 步骤2：注册插件

在系统启动时注册你的插件：

```python
from backend.plugins.plugin_manager import PluginManager
from backend.plugins.my_plugin import MyCustomPlugin

# 创建插件实例
my_plugin = MyCustomPlugin(api_key="your-key")

# 注册到插件管理器
plugin_manager.register(my_plugin)
```

## API 接口

### 获取插件列表

```bash
GET /plugins/list
```

**响应**：
```json
{
  "plugins": ["get_weather", "get_latest_news", "my_plugin"],
  "count": 3,
  "schemas": [...]
}
```

### 获取使用统计

```bash
GET /plugins/stats
```

**响应**：
```json
{
  "total_plugins": 3,
  "enabled_plugins": 3,
  "total_calls": 125,
  "plugins": [...]
}
```

### 获取插件调用历史

```bash
GET /plugins/{plugin_name}/history?limit=20
```

## 使用场景示例

### 场景1：情感陪伴 + 实用帮助

**对话流程**：
```
用户："我明天要出差，心里有点紧张"
↓
AI检测到"出差"和"紧张"
↓
AI调用 get_weather 插件查询目的地天气
↓
AI生成融合回复："我理解你出差的紧张心情。我帮你查了目的地的天气，明天晴朗舒适，温度22℃，很适合出行。放轻松，把需要的东西列个清单，一项项打勾会很有安全感哦~"
```

### 场景2：主动关怀 + 新闻推送

**对话流程**：
```
用户："最近工作压力很大，感觉有点迷茫"
↓
AI感知到"压力"和"迷茫"
↓
AI调用 get_latest_news(category="health") 推送心理健康文章
↓
AI回复："我感受到你现在的压力和迷茫。我为你找了几篇关于压力管理的文章，希望能给你一些启发。想聊聊具体是什么让你感到迷茫吗？"
```

## 安全与权限控制

### 插件分级

1. **只读类插件**（低权限）
   - 天气查询、新闻阅读、信息检索
   - 无需用户授权即可使用

2. **写入类插件**（高权限）
   - 发送邮件、设置提醒、修改数据
   - 需用户明确授权

### 调用限制

- 每个插件每日调用次数限制
- API 调用频率控制
- 沙箱环境隔离（未来实现）

## 最佳实践

### 1. 插件设计原则

- **单一职责**：每个插件只做一件事
- **可复用性**：参数化设计，支持多场景
- **错误处理**：优雅降级，提供备选方案
- **文档完善**：清晰的 schema 定义

### 2. 性能优化

- 缓存常用数据
- 异步调用 API
- 批量处理请求

### 3. 用户体验

- 插件调用对用户透明
- AI 自然融合插件结果到对话中
- 失败时提供友好的备用回复

## 未来扩展

1. **更多实用插件**：
   - 日程管理插件
   - 音乐播放插件
   - 邮件发送插件

2. **插件市场**：
   - 第三方开发者提交插件
   - 用户按需安装
   - 插件评级和推荐

3. **智能编排**：
   - 多个插件组合使用
   - 插件调用链优化
   - 自动触发条件设定

## 故障排查

### 插件未注册

**问题**：重启后插件消失
**解决**：检查插件初始化代码是否在系统启动时执行

### API 调用失败

**问题**：天气/新闻查询返回错误
**解决**：
1. 检查 API 密钥是否配置
2. 验证网络连接
3. 查看日志获取详细错误信息

### Function Calling 不工作

**问题**：AI 没有调用插件
**解决**：
1. 检查 function_schema 定义是否正确
2. 确认 LLM 模型支持 Function Calling
3. 查看 API 响应的 function_call 字段

## 贡献指南

欢迎贡献新插件！请遵循以下步骤：

1. Fork 本项目
2. 创建新插件类，继承 `BasePlugin`
3. 实现 `function_schema` 和 `execute` 方法
4. 编写测试用例
5. 提交 Pull Request

## 许可证

本项目采用 MIT 许可证。
