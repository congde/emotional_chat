"""
Agent模块测试脚本

测试Agent Core的各项功能
"""

import asyncio
import json
from datetime import datetime

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "backend"))

from backend.agent import AgentCore


async def test_agent_chat():
    """测试Agent聊天功能"""
    print("=" * 80)
    print("测试1: Agent聊天功能")
    print("=" * 80)
    
    agent = AgentCore()
    user_id = "test_user_001"
    
    # 场景1: 情感支持
    print("\n【场景1：情感支持】")
    print("-" * 80)
    
    result1 = await agent.process(
        user_input="我最近心情很不好，感觉很焦虑",
        user_id=user_id
    )
    
    print(f"用户: 我最近心情很不好，感觉很焦虑")
    print(f"心语: {result1['response']}")
    print(f"检测到情绪: {result1['emotion']} (强度: {result1['emotion_intensity']})")
    print(f"执行了 {len(result1['actions'])} 个行动")
    print(f"响应时间: {result1['response_time']:.2f}秒")
    
    # 场景2: 问题解决
    print("\n【场景2：问题解决】")
    print("-" * 80)
    
    result2 = await agent.process(
        user_input="我最近睡不好，怎么办？",
        user_id=user_id
    )
    
    print(f"用户: 我最近睡不好，怎么办？")
    print(f"心语: {result2['response']}")
    print(f"检测到情绪: {result2['emotion']} (强度: {result2['emotion_intensity']})")
    print(f"执行了 {len(result2['actions'])} 个行动")
    
    # 显示行动详情
    if result2['actions']:
        print("\n执行的行动:")
        for i, action in enumerate(result2['actions'], 1):
            print(f"  {i}. {action.get('type', 'unknown')}: {action.get('tool', 'N/A')}")
    
    if result2.get('followup_scheduled'):
        print("✓ 已安排回访任务")
    
    print(f"响应时间: {result2['response_time']:.2f}秒")
    
    # 场景3: 行为改变
    print("\n【场景3：行为改变】")
    print("-" * 80)
    
    result3 = await agent.process(
        user_input="我打算每天锻炼半小时，改善身体状况",
        user_id=user_id
    )
    
    print(f"用户: 我打算每天锻炼半小时，改善身体状况")
    print(f"心语: {result3['response']}")
    print(f"检测到情绪: {result3['emotion']} (强度: {result3['emotion_intensity']})")
    print(f"执行了 {len(result3['actions'])} 个行动")
    print(f"响应时间: {result3['response_time']:.2f}秒")


async def test_agent_tools():
    """测试Agent工具调用"""
    print("\n" + "=" * 80)
    print("测试2: Agent工具调用")
    print("=" * 80)
    
    from backend.agent import ToolCaller
    
    tool_caller = ToolCaller()
    
    # 列出所有工具
    print("\n可用工具列表:")
    print("-" * 80)
    for i, tool in enumerate(tool_caller.registry.list_tools(), 1):
        print(f"{i}. {tool.name} ({tool.category})")
        print(f"   描述: {tool.description}")
    
    # 测试工具调用
    print("\n测试工具调用:")
    print("-" * 80)
    
    # 1. 搜索记忆
    print("\n1. 搜索记忆:")
    result = await tool_caller.call(
        "search_memory",
        {"query": "睡眠", "user_id": "test_user_001", "time_range": 7}
    )
    print(f"   成功: {result['success']}")
    if result['success']:
        print(f"   找到 {result['result']['count']} 条记忆")
    
    # 2. 推荐冥想
    print("\n2. 推荐冥想:")
    result = await tool_caller.call(
        "recommend_meditation",
        {"theme": "sleep", "duration": 15}
    )
    print(f"   成功: {result['success']}")
    if result['success']:
        print(f"   推荐了 {result['result']['count']} 个冥想练习")
        for rec in result['result']['recommendations']:
            print(f"     - {rec['title']} ({rec['duration']}分钟)")
    
    # 3. 设置提醒
    print("\n3. 设置提醒:")
    result = await tool_caller.call(
        "set_reminder",
        {
            "content": "记得做睡前冥想",
            "user_id": "test_user_001",
            "schedule_time": "2025-10-15T21:30:00",
            "repeat": True
        }
    )
    print(f"   成功: {result['success']}")
    if result['success']:
        print(f"   {result['result']['message']}")


async def test_agent_memory():
    """测试Agent记忆系统"""
    print("\n" + "=" * 80)
    print("测试3: Agent记忆系统")
    print("=" * 80)
    
    from backend.agent import MemoryHub
    
    memory_hub = MemoryHub()
    user_id = "test_user_001"
    
    # 编码记忆
    print("\n1. 编码记忆:")
    print("-" * 80)
    
    memory = memory_hub.encode({
        "content": "我今天考试了，感觉很紧张",
        "emotion": {"emotion": "焦虑", "intensity": 7.5},
        "user_id": user_id
    })
    
    print(f"   内容: {memory['content']}")
    print(f"   情绪: {memory['emotion']}")
    print(f"   重要性: {memory['importance']:.2f}")
    print(f"   记忆类型: {memory['memory_type']}")
    
    # 巩固记忆
    print("\n2. 巩固记忆:")
    print("-" * 80)
    success = memory_hub.consolidate(memory)
    print(f"   巩固{'成功' if success else '失败'}")
    
    # 检索记忆
    print("\n3. 检索记忆:")
    print("-" * 80)
    
    results = memory_hub.retrieve(
        query="考试 紧张",
        user_id=user_id,
        context={"emotion": "焦虑"},
        top_k=3
    )
    
    print(f"   检索到 {len(results)} 条相关记忆")
    for i, mem in enumerate(results, 1):
        print(f"   {i}. {mem.get('content', '')[:50]}...")
    
    # 获取用户画像
    print("\n4. 用户画像:")
    print("-" * 80)
    
    profile = memory_hub.get_user_profile(user_id)
    print(f"   用户ID: {profile.get('user_id', 'N/A')}")
    print(f"   对话总数: {profile.get('total_conversations', 0)}")
    
    emotion_baseline = profile.get('emotion_baseline', {})
    if emotion_baseline:
        print(f"   主导情绪: {emotion_baseline.get('dominant_emotion', 'N/A')}")
        print(f"   平均情绪强度: {emotion_baseline.get('avg_intensity', 0):.2f}")


