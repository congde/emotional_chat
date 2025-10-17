"""
情感意图识别模块
Intent Recognition Module for Emotional Chat
"""

from .core.intent_classifier import IntentClassifier
from .core.rule_engine import RuleBasedIntentEngine
from .services.intent_service import IntentService

__all__ = [
    "IntentClassifier",
    "RuleBasedIntentEngine",
    "IntentService",
]

