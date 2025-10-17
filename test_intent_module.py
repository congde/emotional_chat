#!/usr/bin/env python3
"""
意图识别模块测试脚本
Intent Recognition Module Test Script
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.modules.intent.services import IntentService
from backend.modules.intent.models import IntentType

def print_separator(title=""):
    """打印分隔线"""
    print("\n" + "="*70)
    if title:
        print(f"  {title}")
        print("="*70)

def test_basic_intent_detection():
    """测试基本意图识别"""
    print_separator("测试1: 基本意图识别")
    
    # 初始化服务
    intent_service = IntentService()
    
    # 测试用例
    test_cases = [
        ("你好，在吗？", IntentType.CHAT),
        ("我好难过，心情很不好", IntentType.EMOTION),
        ("我该怎么办呢？", IntentType.ADVICE),
        ("提醒我明天吃药", IntentType.FUNCTION),
        ("今天天气不错", IntentType.CONVERSATION),
    ]
    
    print("\n测试各种意图类型：")
    for text, expected_intent in test_cases:
        result = intent_service.analyze(text)
        detected = result['intent']['intent']
        confidence = result['intent']['confidence']
        source = result['intent']['source']
        
        match = "✓" if detected == expected_intent.value else "✗"
        print(f"\n{match} 文本: {text}")
        print(f"  预期意图: {expected_intent.value}")
        print(f"  检测意图: {detected}")
        print(f"  置信度: {confidence:.2f}")
        print(f"  来源: {source}")

def test_crisis_detection():
    """测试危机检测"""
    print_separator("测试2: 危机情况检测")
    
    intent_service = IntentService()
    
    # 危机相关测试用例
    crisis_texts = [
        "我不想活了",
        "我想自杀",
        "活着太累了，不想继续了",
        "撑不下去了"
    ]
    
    print("\n测试危机关键词检测：")
    for text in crisis_texts:
        result = intent_service.analyze(text)
        detected = result['intent']['intent']
        confidence = result['intent']['confidence']
        action_required = result['action_required']
        risk_level = result['processed']['risk_level']
        
        is_crisis = detected == IntentType.CRISIS.value
        symbol = "🚨" if is_crisis else "⚠️"
        
        print(f"\n{symbol} 文本: {text}")
        print(f"  检测意图: {detected}")
        print(f"  置信度: {confidence:.2f}")
        print(f"  需要行动: {action_required}")
        print(f"  风险等级: {risk_level}")

def test_input_processing():
    """测试输入预处理"""
    print_separator("测试3: 输入预处理")
    
    intent_service = IntentService()
    
    # 测试各种输入情况
    test_cases = [
        ("正常输入文本", "正常文本"),
        ("  多余的   空格  ", "空格处理"),
        ("包含不想活的危机词汇", "危机词检测"),
        ("", "空输入"),
    ]
    
    print("\n测试输入预处理功能：")
    for text, description in test_cases:
        result = intent_service.analyze(text)
        processed = result['processed']
        
        print(f"\n测试: {description}")
        print(f"  原始文本: '{text}'")
        print(f"  清洗后: '{processed['cleaned']}'")
        print(f"  是否阻止: {processed['blocked']}")
        print(f"  风险等级: {processed['risk_level']}")
        if processed['warnings']:
            print(f"  警告: {', '.join(processed['warnings'])}")

def test_prompt_building():
    """测试Prompt构建"""
    print_separator("测试4: Prompt构建")
    
    intent_service = IntentService()
    
    # 测试不同意图的Prompt构建
    test_contexts = [
        {
            "analysis": {
                "emotion": {"primary": "焦虑"},
                "intent": {
                    "intent": "advice",
                    "confidence": 0.85,
                    "source": "model"
                }
            }
        },
        {
            "analysis": {
                "emotion": {"primary": "难过"},
                "intent": {
                    "intent": "emotion",
                    "confidence": 0.90,
                    "source": "model"
                }
            }
        },
        {
            "analysis": {
                "emotion": {"primary": "绝望"},
                "intent": {
                    "intent": "crisis",
                    "confidence": 1.0,
                    "source": "rule"
                }
            }
        }
    ]
    
    print("\n测试Prompt构建：")
    for i, context in enumerate(test_contexts, 1):
        prompt = intent_service.build_prompt(context)
        emotion = context['analysis']['emotion']['primary']
        intent = context['analysis']['intent']['intent']
        
        print(f"\n--- 场景 {i} ---")
        print(f"情绪: {emotion}, 意图: {intent}")
        print(f"\n构建的Prompt（前200字符）:")
        print(prompt[:200] + "...")

def test_response_suggestions():
    """测试响应建议"""
    print_separator("测试5: 响应建议生成")
    
    intent_service = IntentService()
    
    # 测试不同意图的响应建议
    test_texts = [
        "你好呀",
        "我好难过",
        "该怎么办？",
        "提醒我吃药",
        "不想活了"
    ]
    
    print("\n测试响应建议：")
    for text in test_texts:
        result = intent_service.analyze(text)
        intent = result['intent']['intent']
        suggestion = result['suggestion']
        
        print(f"\n文本: {text}")
        print(f"意图: {intent}")
        print(f"响应风格: {suggestion['response_style']}")
        print(f"优先级: {suggestion['priority']}")
        print(f"建议行动: {', '.join(suggestion['actions'][:3])}")
        print(f"避免: {', '.join(suggestion['avoid'])}")

def test_batch_processing():
    """测试批量处理"""
    print_separator("测试6: 批量处理")
    
    intent_service = IntentService()
    
    # 批量测试
    texts = [
        "你好",
        "我很焦虑",
        "该怎么办？",
        "今天天气不错",
        "提醒我明天八点起床"
    ]
    
    print(f"\n批量处理 {len(texts)} 条文本：")
    print("-" * 60)
    
    for i, text in enumerate(texts, 1):
        result = intent_service.analyze(text)
        intent = result['intent']['intent']
        confidence = result['intent']['confidence']
        
        print(f"{i}. {text}")
        print(f"   → 意图: {intent} (置信度: {confidence:.2f})")

def run_all_tests():
    """运行所有测试"""
    print("\n")
    print("╔" + "═"*68 + "╗")
    print("║" + " "*15 + "意图识别模块测试套件" + " "*20 + "║")
    print("╚" + "═"*68 + "╝")
    
    try:
        test_basic_intent_detection()
        test_crisis_detection()
        test_input_processing()
        test_prompt_building()
        test_response_suggestions()
        test_batch_processing()
        
        print_separator("测试完成")
        print("\n✅ 所有测试已完成！")
        print("\n提示: 这些是功能测试，实际准确率取决于训练数据和模型质量。")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)

