# -*- coding: utf-8 -*-
"""
TaskPacket — 结构化任务定义

TaskPacket 描述一个业务级任务（不是单次工具调用）。
用于 Lane 并行执行和 DAG 任务图。

Hierarchy:
  TaskPacket (business task) → DAGPlan → DAGTask[] (tool call units)

情感陪伴场景的 TaskPacket 示例：
  - "帮助用户缓解焦虑" → emotion_skill + memory_skill + planning_skill
  - "进行心理健康评估" → tool_skill(assessment) + reflect_skill
  - "安排回访任务" → planning_skill + tool_skill(scheduler)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class TaskPriority(str, Enum):
    """任务优先级"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(str, Enum):
    """任务状态"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class EscalationPolicy:
    """失败处理策略"""

    on_failure: str = "notify"  # "retry" | "degrade" | "notify" | "abort"
    max_retries: int = 1
    notify_channel: str = "default"


@dataclass
class AcceptanceTest:
    """验收标准"""

    name: str
    description: str
    assertion: str  # 评估表达式 (e.g., "output.contains('empathy')")
    required: bool = True


@dataclass
class TaskPacket:
    """
    结构化任务定义 — 描述一个完整的业务任务

    Usage::

        packet = TaskPacket(
            objective="帮助用户缓解焦虑",
            skills=["emotion_skill", "memory_skill", "planning_skill"],
            priority=TaskPriority.HIGH,
        )
    """

    task_id: str = ""
    objective: str = ""
    description: str = ""
    skills: List[str] = field(default_factory=list)  # 需要的 Skill 列表
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    # 上下文
    user_input: str = ""
    user_id: str = ""
    session_id: str = ""
    emotion_context: Dict[str, Any] = field(default_factory=dict)
    # 约束
    max_iterations: int = 10
    timeout_seconds: float = 300.0
    # 策略
    escalation: EscalationPolicy = field(default_factory=EscalationPolicy)
    acceptance_tests: List[AcceptanceTest] = field(default_factory=list)
    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "objective": self.objective,
            "description": self.description,
            "skills": self.skills,
            "priority": self.priority.value,
            "status": self.status.value,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "max_iterations": self.max_iterations,
            "timeout_seconds": self.timeout_seconds,
            "metadata": self.metadata,
        }
