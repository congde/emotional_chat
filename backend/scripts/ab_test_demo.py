#!/usr/bin/env python3
"""
A/B测试演示脚本
演示如何创建实验、分配用户、记录事件和分析结果
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.ab_testing import ABTestManager, ABTestConfig
from backend.ab_testing.event_logger import EventLogger, EventType
from backend.logging_config import get_logger

logger = get_logger(__name__)


def demo_model_comparison():
    """
    演示：模型选型对比实验（GPT-4 vs 微调Llama3）
    """
    print("=" * 80)
    print("A/B测试演示：模型选型对比")
    print("=" * 80)
    
    # 创建实验配置
    experiment_id = "model_comparison_20250101"
    config = ABTestConfig(
        experiment_id=experiment_id,
        name="模型选型对比：GPT-4 vs 微调Llama3",
        description="对比GPT-4和微调Llama3在情感陪伴场景下的表现",
        groups=["A", "B"],
        weights=[0.5, 0.5],
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=7),
        enabled=True,
        metadata={
            "group_A_model": "gpt-4-turbo",
            "group_B_model": "llama3-8b-finetuned",
            "target_sample_size": 500
        }
    )
    
    # 初始化管理器
    manager = ABTestManager()
    manager.register_experiment(config)
    
    # 模拟用户分配和对话
    print("\n模拟用户分配和对话...")
    test_users = [f"user_{i}" for i in range(10)]
    
    for user_id in test_users:
        # 分配组
        group = manager.assign_user_to_group(user_id, experiment_id)
        print(f"用户 {user_id} 分配到 {group} 组")
        
        # 模拟对话
        session_id = f"session_{user_id}_{int(time.time())}"
        user_message = "今天工作上出了一个大错误，被领导当众批评了，感觉特别丢人。"
        
        # 模拟响应（根据组选择不同模型）
        if group == "A":
            bot_response = "我理解你现在很难受。被当众批评确实会让人感到尴尬和挫败。"
            model_used = "gpt-4-turbo"
            response_time = 1.2
        else:
            bot_response = "听起来你很失望，努力了却没得到回报确实很难受。要不要聊聊发生了什么？"
            model_used = "llama3-8b-finetuned"
            response_time = 0.8
        
        # 记录响应事件
        manager.log_response(
            user_id=user_id,
            experiment_id=experiment_id,
            session_id=session_id,
            user_message=user_message,
            bot_response=bot_response,
            response_time=response_time,
            model_used=model_used
        )
        
        # 模拟用户评分
        import random
        rating = random.uniform(3.5, 5.0) if group == "B" else random.uniform(3.0, 4.5)
        manager.log_rating(
            user_id=user_id,
            experiment_id=experiment_id,
            session_id=session_id,
            rating=rating
        )
    
    print("\n演示完成！")
    print(f"事件日志已保存到: logs/ab_test_events.jsonl")
    print("可以使用 ab_test_analysis.py 脚本分析数据")


def demo_prompt_comparison():
    """
    演示：Prompt工程对比实验（结构化 vs 自由式）
    """
    print("=" * 80)
    print("A/B测试演示：Prompt工程对比")
    print("=" * 80)
    
    experiment_id = "prompt_comparison_20250101"
    config = ABTestConfig(
        experiment_id=experiment_id,
        name="Prompt工程对比：结构化 vs 自由式",
        description="对比结构化Prompt和自由式Prompt的效果",
        groups=["A", "B"],
        weights=[0.5, 0.5],
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=7),
        enabled=True,
        metadata={
            "group_A_prompt_type": "free_style",
            "group_B_prompt_type": "structured",
            "target_sample_size": 300
        }
    )
    
    manager = ABTestManager()
    manager.register_experiment(config)
    
    print("\n实验已创建，可以开始收集数据...")
    print("实验ID:", experiment_id)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="A/B测试演示脚本")
    parser.add_argument(
        "--demo",
        type=str,
        choices=["model", "prompt", "all"],
        default="model",
        help="要运行的演示类型"
    )
    
    args = parser.parse_args()
    
    if args.demo == "model" or args.demo == "all":
        demo_model_comparison()
    
    if args.demo == "prompt" or args.demo == "all":
        demo_prompt_comparison()


if __name__ == "__main__":
    main()

