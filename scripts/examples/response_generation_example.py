#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
响应生成模块示例代码
Response Generation Module Examples

展示如何使用响应生成模块的各种功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.modules.intent.core.response_generator import ResponseGenerator
from backend.modules.intent.core.enhanced_input_processor import EnhancedInputProcessor
from backend.emotion_analyzer import EmotionAnalyzer

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    from langchain.chat_models import ChatOpenAI

from config import Config


def example_1_basic_usage():
    """示例1：基础用法"""
    print("\n" + "="*60)
    print("示例1：基础用法")
    print("="*60 + "\n")
    
    # 创建LLM客户端
    llm_client = ChatOpenAI(
        api_key=Config.OPENAI_API_KEY,
        base_url=Config.API_BASE_URL,
        model_name=Config.DEFAULT_MODEL,
        temperature=0.7
    )
    
    # 创建响应生成器
    generator = ResponseGenerator(llm_client)
    
    # 生成回复
    result = generator.generate_response(
        user_input="我今天被领导批评了，觉得自己一无是处",
        user_emotion="sad",
        user_id="user_001",
        emotion_intensity=7.5
    )
    
    print(f"用户: 我今天被领导批评了，觉得自己一无是处")
    print(f"情绪: 悲伤 (强度: 7.5)")
    print(f"\n心语: {result['response']}")
    print(f"\n生成方法: {result['generation_method']}")
    print(f"是否有效: {result['is_valid']}")


def example_2_with_history():
    """示例2：带对话历史"""
    print("\n" + "="*60)
    print("示例2：带对话历史的回复生成")
    print("="*60 + "\n")
    
    llm_client = ChatOpenAI(
        api_key=Config.OPENAI_API_KEY,
        base_url=Config.API_BASE_URL,
        model_name=Config.DEFAULT_MODEL,
        temperature=0.7
    )
    
    generator = ResponseGenerator(llm_client)
    
    # 对话历史
    conversation_history = [
        {"role": "user", "content": "最近工作压力好大"},
        {"role": "assistant", "content": "我能感受到你的压力。工作确实不容易。"},
        {"role": "user", "content": "今天又加班到很晚"},
        {"role": "assistant", "content": "加班确实很辛苦。注意休息哦。"}
    ]
    
    # 生成回复（考虑历史）
    result = generator.generate_response(
        user_input="我觉得快撑不下去了",
        user_emotion="frustrated",
        user_id="user_001",
        emotion_intensity=8.0,
        conversation_history=conversation_history
    )
    
    print("对话历史:")
    for turn in conversation_history:
        role = "用户" if turn["role"] == "user" else "心语"
        print(f"  {role}: {turn['content']}")
    
    print(f"\n用户: 我觉得快撑不下去了")
    print(f"情绪: 沮丧 (强度: 8.0)")
    print(f"\n心语: {result['response']}")


def example_3_with_memory():
    """示例3：结合记忆检索"""
    print("\n" + "="*60)
    print("示例3：结合用户记忆的个性化回复")
    print("="*60 + "\n")
    
    llm_client = ChatOpenAI(
        api_key=Config.OPENAI_API_KEY,
        base_url=Config.API_BASE_URL,
        model_name=Config.DEFAULT_MODEL,
        temperature=0.7
    )
    
    generator = ResponseGenerator(llm_client)
    
    # 模拟检索到的用户记忆
    retrieved_memories = [
        {
            "content": "用户提到自己是程序员，经常加班",
            "importance": 0.8,
            "timestamp": "2025-10-15T10:00:00"
        },
        {
            "content": "用户最近在准备项目上线，压力很大",
            "importance": 0.9,
            "timestamp": "2025-10-17T15:30:00"
        }
    ]
    
    # 生成回复
    result = generator.generate_response(
        user_input="项目终于上线了，但感觉很累",
        user_emotion="frustrated",
        user_id="user_001",
        emotion_intensity=6.0,
        retrieved_memories=retrieved_memories
    )
    
    print("相关记忆:")
    for memory in retrieved_memories:
        print(f"  - {memory['content']}")
    
    print(f"\n用户: 项目终于上线了，但感觉很累")
    print(f"情绪: 沮丧 (强度: 6.0)")
    print(f"\n心语: {result['response']}")


def example_4_user_profile():
    """示例4：使用用户画像"""
    print("\n" + "="*60)
    print("示例4：基于用户画像的个性化回复")
    print("="*60 + "\n")
    
    llm_client = ChatOpenAI(
        api_key=Config.OPENAI_API_KEY,
        base_url=Config.API_BASE_URL,
        model_name=Config.DEFAULT_MODEL,
        temperature=0.7
    )
    
    generator = ResponseGenerator(llm_client)
    
    # 用户画像
    user_profile = {
        "preferred_tone": "温柔、缓慢",
        "avoid_topics": ["家庭"],
        "communication_style": "深度倾听型",
        "emoji_preference": "moderate"
    }
    
    # 生成回复
    result = generator.generate_response(
        user_input="我最近心情不好",
        user_emotion="sad",
        user_id="user_001",
        emotion_intensity=5.5,
        user_profile=user_profile
    )
    
    print("用户画像:")
    for key, value in user_profile.items():
        print(f"  {key}: {value}")
    
    print(f"\n用户: 我最近心情不好")
    print(f"情绪: 悲伤 (强度: 5.5)")
    print(f"\n心语: {result['response']}")


