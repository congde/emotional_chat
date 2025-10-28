"""
插件系统 - 为心语机器人提供可扩展的功能模块
"""
from .base_plugin import BasePlugin
from .weather_plugin import WeatherPlugin
from .news_plugin import NewsPlugin
from .plugin_manager import PluginManager

__all__ = [
    "BasePlugin",
    "WeatherPlugin", 
    "NewsPlugin",
    "PluginManager"
]
