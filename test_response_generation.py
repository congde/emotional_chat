#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
响应生成模块测试脚本
Test Script for Response Generation Module

测试内容：
1. 情感策略加载
2. 动态Prompt构建
3. 情感一致性校验
4. 完整响应生成流程
5. 危机干预触发
6. 缓存匹配
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import yaml
import logging
from backend.modules.intent.core.response_generator import ResponseGenerator
from backend.modules.intent.core.dynamic_prompt_builder import DynamicPromptBuilder
from backend.utils.sentiment_classifier import SentimentClassifier

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MockLLMClient:
    """模拟LLM客户端用于测试"""
    
    def __init__(self):
        self.call_count = 0
        self.prompts_history = []
    
    def predict(self, prompt: str) -> str:
        """模拟LLM生成"""
        self.call_count += 1
        self.prompts_history.append(prompt)
        
        # 根据Prompt中的情绪关键词返回不同回复
        if "悲伤" in prompt or "sad" in prompt.lower():
            return "我能感受到你现在的低落和委屈。被批评的感觉确实很难受，特别是在你已经很努力的时候。我在这里倾听，你并不孤单。💙"
        
        elif "焦虑" in prompt or "anxious" in prompt.lower():
            return "面试前紧张是很正常的反应。这种担心说明你很重视这次机会。深呼吸，慢慢来，我陪你一起准备。🌸"
        
        elif "愤怒" in prompt or "angry" in prompt.lower():
            return "我能理解这件事让你很生气。你有权利表达这种愤怒的感受。想说说具体发生了什么吗？"
        
        elif "喜悦" in prompt or "happy" in prompt.lower():
            return "太好了！看到你这么开心我也很高兴！这是值得庆祝的好事。想和我分享更多吗？🎉"
        
        elif "困惑" in prompt or "confused" in prompt.lower():
            return "做选择时感到困惑是很正常的。我们可以一起慢慢梳理各个选项的利弊。你最担心的是什么呢？💭"
        
        elif "孤独" in prompt or "lonely" in prompt.lower():
            return "在陌生环境中感到孤独是很自然的反应。我在这里陪着你，你并不是一个人。想聊聊你的感受吗？🤗"
        
        else:
            return "我在这里倾听。无论你想说什么，我都愿意听。你今天过得怎么样？😊"