def example_5_crisis_intervention():
    """示例5：危机干预"""
    print("\n" + "="*60)
    print("示例5：危机干预场景")
    print("="*60 + "\n")
    
    llm_client = ChatOpenAI(
        api_key=Config.OPENAI_API_KEY,
        base_url=Config.API_BASE_URL,
        model_name=Config.DEFAULT_MODEL,
        temperature=0.7
    )
    
    generator = ResponseGenerator(llm_client)
    
    # 高风险输入
    crisis_input = "我真的不想活了"
    
    # 模拟预处理结果（包含危机关键词）
    metadata = {
        "requires_crisis_intervention": True,
        "risk_keywords": ["不想活了"]
    }
    
    # 生成回复
    result = generator.generate_response(
        user_input=crisis_input,
        user_emotion="high_risk_depression",
        user_id="user_001",
        emotion_intensity=10.0,
        metadata=metadata
    )
    
    print(f"用户: {crisis_input}")
    print(f"⚠️  检测到高风险：{metadata['risk_keywords']}")
    print(f"\n心语: {result['response']}")
    print(f"\n生成方法: {result['generation_method']}")


def example_6_complete_pipeline():
    """示例6：完整处理流程"""
    print("\n" + "="*60)
    print("示例6：完整的对话处理流程")
    print("="*60 + "\n")
    
    # 初始化各个组件
    input_processor = EnhancedInputProcessor()
    emotion_analyzer = EmotionAnalyzer()
    
    llm_client = ChatOpenAI(
        api_key=Config.OPENAI_API_KEY,
        base_url=Config.API_BASE_URL,
        model_name=Config.DEFAULT_MODEL,
        temperature=0.7
    )
    
    response_generator = ResponseGenerator(llm_client)
    
    # 用户输入
    raw_input = "今天被领导骂了，我好难过啊😭"
    user_id = "user_001"
    
    print(f"原始输入: {raw_input}\n")
    
    # 1. 输入预处理
    print("1️⃣ 输入预处理...")
    processed = input_processor.preprocess(raw_input, user_id)
    
    if processed["blocked"]:
        print(f"   ✗ 输入被阻止: {processed['friendly_message']}")
        return
    
    print(f"   ✓ 清洗后: {processed['cleaned']}")
    print(f"   - 中文占比: {processed['metadata'].get('chinese_ratio', 0):.2%}")
    print(f"   - 关键词: {', '.join(processed['metadata'].get('keywords', [])[:5])}")
    
    # 2. 情感分析
    print("\n2️⃣ 情感分析...")
    emotion_data = emotion_analyzer.analyze_emotion(processed["cleaned"])
    
    print(f"   ✓ 情绪: {emotion_data['emotion']}")
    print(f"   - 强度: {emotion_data['intensity']}/10")
    
    # 3. 响应生成
    print("\n3️⃣ 响应生成...")
    result = response_generator.generate_response(
        user_input=processed["cleaned"],
        user_emotion=emotion_data["emotion"],
        user_id=user_id,
        emotion_intensity=emotion_data["intensity"],
        metadata=processed["metadata"]
    )
    
    print(f"   ✓ 生成方法: {result['generation_method']}")
    print(f"   - 是否有效: {result['is_valid']}")
    
    # 4. 输出回复
    print("\n4️⃣ 最终回复:")
    print(f"   心语: {result['response']}")


def example_7_statistics():
    """示例7：统计信息"""
    print("\n" + "="*60)
    print("示例7：查看生成统计信息")
    print("="*60 + "\n")
    
    llm_client = ChatOpenAI(
        api_key=Config.OPENAI_API_KEY,
        base_url=Config.API_BASE_URL,
        model_name=Config.DEFAULT_MODEL,
        temperature=0.7
    )
    
    generator = ResponseGenerator(llm_client)
    
    # 生成多个回复
    test_cases = [
        ("你好", "neutral", 3.0),
        ("谢谢你", "grateful", 4.0),
        ("我很焦虑", "anxious", 7.0),
        ("再见", "neutral", 3.0)
    ]
    
    for user_input, emotion, intensity in test_cases:
        generator.generate_response(
            user_input=user_input,
            user_emotion=emotion,
            user_id="test_user",
            emotion_intensity=intensity
        )
    
    # 获取统计
    stats = generator.get_statistics()
    
    print("生成统计:")
    print(f"  总计: {stats['total_generations']} 次")
    print(f"  LLM生成: {stats['llm_generated']} 次 ({stats.get('llm_rate', 0):.2%})")
    print(f"  缓存匹配: {stats['cached']} 次 ({stats.get('cached_rate', 0):.2%})")
    print(f"  规则引擎: {stats['rule_based']} 次 ({stats.get('rule_based_rate', 0):.2%})")
    print(f"  一致性失败: {stats['consistency_failures']} 次 ({stats.get('failure_rate', 0):.2%})")


def main():
    """主函数"""
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*15 + "响应生成模块示例集" + " "*15 + "║")
    print("╚" + "="*58 + "╝")
    
    examples = [
        ("基础用法", example_1_basic_usage),
        ("带对话历史", example_2_with_history),
        ("结合记忆", example_3_with_memory),
        ("用户画像", example_4_user_profile),
        ("危机干预", example_5_crisis_intervention),
        ("完整流程", example_6_complete_pipeline),
        ("统计信息", example_7_statistics)
    ]
    
    print("\n可用示例:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    print(f"  0. 运行所有示例")
    
    try:
        choice = input("\n请选择要运行的示例 (0-7): ").strip()
        
        if choice == "0":
            for name, func in examples:
                try:
                    func()
                except Exception as e:
                    print(f"\n✗ 示例 '{name}' 运行失败: {e}")
        elif choice.isdigit() and 1 <= int(choice) <= len(examples):
            idx = int(choice) - 1
            name, func = examples[idx]
            func()
        else:
            print("无效的选择")
    
    except KeyboardInterrupt:
        print("\n\n已取消")
    except Exception as e:
        print(f"\n✗ 运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

