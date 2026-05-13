# -*- coding: utf-8 -*-
"""
PolicyEngine — 声明式规则引擎

设计：
- 策略 = "何时触发什么动作" (workflow 规则)
- 正交于权限 = "谁能做什么" (访问控制)
- 规则按优先级评估 (数字越大 = 优先级越高)
- DENY 动作短路评估
- 支持: deny, ask, alert, retry, degrade, escalate_to_human

情感陪伴场景的典型规则：
1. 危机检测 → escalate_to_human (优先级最高)
2. 敏感内容 → alert + degrade
3. 高频工具调用 → alert
4. 评估低分 → retry

Rule evaluation flow:
  Request → Permission System (access control) → ALLOW/DENY/ASK
                    ↓ ALLOWED
           PolicyEngine (workflow rules) → additional actions (alert/degrade)
                    ↓
                Execute tool
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ActionType(str, Enum):
    """策略动作类型"""

    ALLOW = "allow"
    DENY = "deny"
    ASK = "ask"
    ALERT = "alert"
    RETRY = "retry"
    DEGRADE = "degrade"  # 降级到备用工具/模型
    ESCALATE_TO_HUMAN = "escalate_to_human"  # 升级到人工


@dataclass
class PolicyAction:
    """策略动作"""

    type: ActionType
    params: Dict[str, Any] = field(default_factory=dict)
    reason: str = ""


@dataclass
class PolicyRule:
    """声明式策略规则"""

    rule_id: str
    priority: int  # 数字越大优先级越高
    description: str
    condition: str  # 表达式字符串 (e.g., "tool == 'psychological_assessment' && args.urgency == 'critical'")
    action_chain: List[PolicyAction] = field(default_factory=list)
    enabled: bool = True


class PolicyEngine:
    """
    声明式策略引擎 — 按优先级评估规则并返回动作链

    Usage::

        engine = PolicyEngine(rules=[
            PolicyRule(
                rule_id="crisis_intervention",
                priority=100,
                description="危机干预策略",
                condition="emotion.is_crisis == true",
                action_chain=[
                    PolicyAction(type=ActionType.ESCALATE_TO_HUMAN, reason="检测到危机信号"),
                ],
            ),
        ])
        actions = engine.evaluate({"emotion": {"is_crisis": True}, "tool": "respond"})
        for action in actions:
            if action.type == ActionType.ESCALATE_TO_HUMAN:
                ...
    """

    # 情感陪伴场景的默认规则
    _DEFAULT_RULES: List[PolicyRule] = [
        PolicyRule(
            rule_id="crisis_intervention",
            priority=100,
            description="危机干预 — 检测到自杀/自残信号时升级到人工",
            condition="emotion.is_crisis == true",
            action_chain=[
                PolicyAction(
                    type=ActionType.ESCALATE_TO_HUMAN,
                    params={"urgency": "critical"},
                    reason="检测到危机信号，需要人工介入",
                ),
                PolicyAction(
                    type=ActionType.ALERT,
                    params={"channel": "crisis_team"},
                    reason="通知危机干预团队",
                ),
            ],
        ),
        PolicyRule(
            rule_id="high_intensity_emotion",
            priority=80,
            description="高情绪强度 — 降级到安全回应",
            condition="emotion.intensity >= 9.0",
            action_chain=[
                PolicyAction(
                    type=ActionType.DEGRADE,
                    params={"fallback": "safe_empathy_response"},
                    reason="情绪强度过高，使用安全回应策略",
                ),
            ],
        ),
        PolicyRule(
            rule_id="sensitive_assessment",
            priority=60,
            description="敏感评估 — 心理评估需要确认",
            condition="tool == 'psychological_assessment'",
            action_chain=[
                PolicyAction(
                    type=ActionType.ASK,
                    params={"message": "即将进行心理健康评估，是否继续？"},
                    reason="心理评估需要用户确认",
                ),
            ],
        ),
        PolicyRule(
            rule_id="tool_rate_limit",
            priority=40,
            description="工具频率限制 — 高频调用告警",
            condition="tool_call_count >= 5",
            action_chain=[
                PolicyAction(
                    type=ActionType.ALERT,
                    params={"message": "工具调用频率过高"},
                    reason="可能存在循环调用",
                ),
            ],
        ),
    ]

    def __init__(self, rules: Optional[List[PolicyRule]] = None):
        if rules is not None:
            self._rules: List[PolicyRule] = sorted(rules, key=lambda r: -r.priority)
        else:
            self._rules = sorted(self._DEFAULT_RULES, key=lambda r: -r.priority)

    def register_rule(self, rule: PolicyRule) -> None:
        """注册新规则并按优先级排序"""
        self._rules.append(rule)
        self._rules.sort(key=lambda r: -r.priority)
        logger.info("Registered policy rule '%s' (priority=%d)", rule.rule_id, rule.priority)

    def remove_rule(self, rule_id: str) -> None:
        """移除规则"""
        self._rules = [r for r in self._rules if r.rule_id != rule_id]

    def evaluate(self, context: Dict[str, Any]) -> List[PolicyAction]:
        """
        按优先级评估所有规则，返回触发的动作链

        Args:
            context: 评估上下文，如:
                {
                    "tool": "psychological_assessment",
                    "args": {"urgency": "critical"},
                    "emotion": {"is_crisis": True, "intensity": 8.0},
                    "tool_call_count": 3,
                }

        Returns:
            触发的动作列表（按优先级排序）
        """
        actions: List[PolicyAction] = []

        for rule in self._rules:
            if not rule.enabled:
                continue

            if self._evaluate_condition(rule.condition, context):
                actions.extend(rule.action_chain)
                logger.debug(
                    "Policy rule '%s' triggered: %s",
                    rule.rule_id,
                    rule.description,
                )

                # DENY 短路
                if any(a.type == ActionType.DENY for a in rule.action_chain):
                    break

        return actions

    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """
        评估条件表达式

        支持简单表达式语法：
        - "tool == 'bash'"                    → context["tool"] == "bash"
        - "emotion.is_crisis == true"          → context["emotion"]["is_crisis"] == True
        - "emotion.intensity >= 9.0"           → context["emotion"]["intensity"] >= 9.0
        - "tool_call_count >= 5"               → context["tool_call_count"] >= 5
        """
        try:
            # 解析条件
            # 支持 ==, !=, >=, <=, >, < 操作符
            for op in [">=", "<=", "!=", "==", ">", "<"]:
                if op in condition:
                    parts = condition.split(op, 1)
                    left_path = parts[0].strip()
                    right_value = parts[1].strip()

                    # 获取左值
                    left_value = self._resolve_path(left_path, context)

                    # 解析右值
                    right_parsed = self._parse_value(right_value)

                    # 比较
                    if op == "==":
                        return left_value == right_parsed
                    elif op == "!=":
                        return left_value != right_parsed
                    elif op == ">=":
                        return left_value >= right_parsed
                    elif op == "<=":
                        return left_value <= right_parsed
                    elif op == ">":
                        return left_value > right_parsed
                    elif op == "<":
                        return left_value < right_parsed

            # 无操作符 → 当作布尔值
            value = self._resolve_path(condition, context)
            return bool(value)

        except Exception as e:
            logger.warning("Failed to evaluate condition '%s': %s", condition, e)
            return False

    def _resolve_path(self, path: str, context: Dict[str, Any]) -> Any:
        """解析点分隔路径，如 'emotion.is_crisis' → context['emotion']['is_crisis']"""
        parts = path.split(".")
        value = context
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return None
        return value

    def _parse_value(self, value: str) -> Any:
        """解析字符串值为 Python 类型"""
        value = value.strip()
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False
        if value.startswith("'") and value.endswith("'"):
            return value[1:-1]
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        try:
            return int(value)
        except ValueError:
            pass
        try:
            return float(value)
        except ValueError:
            pass
        return value
