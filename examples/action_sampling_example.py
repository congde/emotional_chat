#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动作采样示例 - 展示正确的概率采样实现

演示如何使用 torch.distributions.Categorical 进行概率采样
"""

import torch
import torch.distributions as dist


def sample_action_correct(action_probs):
    """
    正确的动作采样方法：使用Categorical分布按概率采样
    
    Args:
        action_probs: 动作概率分布，形状为 [num_actions] 或 [batch_size, num_actions]
        
    Returns:
        action: 采样得到的动作索引
    """
    # 创建以参数probs为标准的类别分布,按概率进行采样
    dist = torch.distributions.Categorical(action_probs)
    action = dist.sample()
    return action


def sample_action_old_style(action_probs):
    """
    旧代码风格（注释不准确）
    
    注意：虽然代码功能相同，但注释容易误导
    """
    # dist = Categorical(action_probs) #归一化动作概率函数
    # #随机选择一个动作
    # action = dist.sample() #随机选择一个动作
    
    dist = torch.distributions.Categorical(action_probs)
    action = dist.sample()
    return action


def demonstrate_sampling():
    """演示概率采样的工作原理"""
    print("=" * 60)
    print("动作概率采样演示")
    print("=" * 60)
    
    # 示例1: 简单的动作概率分布
    print("\n【示例1：简单的动作概率分布】")
    action_probs = torch.tensor([0.1, 0.3, 0.5, 0.1])  # 4个动作，第3个动作概率最高
    print(f"动作概率分布: {action_probs}")
    print(f"概率和: {action_probs.sum().item():.2f}")
    
    # 采样多次，观察分布
    samples = []
    num_samples = 1000
    for _ in range(num_samples):
        action = sample_action_correct(action_probs)
        samples.append(action.item())
    
    # 统计每个动作被选中的次数
    from collections import Counter
    counter = Counter(samples)
    print(f"\n采样 {num_samples} 次的结果:")
    for action_idx in range(len(action_probs)):
        count = counter.get(action_idx, 0)
        prob = count / num_samples
        expected_prob = action_probs[action_idx].item()
        print(f"  动作 {action_idx}: 选中 {count} 次 ({prob:.2%}), 期望概率: {expected_prob:.2%}")
    
    # 示例2: 未归一化的概率（Categorical会自动归一化）
    print("\n【示例2：未归一化的概率（自动归一化）】")
    unnormalized_probs = torch.tensor([1.0, 3.0, 5.0, 1.0])  # 未归一化
    print(f"未归一化的值: {unnormalized_probs}")
    print(f"总和: {unnormalized_probs.sum().item()}")
    
    # Categorical会自动归一化
    dist = torch.distributions.Categorical(unnormalized_probs)
    normalized_probs = dist.probs
    print(f"归一化后的概率: {normalized_probs}")
    print(f"归一化后总和: {normalized_probs.sum().item():.2f}")
    
    # 示例3: 批量采样
    print("\n【示例3：批量采样】")
    batch_size = 5
    batch_action_probs = torch.tensor([
        [0.1, 0.3, 0.5, 0.1],
        [0.2, 0.2, 0.2, 0.4],
        [0.5, 0.3, 0.1, 0.1],
        [0.25, 0.25, 0.25, 0.25],
        [0.7, 0.1, 0.1, 0.1],
    ])
    print(f"批量动作概率分布形状: {batch_action_probs.shape}")
    
    dist_batch = torch.distributions.Categorical(batch_action_probs)
    batch_actions = dist_batch.sample()
    print(f"批量采样结果: {batch_actions}")
    
    # 示例4: 获取采样概率（用于计算log_prob）
    print("\n【示例4：获取采样概率】")
    action_probs = torch.tensor([0.1, 0.3, 0.5, 0.1])
    dist = torch.distributions.Categorical(action_probs)
    action = dist.sample()
    log_prob = dist.log_prob(action)
    prob = dist.probs[action]
    
    print(f"采样动作: {action.item()}")
    print(f"该动作的概率: {prob.item():.4f}")
    print(f"该动作的对数概率: {log_prob.item():.4f}")
    
    print("\n" + "=" * 60)
    print("关键点总结:")
    print("=" * 60)
    print("1. Categorical.sample() 是按概率采样，不是均匀随机")
    print("2. 概率高的动作被选中的概率更高")
    print("3. 如果输入未归一化，Categorical会自动归一化")
    print("4. 可以使用 log_prob() 获取采样动作的对数概率（用于强化学习）")
    print("5. 支持批量采样，提高效率")


if __name__ == "__main__":
    demonstrate_sampling()

