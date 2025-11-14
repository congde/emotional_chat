#!/usr/bin/env python3
"""
测试天气插件
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.plugins.weather_plugin import WeatherPlugin
from backend.plugins.plugin_manager import PluginManager

def test_weather_plugin():
    """测试天气插件"""
    print("=" * 50)
    print("测试天气插件")
    print("=" * 50)
    
    # 检查环境变量
    print("\n1. 检查环境变量:")
    openweather_key = os.getenv("OPENWEATHER_API_KEY")
    hefeng_key = os.getenv("HEFENG_WEATHER_API_KEY")
    weather_key = os.getenv("WEATHER_API_KEY")
    
    print(f"   OPENWEATHER_API_KEY: {'已设置' if openweather_key else '未设置'}")
    print(f"   HEFENG_WEATHER_API_KEY: {'已设置' if hefeng_key else '未设置'}")
    print(f"   WEATHER_API_KEY: {'已设置' if weather_key else '未设置'}")
    
    # 创建插件
    print("\n2. 创建天气插件:")
    try:
        weather_plugin = WeatherPlugin()
        print(f"   ✓ 插件创建成功")
        print(f"   插件名称: {weather_plugin.name}")
        print(f"   插件描述: {weather_plugin.description}")
        print(f"   是否启用: {weather_plugin.enabled}")
        print(f"   API密钥: {'已设置' if weather_plugin.api_key else '未设置'}")
        print(f"   使用OpenWeather: {weather_plugin.use_openweather}")
        print(f"   API地址: {weather_plugin.base_url}")
    except Exception as e:
        print(f"   ✗ 插件创建失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 测试函数schema
    print("\n3. 测试函数Schema:")
    try:
        schema = weather_plugin.function_schema
        print(f"   ✓ Schema获取成功")
        print(f"   函数名: {schema.get('name')}")
        print(f"   描述: {schema.get('description')}")
    except Exception as e:
        print(f"   ✗ Schema获取失败: {e}")
        return
    
    # 测试插件执行
    print("\n4. 测试插件执行 (查询深圳天气):")
    try:
        result = weather_plugin.execute(location="深圳")
        print(f"   执行结果:")
        print(f"   {result}")
        
        if "error" in result:
            print(f"\n   ✗ 查询失败: {result['error']}")
        else:
            print(f"\n   ✓ 查询成功!")
            print(f"   地点: {result.get('location')}")
            print(f"   温度: {result.get('temperature')}℃")
            print(f"   天气: {result.get('description')}")
            print(f"   湿度: {result.get('humidity')}%")
    except Exception as e:
        print(f"   ✗ 执行失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试插件管理器
    print("\n5. 测试插件管理器:")
    try:
        plugin_manager = PluginManager()
        plugin_manager.register(weather_plugin)
        print(f"   ✓ 插件已注册到管理器")
        
        schemas = plugin_manager.get_function_schemas()
        print(f"   可用函数数量: {len(schemas)}")
        for schema in schemas:
            print(f"     - {schema.get('name')}: {schema.get('description')[:50]}...")
        
        # 测试执行
        print("\n6. 通过管理器执行插件:")
        result = plugin_manager.execute_plugin("get_weather", location="北京")
        if "error" in result:
            print(f"   ✗ 执行失败: {result['error']}")
        else:
            print(f"   ✓ 执行成功!")
            print(f"   结果: {result}")
    except Exception as e:
        print(f"   ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_weather_plugin()