async def test_agent_planner():
    """测试Agent规划器"""
    print("\n" + "=" * 80)
    print("测试4: Agent规划器")
    print("=" * 80)
    
    from backend.agent import Planner
    
    planner = Planner()
    
    # 测试不同场景的规划
    scenarios = [
        ("我怎么才能睡得更好？", "问题解决场景"),
        ("我好难过", "情感支持场景"),
        ("我打算每天读书", "行为改变场景"),
    ]
    
    for i, (user_input, description) in enumerate(scenarios, 1):
        print(f"\n{i}. {description}")
        print("-" * 80)
        
        context = {
            "user_id": "test_user_001",
            "user_input": user_input,
            "perception": {
                "emotion": "焦虑" if "难过" in user_input else "平静",
                "emotion_intensity": 7.0 if "难过" in user_input else 5.0,
                "intent": "problem_solving"
            }
        }
        
        plan = await planner.plan(user_input, context)
        
        print(f"   用户: {user_input}")
        print(f"   策略: {plan.strategy.value}")
        print(f"   步骤数: {len(plan.steps)}")
        
        for j, step in enumerate(plan.steps, 1):
            print(f"     步骤{j}: {step['action']} - {step.get('tool', 'N/A')}")


async def test_agent_reflector():
    """测试Agent反思器"""
    print("\n" + "=" * 80)
    print("测试5: Agent反思器")
    print("=" * 80)
    
    from backend.agent import Reflector
    
    reflector = Reflector()
    
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
            {"type": "response", "content": "建议尝试冥想"}
        ],
        "feedback_score": 0.8,
        "response_time": 1.5,
        "goal_achieved": True
    }
    
    # 评估交互
    print("\n1. 评估交互:")
    print("-" * 80)
    
    evaluation = await reflector.evaluate(interaction)
    
    print(f"   结果: {evaluation['result']}")
    print(f"   评分: {evaluation['score']:.2f}")
    print(f"   成功: {'是' if evaluation['success'] else '否'}")
    
    analysis = evaluation['analysis']
    if analysis.get('strengths'):
        print(f"   优点: {', '.join(analysis['strengths'])}")
    if analysis.get('weaknesses'):
        print(f"   缺点: {', '.join(analysis['weaknesses'])}")
    if evaluation.get('improvements'):
        print(f"   改进建议: {', '.join(evaluation['improvements'])}")
    
    # 规划回访
    print("\n2. 规划回访:")
    print("-" * 80)
    
    followup = await reflector.plan_followup("test_user_001", {})
    
    if followup:
        print(f"   类型: {followup['type']}")
        print(f"   原因: {followup['reason']}")
        print(f"   消息: {followup['message']}")
        print(f"   时间: {followup['schedule_time']}")
        print(f"   优先级: {followup['priority']}")
    else:
        print("   暂无回访需求")
    
    # 经验总结
    print("\n3. 经验总结:")
    print("-" * 80)
    
    summary = reflector.get_experience_summary(limit=10)
    
    print(f"   交互总数: {summary['total_interactions']}")
    print(f"   成功率: {summary['success_rate']:.2%}")
    if summary.get('common_issues'):
        print(f"   常见问题: {', '.join(summary['common_issues'])}")
    if summary.get('best_practices'):
        print(f"   最佳实践: {', '.join(summary['best_practices'])}")


async def test_agent_status():
    """测试Agent状态"""
    print("\n" + "=" * 80)
    print("测试6: Agent状态")
    print("=" * 80)
    
    agent = AgentCore()
    
    status = agent.get_agent_status()
    
    print("\nAgent状态信息:")
    print("-" * 80)
    print(json.dumps(status, ensure_ascii=False, indent=2))


async def main():
    """主测试函数"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 25 + "心语Agent模块测试" + " " * 25 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    tests = [
        ("Agent聊天功能", test_agent_chat),
        ("Agent工具调用", test_agent_tools),
        ("Agent记忆系统", test_agent_memory),
        ("Agent规划器", test_agent_planner),
        ("Agent反思器", test_agent_reflector),
        ("Agent状态", test_agent_status),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            await test_func()
            passed += 1
            print(f"\n✓ {name} 测试通过")
        except Exception as e:
            failed += 1
            print(f"\n✗ {name} 测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # 总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    print(f"总计: {len(tests)} 个测试")
    print(f"通过: {passed} 个 ✓")
    print(f"失败: {failed} 个 ✗")
    print(f"成功率: {passed/len(tests)*100:.1f}%")
    print()


if __name__ == "__main__":
    asyncio.run(main())

