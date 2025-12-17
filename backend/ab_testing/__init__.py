"""
A/B测试框架模块
提供分流、埋点、数据分析等功能
"""

from .ab_test_manager import ABTestManager, ABTestConfig
from .group_assigner import GroupAssigner
from .event_logger import EventLogger, EventType
from .analyzer import ABTestAnalyzer

__all__ = [
    "ABTestManager",
    "ABTestConfig",
    "GroupAssigner", 
    "EventLogger",
    "EventType",
    "ABTestAnalyzer"
]

