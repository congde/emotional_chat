#!/usr/bin/env python3
"""
性能优化示例
展示如何使用性能优化功能
"""

import asyncio
import time
import json
import requests
from typing import Dict, List, Any
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.services.performance_optimizer import performance_optimizer
from backend.services.optimized_chat_service import optimized_chat_service
from backend.config.performance_config import performance_config


async def test_parallel_processing():
    """测试并行处理"""
    print("🔄 测试并行处理...")
    
    # 模拟情感分析器
    class MockEmotionAnalyzer:
        async def analyze(self, text):
            await asyncio.sleep(0.1)  # 模拟处理时间
            return {"emotion": "positive", "intensity": 7.5}
    
    # 模拟安全检查器
    class MockSafetyChecker:
        async def check(self, text):
            await asyncio.sleep(0.05)  # 模拟处理时间
            return {"safe": True, "confidence": 0.95}
    
    # 模拟记忆检索器
    class MockMemoryRetriever:
        async def retrieve(self, text):
            await asyncio.sleep(0.2)  # 模拟处理时间
            return {"relevant_memories": ["用户之前提到过类似的话题"]}
    
    # 创建模拟器
    emotion_analyzer = MockEmotionAnalyzer()
    safety_checker = MockSafetyChecker()
    memory_retriever = MockMemoryRetriever()
    
    # 测试并行处理
    start_time = time.time()
    result = await performance_optimizer.parallel_processing(
        "我今天心情很好！",
        emotion_analyzer,
        safety_checker,
        memory_retriever
    )
    end_time = time.time()
    
    print(f"✅ 并行处理完成")
    print(f"   处理时间: {result['processing_time']:.3f}s")
    print(f"   总时间: {end_time - start_time:.3f}s")
    print(f"   情感分析: {result['emotion']}")
    print(f"   安全检查: {result['safety']}")
    print(f"   记忆检索: {result['memory']}")


async def test_caching():
    """测试缓存机制"""
    print("\n💾 测试缓存机制...")
    
    # 测试缓存设置和获取
    test_key = "test:cache:example"
    test_value = {"message": "这是一个测试缓存", "timestamp": time.time()}
    
    # 设置缓存
    performance_optimizer.redis_client.setex(
        test_key, 
        60,  # 60秒TTL
        json.dumps(test_value)
    )
    
    # 获取缓存
    cached = performance_optimizer.redis_client.get(test_key)
    if cached:
        cached_data = json.loads(cached)
        print(f"✅ 缓存获取成功: {cached_data}")
    else:
        print("❌ 缓存获取失败")
    
    # 测试缓存性能
    cache_key = performance_optimizer.cache_key("test", "重复的测试内容")
    
    # 第一次计算（无缓存）
    start_time = time.time()
    result1 = await performance_optimizer._get_or_compute(
        cache_key,
        lambda: asyncio.sleep(0.1) or "计算结果"
    )
    first_time = time.time() - start_time
    
    # 第二次计算（有缓存）
    start_time = time.time()
    result2 = await performance_optimizer._get_or_compute(
        cache_key,
        lambda: asyncio.sleep(0.1) or "计算结果"
    )
    second_time = time.time() - start_time
    
    print(f"✅ 缓存性能测试")
    print(f"   首次计算时间: {first_time:.3f}s")
    print(f"   缓存命中时间: {second_time:.3f}s")
    print(f"   性能提升: {first_time/second_time:.1f}x")


async def test_streaming_response():
    """测试流式响应"""
    print("\n🌊 测试流式响应...")
    
    # 模拟LLM客户端
    class MockLLMClient:
        async def stream(self, prompt):
            words = ["你好", "，", "我", "是", "你", "的", "AI", "助手", "，", "很", "高兴", "为", "你", "服务", "！"]
            for word in words:
                yield word
                await asyncio.sleep(0.1)  # 模拟生成延迟
    
    mock_llm = MockLLMClient()
    
    print("   流式输出:")
    async for chunk in performance_optimizer.stream_response("测试提示", mock_llm):
        if chunk.startswith("data: "):
            token = chunk[6:].strip()
            if token and token != "[DONE]":
                print(f"   {token}", end="", flush=True)
    
    print("\n✅ 流式响应测试完成")


async def test_fallback_strategy():
    """测试降级策略"""
    print("\n🛡️ 测试降级策略...")
    
    # 测试不同类型的降级策略
    error_types = [
        "llm_timeout",
        "memory_timeout", 
        "vector_error",
        "general_error"
    ]
    
    for error_type in error_types:
        fallback_response = performance_optimizer.fallback_strategy(
            error_type, "用户输入"
        )
        print(f"   {error_type}: {fallback_response}")
    
    print("✅ 降级策略测试完成")


async def test_performance_monitoring():
    """测试性能监控"""
    print("\n📊 测试性能监控...")
    
    # 获取性能指标
    metrics = performance_optimizer.get_performance_metrics()
    print(f"   性能指标: {json.dumps(metrics, indent=2, ensure_ascii=False)}")
    
    # 测试性能监控装饰器
    @performance_optimizer.performance_monitor
    async def test_function(delay: float):
        await asyncio.sleep(delay)
        return "测试完成"
    
    # 测试正常执行
    result = await test_function(0.1)
    print(f"   正常执行结果: {result}")
    
    # 测试慢查询
    result = await test_function(0.5)
    print(f"   慢查询结果: {result}")
    
    print("✅ 性能监控测试完成")


async def test_optimized_chat_service():
    """测试优化的聊天服务"""
    print("\n🤖 测试优化的聊天服务...")
    
    # 模拟聊天请求
    chat_request = {
        "message": "我今天心情不太好，能给我一些建议吗？",
        "session_id": "test_session_001",
        "user_id": "test_user_001"
    }
    
    try:
        # 测试优化的聊天处理
        start_time = time.time()
        response = await optimized_chat_service.chat_optimized(chat_request)
        end_time = time.time()
        
        print(f"✅ 优化聊天处理完成")
        print(f"   处理时间: {end_time - start_time:.3f}s")
        print(f"   响应: {response.get('response', '无响应')[:100]}...")
        print(f"   优化启用: {response.get('optimization_enabled', False)}")
        
    except Exception as e:
        print(f"❌ 聊天服务测试失败: {e}")


async def test_health_check():
    """测试健康检查"""
    print("\n🏥 测试健康检查...")
    
    try:
        health_status = await optimized_chat_service.health_check_optimized()
        print(f"   健康状态: {health_status['status']}")
        print(f"   检查结果: {json.dumps(health_status['checks'], indent=2, ensure_ascii=False)}")
        
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")


async def test_configuration():
    """测试配置管理"""
    print("\n⚙️ 测试配置管理...")
    
    # 显示当前配置
    all_config = performance_config.get_all_config()
    print("   当前配置:")
    for category, config in all_config.items():
        print(f"   {category}: {config}")
    
    # 验证配置
    is_valid = performance_config.validate_config()
    print(f"   配置有效性: {'✅ 有效' if is_valid else '❌ 无效'}")


async def main():
    """主函数"""
    print("🚀 开始性能优化功能测试")
    print("=" * 60)
    
    try:
        # 运行所有测试
        await test_parallel_processing()
        await test_caching()
        await test_streaming_response()
        await test_fallback_strategy()
        await test_performance_monitoring()
        await test_optimized_chat_service()
        await test_health_check()
        await test_configuration()
        
        print("\n" + "=" * 60)
        print("✅ 所有性能优化测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 运行测试
    asyncio.run(main())
