# 天气查询插件（Weather Plugin）

## 功能概述

天气查询插件是一个智能的天气信息查询工具，能够根据用户提供的城市名称，查询实时天气信息，并以自然、温暖的语言形式返回给用户。插件支持多种天气数据源，具有自动降级机制，确保在无API密钥的情况下也能正常工作。

## 技术实现

### 核心特性

1. **多数据源支持**
   - **OpenWeatherMap API**（优先）：需要API密钥，提供稳定可靠的天气数据
   - **和风天气 API**（备选）：国内服务，需要API密钥
   - **wttr.in 免费API**（自动降级）：无需API密钥，开箱即用

2. **智能降级策略**
   - 优先使用配置的付费API（OpenWeatherMap > 和风天气）
   - 如果未配置API密钥，自动使用免费的wttr.in API
   - 确保用户在任何情况下都能获取天气信息

3. **完整的数据结构**
   - 地点名称
   - 当前温度（℃）
   - 体感温度（℃）
   - 天气状况描述
   - 湿度（%）
   - 风速（m/s）
   - 气压（hPa）

4. **智能意图识别**
   - 自动检测用户是否在询问天气
   - 从用户输入中提取城市名称
   - 强制调用天气插件，确保准确响应

5. **自然语言生成**
   - 将结构化数据转换为温暖、陪伴式的自然语言
   - 根据天气情况给出贴心的建议
   - 保持"心语"陪伴者的角色定位

## Function Schema

```json
{
  "name": "get_weather",
  "description": "获取指定城市的实时天气信息。用户可以询问某地的天气情况，我会查询并提供详细的天气数据。",
  "parameters": {
    "type": "object",
    "properties": {
      "location": {
        "type": "string",
        "description": "城市名称，例如：北京、上海、杭州、深圳等"
      }
    },
    "required": ["location"]
  }
}
```

## 返回数据结构

插件执行后返回以下格式的JSON数据：

```json
{
  "location": "深圳",
  "temperature": 21.0,
  "description": "Sunny",
  "humidity": 73,
  "wind_speed": 3.3,
  "feels_like": 21.0,
  "pressure": 1019,
  "note": "使用免费的wttr.in API"
}
```

### 字段说明

- `location`: 城市名称（可能被API标准化，如"Shenzhen"）
- `temperature`: 当前温度（摄氏度，保留1位小数）
- `description`: 天气状况描述（如"Sunny"、"Cloudy"、"Rainy"等）
- `humidity`: 相对湿度（百分比，整数）
- `wind_speed`: 风速（米/秒，保留1位小数）
- `feels_like`: 体感温度（摄氏度，保留1位小数）
- `pressure`: 大气压强（百帕，整数）
- `note`: 数据来源说明（可选字段）

## 配置说明

### 环境变量配置（可选）

插件支持通过环境变量配置API密钥，按优先级顺序：

1. **OpenWeatherMap API**（推荐）
   ```bash
   export OPENWEATHER_API_KEY=your_openweather_api_key
   ```
   - 免费额度：1000次/天
   - 注册地址：https://openweathermap.org/api

2. **和风天气 API**
   ```bash
   export HEFENG_WEATHER_API_KEY=your_hefeng_api_key
   # 或
   export WEATHER_API_KEY=your_hefeng_api_key
   ```
   - 免费额度：1000次/天
   - 注册地址：https://dev.qweather.com/

3. **无需配置（默认）**
   - 如果未配置任何API密钥，插件会自动使用免费的wttr.in API
   - 无需注册，无需密钥，开箱即用

### 配置优先级

```
OpenWeatherMap API > 和风天气 API > wttr.in 免费API
```

## 使用示例

### 示例1：基础天气查询

**用户输入：**
```
深圳今天天气
```

**插件调用：**
```json
{
  "name": "get_weather",
  "arguments": {
    "location": "深圳"
  }
}
```

**插件返回：**
```json
{
  "location": "Shenzhen",
  "temperature": 21.0,
  "description": "Sunny",
  "humidity": 73,
  "wind_speed": 3.3,
  "feels_like": 21.0,
  "pressure": 1019,
  "note": "使用免费的wttr.in API"
}
```

**AI最终回复：**
```
深圳今天天气晴朗，气温21℃，体感舒适，是个不错的日子。阳光正好，适合出门走走，但风速有3.3米/秒，早晚稍凉，记得带件薄外套。这样的天气，愿你的心情也像阳光一样明媚。如果需要倾诉或陪伴，我一直都在。
```

