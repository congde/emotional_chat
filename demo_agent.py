#!/usr/bin/env python3
"""
Agent演示脚本

演示Agent的核心功能和使用方法
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.agent import AgentCore, get_agent_core


async def main():
    """主演示函数"""
    print("=" * 60)
    print("心语Agent演示")
    print("=" * 60)
    
    # 创建Agent Core实例
    agent = get_agent_core()
    
    # 测试用户ID
    user_id = "demo_user_001"
    
    # 场景1: 情感支持
    print("\n【场景1：情感支持】")
    print("-" * 60)
    result1 = await agent.process(
        user_input="我最近心情很不好，感觉很焦虑",
        user_id=user_id
    )
    print(f"用户：我最近心情很不好，感觉很焦虑")
    print(f"心语：{result1['response']}")
    print(f"情绪：{result1['emotion']} (强度: {result1['emotion_intensity']})")
    print(f"执行了 {len(result1['actions'])} 个行动")
    if result1.get('followup_scheduled'):
        print("✓ 已安排回访")
    
    # 场景2: 问题解决
    print("\n【场景2：问题解决】")
    print("-" * 60)
    result2 = await agent.process(
        user_input="我最近睡不好，怎么办？",
        user_id=user_id
    )
    print(f"用户：我最近睡不好，怎么办？")
    print(f"心语：{result2['response']}")
    print(f"情绪：{result2['emotion']} (强度: {result2['emotion_intensity']})")
    print(f"执行了 {len(result2['actions'])} 个行动")
    if result2.get('followup_scheduled'):
        print("✓ 已安排回访")
    
    # 场景3: 信息查询
    print("\n【场景3：信息查询】")
    print("-" * 60)
    result3 = await agent.process(
        user_input="什么是正念冥想？",
        user_id=user_id
    )
    print(f"用户：什么是正念冥想？")
    print(f"心语：{result3['response']}")
    print(f"情绪：{result3['emotion']} (强度: {result3['emotion_intensity']})")
    
    # 获取Agent状态
    print("\n【Agent状态】")
    print("-" * 60)
    status = agent.get_agent_status()
    print(f"状态: {status['status']}")
    print(f"总交互数: {status['statistics']['total_interactions']}")
    print(f"可用工具数: {status['statistics']['available_tools']}")
    print(f"工作记忆大小: {status['statistics']['working_memory_size']}")
    
    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())


