"""
天气查询插件 - 提供实时天气信息查询功能
"""
import os
import requests
from typing import Dict, Any
from .base_plugin import BasePlugin
import logging

logger = logging.getLogger(__name__)


class WeatherPlugin(BasePlugin):
    """天气查询插件 - 使用和风天气API"""
    
    def __init__(self, api_key: str = None):
        # 如果没有提供API key，尝试从环境变量获取
        api_key = api_key or os.getenv("HEFENG_WEATHER_API_KEY") or os.getenv("WEATHER_API_KEY")
        
        super().__init__(
            name="get_weather",
            description="获取指定城市的实时天气信息，包括温度、天气状况、风力、湿度等",
            api_key=api_key
        )
        
        # 如果使用 OpenWeatherMap API（备选）
        self.use_openweather = bool(api_key and os.getenv("OPENWEATHER_API_KEY"))
        
        if self.use_openweather:
            self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        else:
            # 和风天气 API
            self.base_url = "https://devapi.qweather.com/v7/weather/now"
    
    @property
    def function_schema(self) -> Dict[str, Any]:
        """返回 Function Calling 的 JSON Schema"""
        return {
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
    
    def validate_params(self, **kwargs) -> bool:
        """验证参数"""
        location = kwargs.get("location")
        if not location or not isinstance(location, str):
            logger.warning(f"无效的location参数: {location}")
            return False
        return True
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """执行天气查询"""
        if not self.enabled:
            return {"error": "插件已禁用"}
        
        if not self.api_key:
            return {"error": "天气API密钥未配置"}
        
        location = kwargs.get("location")
        if not self.validate_params(**kwargs):
            return {"error": "参数验证失败"}
        
        try:
            if self.use_openweather:
                return self._query_openweather(location)
            else:
                return self._query_qweather(location)
        
        except Exception as e:
            logger.error(f"天气查询失败: {e}")
            return {"error": f"查询失败: {str(e)}"}
    
    def _query_openweather(self, location: str) -> Dict[str, Any]:
        """使用 OpenWeatherMap API 查询"""
        params = {
            'q': location,
            'appid': self.api_key,
            'units': 'metric',  # 摄氏度
            'lang': 'zh_cn'
        }
        
        response = requests.get(self.base_url, params=params, timeout=10)
        
        if response.status_code != 200:
            data = response.json()
            return {"error": data.get("message", "天气查询失败")}
        
        data = response.json()
        
        return {
            "location": data["name"],
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"].get("speed", 0),
            "feels_like": data["main"].get("feels_like"),
            "pressure": data["main"].get("pressure")
        }
    
    def _query_qweather(self, location: str) -> Dict[str, Any]:
        """使用和风天气API查询（示例实现）"""
        # 这里使用模拟数据，实际需要调用和风天气API
        # 和风天气需要先获取location_id，然后查询天气
        
        logger.info(f"查询和风天气（模拟）: {location}")
        
        # 模拟天气数据返回
        return {
            "location": location,
            "temperature": 22,
            "description": "晴",
            "humidity": 50,
            "wind_speed": 3.5,
            "note": "当前使用模拟数据，需要配置和风天气API密钥"
        }
    
    def _get_location_id(self, city_name: str) -> str:
        """获取城市代码（和风天气需要）"""
        # 这里应该调用和风天气的城市搜索API
        # 返回 location_id
        pass
