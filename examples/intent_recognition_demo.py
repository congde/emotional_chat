#!/usr/bin/env python3
"""
意图识别模块使用示例
Intent Recognition Module Usage Examples
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.modules.intent.services import IntentService
from backend.modules.intent.models import IntentType


def example_1_basic_usage():
    """示例1: 基本使用"""
    print("\n" + "="*70)
    print("示例1: 基本意图识别")
    print("="*70)
    
    # 初始化服务
    intent_service = IntentService()
    
    # 分析用户输入
    text = "我最近睡不好觉，该怎么办？"
    result = intent_service.analyze(text, user_id="user_001")
    
    print(f"\n用户输入: {text}")
    print(f"识别意图: {result['intent']['intent']}")
    print(f"置信度: {result['intent']['confidence']:.2f}")
    print(f"来源: {result['intent']['source']}")
    print(f"响应风格: {result['suggestion']['response_style']}")


def example_2_crisis_detection():
    """示例2: 危机检测"""
    print("\n" + "="*70)
    print("示例2: 危机情况检测")
    print("="*70)
    
    intent_service = IntentService()
    
    # 危机情况
    texts = [
        "我不想活了",
        "我想自杀",
        "生活太累了，撑不下去"
    ]
    
    for text in texts:
        result = intent_service.analyze(text)
        
        print(f"\n输入: {text}")
        print(f"意图: {result['intent']['intent']}")
        print(f"需要行动: {result['action_required']}")
        print(f"风险等级: {result['processed']['risk_level']}")
        
        if result['action_required']:
            print("⚠️ 检测到危机情况！")
            print("建议响应:")
            for action in result['suggestion']['actions'][:3]:
                print(f"  - {action}")


def example_3_prompt_building():
    """示例3: 构建Prompt"""
    print("\n" + "="*70)
    print("示例3: 根据意图构建Prompt")
    print("="*70)
    
    intent_service = IntentService()
    
    # 模拟用户上下文
    user_context = {
        "analysis": {
            "emotion": {"primary": "焦虑"},
            "intent": {
                "intent": "advice",
                "confidence": 0.85,
                "source": "model"
            }
        }
    }
    
    # 构建prompt
    prompt = intent_service.build_prompt(user_context)
    
    print("\n用户上下文:")
    print(f"  情绪: {user_context['analysis']['emotion']['primary']}")
    print(f"  意图: {user_context['analysis']['intent']['intent']}")
    
    print("\n构建的Prompt:")
    print("-" * 70)
    print(prompt)
    print("-" * 70)


def example_4_different_intents():
    """示例4: 不同意图的响应策略"""
    print("\n" + "="*70)
    print("示例4: 各种意图类型的响应策略")
    print("="*70)
    
    intent_service = IntentService()
    
    test_cases = [
        ("你好，在吗？", "chat"),
        ("我好难过", "emotion"),
        ("该怎么办？", "advice"),
        ("提醒我明天8点起床", "function"),
        ("今天去公园散步了", "conversation"),
    ]
    
    for text, expected_intent in test_cases:
        result = intent_service.analyze(text)
        suggestion = result['suggestion']
        
        print(f"\n输入: {text}")
        print(f"检测意图: {result['intent']['intent']}")
        print(f"响应风格: {suggestion['response_style']}")
        print(f"优先级: {suggestion['priority']}")
        print(f"建议行动: {', '.join(suggestion['actions'][:2])}")


def example_5_integration_with_chat():
    """示例5: 集成到聊天流程"""
    print("\n" + "="*70)
    print("示例5: 集成到聊天服务")
    print("="*70)
    
    intent_service = IntentService()
    
    # 模拟聊天流程
    user_message = "我最近压力很大，总是睡不着"
    
    # 1. 意图识别
    intent_analysis = intent_service.analyze(user_message, user_id="user_123")
    
    print(f"\n用户消息: {user_message}")
    print(f"\n步骤1 - 意图识别:")
    print(f"  意图: {intent_analysis['intent']['intent']}")
    print(f"  置信度: {intent_analysis['intent']['confidence']:.2f}")
    
    # 2. 检查是否需要特殊处理
    if intent_analysis['action_required']:
        print("\n步骤2 - 特殊处理:")
        print("  ⚠️ 检测到需要特殊关注的情况")
    else:
        print("\n步骤2 - 正常流程")
    
    # 3. 构建上下文
    user_context = {
        "analysis": {
            "emotion": {"primary": "焦虑"},
            "intent": intent_analysis['intent']
        }
    }
    
    # 4. 生成Prompt
    prompt = intent_service.build_prompt(user_context)
    
    print(f"\n步骤3 - Prompt构建（前150字符）:")
    print(f"  {prompt[:150]}...")
    
    # 5. 后续会调用大模型生成回复
    print(f"\n步骤4 - 调用大模型生成回复 (模拟)")
    print(f"  响应建议: {intent_analysis['suggestion']['response_style']}")


def example_6_batch_processing():
    """示例6: 批量处理"""
    print("\n" + "="*70)
    print("示例6: 批量处理多条消息")
    print("="*70)
    
    intent_service = IntentService()
    
    messages = [
        "你好",
        "我心情不好",
        "该怎么办？",
        "提醒我吃药",
        "今天天气真好",
    ]
    
    print(f"\n批量处理 {len(messages)} 条消息:")
    print("-" * 70)
    
    results = []
    for i, msg in enumerate(messages, 1):
        result = intent_service.analyze(msg)
        results.append(result)
        
        print(f"{i}. {msg:30s} → {result['intent']['intent']:12s} "
              f"({result['intent']['confidence']:.2f})")
    
    print(f"\n处理完成，共 {len(results)} 条")


def main():
    """运行所有示例"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*18 + "意图识别模块使用示例" + " "*18 + "║")
    print("╚" + "="*68 + "╝")
    
    try:
        example_1_basic_usage()
        example_2_crisis_detection()
        example_3_prompt_building()
        example_4_different_intents()
        example_5_integration_with_chat()
        example_6_batch_processing()
        
        print("\n" + "="*70)
        print("所有示例运行完成！")
        print("="*70)
        print("\n更多信息:")
        print("  - 文档: docs/意图识别模块说明.md")
        print("  - 测试: python3 test_intent_module.py")
        print("  - API: http://localhost:8000/intent/")
        print()
        
    except Exception as e:
        print(f"\n❌ 示例运行出错: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