### 示例2：未来行程天气查询

**用户输入：**
```
明天去杭州，天气怎么样？
```

**插件调用：**
```json
{
  "name": "get_weather",
  "arguments": {
    "location": "杭州"
  }
}
```

**AI最终回复：**
```
明天杭州的天气有些薄雾，气温17℃，体感也是17℃，整体比较舒适。湿度有68%，风不大，出门时可以带件薄外套。这样的天气适合慢慢走走，但能见度可能稍低，注意出行安全。希望你在杭州度过愉快的一天。
```

### 示例3：错误处理

**场景：** 网络请求失败或城市名称无效

**插件返回：**
```json
{
  "error": "天气查询失败，状态码: 404"
}
```

**AI最终回复：**
```
很抱歉，天气查询遇到了问题。不过我还是想陪伴你，有什么想聊的吗？
```

## 技术细节

### 意图识别机制

系统会自动检测用户输入中的天气相关关键词：
- 中文关键词：天气、温度、下雨、晴天、阴天、气温、降雨、下雪
- 英文关键词：weather
- 城市识别：支持常见城市名称（北京、上海、广州、深圳、杭州等）

当检测到天气查询意图时，系统会：
1. 强制调用 `get_weather` 工具
2. 自动从用户输入中提取城市名称
3. 如果未明确指定城市，使用默认值或提示用户

### 数据格式化

插件结果会被格式化为易读的多行文本：

```
地点：深圳
温度：21.0℃
体感温度：21.0℃
天气状况：Sunny
湿度：73%
风速：3.3m/s
气压：1019hPa
```

这个格式化的文本会被传递给LLM，用于生成最终的自然语言回复。

### 自然语言生成策略

系统会基于天气数据生成包含以下要素的回复：
1. **核心信息**：明确告知天气状况和温度
2. **贴心建议**：根据天气情况给出出行建议
3. **情感陪伴**：保持"心语"的温暖陪伴者角色
4. **个性化**：结合用户的具体场景（如"明天去杭州"）

## 实现文件

- **插件实现**：`backend/plugins/weather_plugin.py`
- **引擎集成**：`backend/modules/llm/core/llm_with_plugins.py`
- **插件管理器**：`backend/plugins/plugin_manager.py`

## 测试方法

### 1. 直接测试插件

```python
from backend.plugins.weather_plugin import WeatherPlugin

plugin = WeatherPlugin()
result = plugin.execute(location="深圳")
print(result)
```

### 2. 通过API测试

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "深圳今天天气",
    "user_id": "test_user"
  }'
```

### 3. 查看调试日志

重启服务后，在日志中查找以下标记：
- `[DEBUG] 检测到天气查询意图`
- `[DEBUG] 执行插件: get_weather`
- `[DEBUG] 插件执行结果`
- `[DEBUG] 最终回复内容`

## 常见问题

### Q: 为什么需要配置API密钥？

A: 虽然插件支持免费的wttr.in API，但配置付费API可以获得：
- 更稳定的服务
- 更高的请求频率限制
- 更准确的数据
- 更好的中文支持

### Q: 免费API有什么限制？

A: wttr.in API是公开服务，没有严格的频率限制，但：
- 建议不要过于频繁地请求
- 可能在某些地区访问较慢
- 数据格式可能与付费API略有差异

### Q: 如何知道当前使用的是哪个API？

A: 查看插件返回结果中的 `note` 字段，或查看服务启动日志。

### Q: 支持哪些城市？

A: 
- 支持全球主要城市
- 支持中文城市名称（如"北京"、"深圳"）
- 支持英文城市名称（如"Beijing"、"Shenzhen"）
- 支持城市+国家格式（如"Beijing,CN"）

## 更新日志

### v1.0.0 (当前版本)
- ✅ 支持 OpenWeatherMap API
- ✅ 支持和风天气 API
- ✅ 集成免费的 wttr.in API（无需密钥）
- ✅ 智能意图识别和强制调用
- ✅ 完整的错误处理和降级机制
- ✅ 自然语言生成和情感陪伴

## 未来计划

- [ ] 支持天气预报（未来几天）
- [ ] 支持天气预警信息
- [ ] 支持空气质量查询
- [ ] 支持更多城市名称识别
- [ ] 缓存机制优化