def print_section(title: str):
    """打印分隔标题"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")


def test_strategy_loading():
    """测试1：策略配置加载"""
    print_section("测试1：策略配置加载")
    
    try:
        strategy_file = "/home/workSpace/emotional_chat/backend/config/emotion_strategy.yaml"
        with open(strategy_file, 'r', encoding='utf-8') as f:
            strategy = yaml.safe_load(f)
        
        print("✓ 策略配置加载成功")
        print(f"  - 情感类型数量: {len([k for k in strategy.keys() if k not in ['global_settings', 'default']])}")
        print(f"  - 全局配置: {'存在' if 'global_settings' in strategy else '缺失'}")
        
        # 检查几个关键情绪
        key_emotions = ["sad", "anxious", "happy", "high_risk_depression"]
        for emotion in key_emotions:
            if emotion in strategy:
                s = strategy[emotion]
                print(f"  - {emotion}: 目标='{s.get('goal', '未设置')}', 语气='{s.get('tone', '未设置')}'")
            else:
                print(f"  ✗ {emotion}: 配置缺失")
        
        return True
    except Exception as e:
        print(f"✗ 策略配置加载失败: {e}")
        return False


def test_dynamic_prompt_builder():
    """测试2：动态Prompt构建"""
    print_section("测试2：动态Prompt构建")
    
    try:
        # 加载策略
        strategy_file = "/home/workSpace/emotional_chat/backend/config/emotion_strategy.yaml"
        with open(strategy_file, 'r', encoding='utf-8') as f:
            strategy = yaml.safe_load(f)
        
        # 创建构建器
        builder = DynamicPromptBuilder(strategy)
        
        # 测试用例
        test_case = {
            "user_input": "我今天被领导批评了，觉得自己一无是处",
            "emotion": "sad",
            "emotion_intensity": 7.5,
            "conversation_history": [
                {"role": "user", "content": "最近工作压力好大"},
                {"role": "assistant", "content": "我能感受到你的压力。"}
            ]
        }
        
        # 构建Prompt
        prompt = builder.build_prompt(**test_case)
        
        print("✓ 动态Prompt构建成功")
        print(f"\n生成的Prompt (前500字符):")
        print("-" * 60)
        print(prompt[:500] + "...")
        print("-" * 60)
        
        # 检查关键元素
        checks = [
            ("情绪类型", "悲伤" in prompt or "sad" in prompt),
            ("情绪强度", "7.5" in prompt),
            ("对话历史", "最近工作压力" in prompt),
            ("回应策略", "目标" in prompt or "语气" in prompt)
        ]
        
        print("\n关键元素检查:")
        for check_name, check_result in checks:
            status = "✓" if check_result else "✗"
            print(f"  {status} {check_name}")
        
        return True
    except Exception as e:
        print(f"✗ 动态Prompt构建失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sentiment_classifier():
    """测试3：情感一致性校验"""
    print_section("测试3：情感一致性校验")
    
    try:
        classifier = SentimentClassifier()
        
        # 测试用例
        test_cases = [
            {
                "name": "悲伤情绪-正确回复",
                "user_emotion": "sad",
                "ai_response": "我能感受到你现在的低落。但请相信，你的存在本身就有价值。💙",
                "expected": True
            },
            {
                "name": "悲伤情绪-错误回复",
                "user_emotion": "sad",
                "ai_response": "哈哈，这有什么好难过的，开心点！😄",
                "expected": False
            },
            {
                "name": "焦虑情绪-正确回复",
                "user_emotion": "anxious",
                "ai_response": "深呼吸，慢慢来。我在这里陪着你。🌸",
                "expected": True
            },
            {
                "name": "喜悦情绪-正确回复",
                "user_emotion": "happy",
                "ai_response": "太好了！真为你开心！🎉",
                "expected": True
            }
        ]
        
        passed = 0
        failed = 0
        
        for test in test_cases:
            result = classifier.comprehensive_check(
                test["ai_response"], 
                test["user_emotion"]
            )
            
            is_correct = result["is_valid"] == test["expected"]
            status = "✓" if is_correct else "✗"
            
            if is_correct:
                passed += 1
            else:
                failed += 1
            
            print(f"{status} {test['name']}")
            print(f"   期望: {'通过' if test['expected'] else '不通过'}")
            print(f"   实际: {'通过' if result['is_valid'] else '不通过'}")
            if result["warnings"]:
                print(f"   警告: {', '.join(result['warnings'])}")
            print()
        
        print(f"总计: {passed} 通过, {failed} 失败")
        return failed == 0
        
    except Exception as e:
        print(f"✗ 情感一致性校验测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_response_generation():
    """测试4：完整响应生成流程"""
    print_section("测试4：完整响应生成流程")
    
    try:
        # 创建模拟客户端和生成器
        mock_client = MockLLMClient()
        generator = ResponseGenerator(mock_client)
        
        # 测试用例
        test_cases = [
            {
                "name": "悲伤情绪场景",
                "user_input": "我今天被领导批评了，觉得自己一无是处",
                "user_emotion": "sad",
                "emotion_intensity": 7.5
            },
            {
                "name": "焦虑情绪场景",
                "user_input": "明天要面试，我好紧张",
                "user_emotion": "anxious",
                "emotion_intensity": 6.0
            },
            {
                "name": "喜悦情绪场景",
                "user_input": "我今天升职了！",
                "user_emotion": "happy",
                "emotion_intensity": 8.5
            },
            {
                "name": "困惑情绪场景",
                "user_input": "我不知道该选哪个工作机会",
                "user_emotion": "confused",
                "emotion_intensity": 5.0
            }
        ]
        
        for i, test in enumerate(test_cases, 1):
            print(f"测试场景 {i}: {test['name']}")
            print(f"  用户: {test['user_input']}")
            print(f"  情绪: {test['user_emotion']} (强度: {test['emotion_intensity']})")
            
            result = generator.generate_response(
                user_input=test['user_input'],
                user_emotion=test['user_emotion'],
                user_id="test_user",
                emotion_intensity=test['emotion_intensity']
            )
            
            print(f"  方法: {result['generation_method']}")
            print(f"  心语: {result['response']}")
            print(f"  有效: {'✓' if result['is_valid'] else '✗'}")
            if result['warnings']:
                print(f"  警告: {', '.join(result['warnings'])}")
            print()
        
        # 显示统计
        stats = generator.get_statistics()
        print("统计信息:")
        print(f"  总计生成: {stats['total_generations']}")
        print(f"  LLM生成: {stats['llm_generated']}")
        print(f"  规则生成: {stats['rule_based']}")
        print(f"  缓存匹配: {stats['cached']}")
        print(f"  一致性失败: {stats['consistency_failures']}")
        
        return True
        
    except Exception as e:
        print(f"✗ 响应生成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_crisis_intervention():
    """测试5：危机干预触发"""
    print_section("测试5：危机干预触发")
    
    try:
        mock_client = MockLLMClient()
        generator = ResponseGenerator(mock_client)
        
        # 危机场景测试
        crisis_cases = [
            {
                "user_input": "我真的不想活了",
                "user_emotion": "high_risk_depression",
                "metadata": {"requires_crisis_intervention": True, "risk_keywords": ["不想活了"]}
            },
            {
                "user_input": "我想自杀",
                "user_emotion": "sad",
                "metadata": {"requires_crisis_intervention": True, "risk_keywords": ["自杀"]}
            }
        ]
        
        for i, test in enumerate(crisis_cases, 1):
            print(f"危机场景 {i}:")
            print(f"  用户: {test['user_input']}")
            
            result = generator.generate_response(
                user_input=test['user_input'],
                user_emotion=test['user_emotion'],
                user_id="test_user",
                metadata=test['metadata']
            )
            
            print(f"  方法: {result['generation_method']}")
            print(f"  回复: {result['response'][:100]}...")
            print(f"  是否包含热线: {'✓' if '热线' in result['response'] or '电话' in result['response'] else '✗'}")
            print()
        
        return True
        
    except Exception as e:
        print(f"✗ 危机干预测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cached_responses():
    """测试6：缓存回复匹配"""
    print_section("测试6：缓存回复匹配")
    
    try:
        mock_client = MockLLMClient()
        generator = ResponseGenerator(mock_client, enable_cache=True)
        
        # 缓存场景测试
        cache_cases = [
            {"input": "你好", "emotion": "neutral"},
            {"input": "在吗", "emotion": "neutral"},
            {"input": "谢谢你", "emotion": "grateful"},
            {"input": "再见", "emotion": "neutral"}
        ]
        
        for test in cache_cases:
            result = generator.generate_response(
                user_input=test['input'],
                user_emotion=test['emotion'],
                user_id="test_user"
            )
            
            is_cached = result['generation_method'] == 'cached'
            status = "✓" if is_cached else "○"
            
            print(f"{status} '{test['input']}' -> {result['generation_method']}")
            print(f"   回复: {result['response']}")
            print()
        
        stats = generator.get_statistics()
        print(f"缓存命中率: {stats.get('cached_rate', 0):.2%}")
        
        return True
        
    except Exception as e:
        print(f"✗ 缓存回复测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "响应生成模块测试套件" + " "*15 + "║")
    print("╚" + "="*58 + "╝")
    
    tests = [
        ("策略配置加载", test_strategy_loading),
        ("动态Prompt构建", test_dynamic_prompt_builder),
        ("情感一致性校验", test_sentiment_classifier),
        ("完整响应生成", test_response_generation),
        ("危机干预触发", test_crisis_intervention),
        ("缓存回复匹配", test_cached_responses)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"测试 '{test_name}' 执行异常: {e}")
            results.append((test_name, False))
    
    # 汇总结果
    print_section("测试结果汇总")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status:8} - {test_name}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！响应生成模块运行正常。")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，请检查。")
        return 1


if __name__ == "__main__":
    sys.exit(main())

