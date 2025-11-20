#!/usr/bin/env python3
"""
Agent测试脚本

测试Agent各个模块的功能
"""

import asyncio
import sys
import os
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.agent import (
    AgentCore, get_agent_core,
    MemoryHub, get_memory_hub,
    Planner,
    ToolCaller, get_tool_caller,
    Reflector, get_reflector
)


async def test_memory_hub():
    """测试记忆中枢"""
    print("\n" + "=" * 60)
    print("测试：Memory Hub")
    print("=" * 60)
    
    memory_hub = get_memory_hub()
    user_id = "test_user_001"
    
    # 测试编码记忆
    memory = memory_hub.encode({
        "content": "我今天心情很好，完成了重要的工作",
        "emotion": {"emotion": "开心", "intensity": 8.0},
        "user_id": user_id,
        "role": "user"
    })
    print(f"✓ 编码记忆: {memory['memory_type']}, 重要性: {memory['importance']}")
    
    # 测试检索记忆
    results = memory_hub.retrieve(
        query="心情",
        user_id=user_id,
        top_k=3
    )
    print(f"✓ 检索到 {len(results)} 条相关记忆")
    
    # 测试用户画像
    profile = memory_hub.get_user_profile(user_id)
    print(f"✓ 获取用户画像: {len(profile)} 个字段")


async def test_planner():
    """测试规划模块"""
    print("\n" + "=" * 60)
    print("测试：Planner")
    print("=" * 60)
    
    planner = Planner()
    
    context = {
        "user_id": "test_user_001",
        "perception": {
            "emotion": "焦虑",
            "emotion_intensity": 7.5,
            "intent": "problem_solving"
        },
        "memories": [],
        "user_profile": {}
    }
    
    plan = await planner.plan("我最近睡不好，怎么办？", context)
    print(f"✓ 生成执行计划")
    print(f"  目标类型: {plan.goal.get('goal_type')}")
    print(f"  策略: {plan.strategy.value}")
    print(f"  步骤数: {len(plan.steps)}")


async def test_tool_caller():
    """测试工具调用器"""
    print("\n" + "=" * 60)
    print("测试：Tool Caller")
    print("=" * 60)
    
    tool_caller = get_tool_caller()
    
    # 列出所有工具
    tools = tool_caller.registry.list_tools()
    print(f"✓ 可用工具数: {len(tools)}")
    for tool in tools[:5]:  # 显示前5个
        print(f"  - {tool.name}: {tool.description[:50]}")
    
    # 测试调用工具
    result = await tool_caller.call(
        "search_memory",
        {
            "query": "睡眠",
            "user_id": "test_user_001",
            "time_range": 7
        }
    )
    print(f"✓ 工具调用结果: {result.get('success')}")


async def test_reflector():
    """测试反思模块"""
    print("\n" + "=" * 60)
    print("测试：Reflector")
    print("=" * 60)
    
    reflector = get_reflector()
    
    # 模拟交互记录
    interaction = {
        "id": "test_interaction_001",
        "user_id": "test_user_001",
        "input": "我最近睡不好",
        "perception": {
            "emotion": "焦虑",
            "emotion_intensity": 7.5
        },
        "plan": {
            "strategy": "tool_use"
        },
        "results": [
            {"type": "tool_call", "success": True},
            {"type": "response", "content": "建议尝试冥想..."}
        ],
        "feedback_score": 0.8,
        "response_time": 1.5,
        "goal_achieved": True
    }
    
    evaluation = await reflector.evaluate(interaction)
    print(f"✓ 评估结果: {evaluation['result']}")
    print(f"  评分: {evaluation['score']:.2f}")
    print(f"  改进建议数: {len(evaluation.get('improvements', []))}")


async def test_agent_core():
    """测试Agent核心"""
    print("\n" + "=" * 60)
    print("测试：Agent Core")
    print("=" * 60)
    
    agent = get_agent_core()
    user_id = "test_user_001"
    
    # 测试完整流程
    result = await agent.process(
        user_input="我最近心情很不好，感觉很焦虑",
        user_id=user_id
    )
    
    print(f"✓ 处理完成")
    print(f"  成功: {result['success']}")
    print(f"  回复长度: {len(result['response'])}")
    print(f"  情绪: {result['emotion']}")
    print(f"  行动数: {len(result['actions'])}")
    
    # 测试状态
    status = agent.get_agent_status()
    print(f"✓ Agent状态: {status['status']}")


async def main():
    """主测试函数"""
    print("=" * 60)
    print("Agent模块测试")
    print("=" * 60)
    
    try:
        await test_memory_hub()
        await test_planner()
        await test_tool_caller()
        await test_reflector()
        await test_agent_core()
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())


