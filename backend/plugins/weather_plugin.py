"""
天气查询插件 - 提供实时天气信息查询功能
"""
import os
import requests
import time
from urllib.parse import quote
from typing import Dict, Any
from .base_plugin import BasePlugin
import logging

logger = logging.getLogger(__name__)


class WeatherPlugin(BasePlugin):
    """天气查询插件 - 使用和风天气API"""
    
    def __init__(self, api_key: str = None):
        # 优先使用 OpenWeatherMap API（如果配置了）
        openweather_key = os.getenv("OPENWEATHER_API_KEY")
        if openweather_key:
            api_key = api_key or openweather_key
            self.use_openweather = True
            self.use_free_api = False
            self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        else:
            # 如果没有提供API key，尝试从环境变量获取和风天气API密钥
            api_key = api_key or os.getenv("HEFENG_WEATHER_API_KEY") or os.getenv("WEATHER_API_KEY")
            if api_key:
                self.use_openweather = False
                self.use_free_api = False
                # 和风天气 API
                self.base_url = "https://devapi.qweather.com/v7/weather/now"
            else:
                # 没有配置API密钥，使用免费的备用API
                self.use_openweather = False
                self.use_free_api = True
                self.base_url = None  # 免费API不需要base_url
                logger.info("未配置天气API密钥，将使用免费的wttr.in API")
        
        super().__init__(
            name="get_weather",
            description="获取指定城市的实时天气信息，包括温度、天气状况、风力、湿度等",
            api_key=api_key
        )
    
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
        
        location = kwargs.get("location")
        if not self.validate_params(**kwargs):
            return {"error": "参数验证失败"}
        
        try:
            if self.use_openweather:
                return self._query_openweather(location)
            elif self.use_free_api:
                return self._query_free_api(location)
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
        
        # 重试配置
        max_retries = 3
        timeout = 20  # 增加超时时间到20秒
        retry_delay = 2  # 初始重试延迟（秒）
        
        last_exception = None
        for attempt in range(max_retries):
            try:
                logger.debug(f"OpenWeatherMap API请求 (尝试 {attempt + 1}/{max_retries}): {location}")
                response = requests.get(self.base_url, params=params, timeout=timeout)
                
                if response.status_code != 200:
                    error_data = response.json() if response.text else {}
                    error_msg = error_data.get("message", f"天气查询失败，状态码: {response.status_code}")
                    logger.warning(f"OpenWeatherMap API错误: {error_msg}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay * (attempt + 1))  # 指数退避
                        continue
                    return {"error": error_msg}
                
                data = response.json()
                
                logger.debug(f"OpenWeatherMap API查询成功: {location}")
                return {
                    "location": data.get("name", location),
                    "temperature": round(data["main"]["temp"], 1),
                    "description": data["weather"][0]["description"] if data.get("weather") else "未知",
                    "humidity": data["main"].get("humidity", 0),
                    "wind_speed": round(data["wind"].get("speed", 0), 1),
                    "feels_like": round(data["main"].get("feels_like", data["main"]["temp"]), 1),
                    "pressure": data["main"].get("pressure", 0)
                }
                
            except requests.exceptions.Timeout as e:
                last_exception = e
                logger.warning(f"OpenWeatherMap API请求超时 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))  # 指数退避
                    continue
                    
            except requests.exceptions.ConnectionError as e:
                last_exception = e
                logger.warning(f"OpenWeatherMap API连接错误 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))  # 指数退避
                    continue
                    
            except requests.exceptions.RequestException as e:
                last_exception = e
                logger.warning(f"OpenWeatherMap API请求异常 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))  # 指数退避
                    continue
                    
            except Exception as e:
                logger.error(f"OpenWeatherMap API解析异常: {e}")
                # 解析错误通常不需要重试
                return {"error": f"数据解析失败: {str(e)}"}
        
        # 所有重试都失败了
        error_msg = "网络请求失败"
        if last_exception:
            if isinstance(last_exception, requests.exceptions.Timeout):
                error_msg = "网络请求超时，请稍后重试"
            elif isinstance(last_exception, requests.exceptions.ConnectionError):
                error_msg = "无法连接到天气服务，请检查网络连接"
            else:
                error_msg = f"网络请求失败: {str(last_exception)}"
        
        logger.error(f"OpenWeatherMap API请求最终失败: {error_msg}")
        return {"error": error_msg}
    
    def _query_free_api(self, location: str) -> Dict[str, Any]:
        """使用免费的wttr.in API查询（无需API密钥）"""
        # 重试配置
        max_retries = 3
        timeout = 20  # 增加超时时间到20秒
        retry_delay = 2  # 初始重试延迟（秒）
        
        # 正确编码城市名称（处理中文等特殊字符）
        encoded_location = quote(location)
        url = f"https://wttr.in/{encoded_location}?format=j1&lang=zh"
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; WeatherBot/1.0)",
            "Accept": "application/json"
        }
        
        # 重试逻辑
        last_exception = None
        for attempt in range(max_retries):
            try:
                logger.debug(f"wttr.in API请求 (尝试 {attempt + 1}/{max_retries}): {location}")
                response = requests.get(url, headers=headers, timeout=timeout)
                
                if response.status_code != 200:
                    logger.warning(f"wttr.in API错误: 状态码 {response.status_code}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay * (attempt + 1))  # 指数退避
                        continue
                    return {"error": f"天气查询失败，状态码: {response.status_code}"}
                
                data = response.json()
                
                # 解析wttr.in的JSON格式
                current = data.get("current_condition", [{}])[0]
                location_info = data.get("nearest_area", [{}])[0]
                
                # 获取城市名称
                city_name = location_info.get("areaName", [{}])[0].get("value", location)
                
                # 温度（摄氏度）
                temp_c = float(current.get("temp_C", 0))
                
                # 天气描述
                weather_desc = current.get("weatherDesc", [{}])[0].get("value", "未知")
                
                # 湿度
                humidity = int(current.get("humidity", 0))
                
                # 风速（km/h）
                wind_speed_kmh = float(current.get("windspeedKmph", 0))
                wind_speed_ms = round(wind_speed_kmh / 3.6, 1)  # 转换为m/s
                
                # 体感温度
                feels_like = float(current.get("FeelsLikeC", temp_c))
                
                # 气压
                pressure = int(current.get("pressure", 0))
                
                logger.debug(f"wttr.in API查询成功: {location} -> {city_name}")
                return {
                    "location": city_name,
                    "temperature": round(temp_c, 1),
                    "description": weather_desc,
                    "humidity": humidity,
                    "wind_speed": wind_speed_ms,
                    "feels_like": round(feels_like, 1),
                    "pressure": pressure,
                    "note": "使用免费的wttr.in API"
                }
                
            except requests.exceptions.Timeout as e:
                last_exception = e
                logger.warning(f"wttr.in API请求超时 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))  # 指数退避
                    continue
                    
            except requests.exceptions.ConnectionError as e:
                last_exception = e
                logger.warning(f"wttr.in API连接错误 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))  # 指数退避
                    continue
                    
            except requests.exceptions.RequestException as e:
                last_exception = e
                logger.warning(f"wttr.in API请求异常 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))  # 指数退避
                    continue
                    
            except Exception as e:
                last_exception = e
                logger.error(f"wttr.in API解析异常: {e}")
                # 解析错误通常不需要重试
                return {"error": f"数据解析失败: {str(e)}"}
        
        # 所有重试都失败了
        error_msg = "网络请求失败"
        if last_exception:
            if isinstance(last_exception, requests.exceptions.Timeout):
                error_msg = "网络请求超时，请稍后重试"
            elif isinstance(last_exception, requests.exceptions.ConnectionError):
                error_msg = "无法连接到天气服务，请检查网络连接"
            else:
                error_msg = f"网络请求失败: {str(last_exception)}"
        
        logger.error(f"wttr.in API请求最终失败: {error_msg}")
        return {"error": error_msg}
    
    def _query_qweather(self, location: str) -> Dict[str, Any]:
        """使用和风天气API查询（需要API密钥）"""
        if not self.api_key:
            # 如果没有API密钥，回退到免费API
            logger.info(f"和风天气API密钥未配置，使用免费API: {location}")
            return self._query_free_api(location)
        
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
