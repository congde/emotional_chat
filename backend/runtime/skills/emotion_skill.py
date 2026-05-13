# -*- coding: utf-8 -*-
"""
EmotionSkill — 情感分析技能

从原 agent_core.py 的"阶段1: 感知层"迁移而来。
将 emotion_analyzer 封装为独立 Skill，可插拔、可开关。

迁移映射：
  原: AgentCore._perceive() → EmotionAnalyzer
  新: EmotionSkill.execute() → EmotionAnalyzer (via Skill Protocol)
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional

from backend.runtime.skills.base import Skill, SkillContext, SkillResult
from backend.runtime.config.guards import is_module_enabled

logger = logging.getLogger(__name__)


class EmotionSkill(Skill):
    """
    情感分析技能 — 感知用户情绪状态

    功能：
    - 情感识别（快乐/悲伤/焦虑/愤怒等）
    - 情绪强度评估 (0-10)
    - 情感趋势追踪
    - 危机信号检测
    """

    def __init__(self, emotion_analyzer=None):
        """
        初始化情感分析技能

        Args:
            emotion_analyzer: 情感分析器实例（可选，延迟加载）
        """
        self._analyzer = emotion_analyzer
        self._crisis_keywords = [
            "不想活", "自杀", "自残", "结束生命",
            "活不下去", "没意思", "想死",
        ]

    @property
    def name(self) -> str:
        return "emotion_skill"

    @property
    def description(self) -> str:
        return "情感分析技能 — 识别用户情绪状态、强度和趋势"

    def is_applicable(self, context: SkillContext) -> bool:
        """情感分析对所有有用户输入的上下文都适用"""
        return bool(context.user_input)

    async def execute(self, context: SkillContext, **kwargs) -> SkillResult:
        """
        执行情感分析

        Args:
            context: 包含 user_input 的上下文

        Returns:
            SkillResult，output 包含 emotion_data:
            {
                "emotion": "sad",
                "emotion_intensity": 7.0,
                "emotion_trend": "declining",
                "is_crisis": False,
                "dominant_emotions": ["sad", "anxious"],
            }
        """
        if not is_module_enabled("emotion_skill"):
            return SkillResult(
                success=True,
                output={"emotion": "neutral", "emotion_intensity": 5.0},
                skill_name=self.name,
            )

        start_ms = time.time() * 1000

        try:
            user_input = context.user_input
            if not user_input:
                return SkillResult(
                    success=True,
                    output={"emotion": "neutral", "emotion_intensity": 5.0},
                    skill_name=self.name,
                )

            # 使用 emotion_analyzer（如果有）
            if self._analyzer:
                emotion_data = await self._analyze_with_analyzer(user_input, context)
            else:
                emotion_data = self._heuristic_analysis(user_input, context)

            # 危机检测
            is_crisis = self._detect_crisis(user_input)
            emotion_data["is_crisis"] = is_crisis

            execution_time = time.time() * 1000 - start_ms

            return SkillResult(
                success=True,
                output=emotion_data,
                emotion_tag=emotion_data.get("emotion", "neutral"),
                confidence=emotion_data.get("confidence", 0.8),
                skill_name=self.name,
                execution_time_ms=execution_time,
            )

        except Exception as e:
            logger.error("EmotionSkill execution failed: %s", e, exc_info=True)
            return SkillResult(
                success=False,
                error=str(e),
                output={"emotion": "neutral", "emotion_intensity": 5.0},
                skill_name=self.name,
                execution_time_ms=time.time() * 1000 - start_ms,
            )

    async def _analyze_with_analyzer(
        self, user_input: str, context: SkillContext
    ) -> Dict[str, Any]:
        """使用 EmotionAnalyzer 进行深度分析"""
        try:
            result = self._analyzer.analyze(user_input)
            if isinstance(result, dict):
                return result
            return {
                "emotion": getattr(result, "emotion", "neutral"),
                "emotion_intensity": getattr(result, "intensity", 5.0),
                "emotion_trend": getattr(result, "trend", "stable"),
                "dominant_emotions": getattr(result, "dominant_emotions", ["neutral"]),
                "confidence": getattr(result, "confidence", 0.8),
            }
        except Exception as e:
            logger.warning("EmotionAnalyzer failed, falling back to heuristic: %s", e)
            return self._heuristic_analysis(user_input, context)

    def _heuristic_analysis(
        self, user_input: str, context: SkillContext
    ) -> Dict[str, Any]:
        """基于规则的情感分析（不依赖 LLM）"""
        # 情绪关键词映射
        emotion_keywords = {
            "happy": ["开心", "高兴", "快乐", "幸福", "喜悦", "好开心"],
            "sad": ["难过", "伤心", "悲伤", "哭", "失落", "沮丧"],
            "anxious": ["焦虑", "担心", "紧张", "害怕", "不安", "忧虑"],
            "angry": ["生气", "愤怒", "烦", "讨厌", "不满", "火大"],
            "grateful": ["谢谢", "感谢", "感恩", "真好"],
            "lonely": ["孤独", "寂寞", "没人", "一个人"],
        }

        detected_emotions = []
        max_intensity = 3.0

        for emotion, keywords in emotion_keywords.items():
            for kw in keywords:
                if kw in user_input:
                    detected_emotions.append(emotion)
                    max_intensity = max(max_intensity, 5.0 + len(user_input) / 100)
                    break

        if not detected_emotions:
            detected_emotions = ["neutral"]

        return {
            "emotion": detected_emotions[0],
            "emotion_intensity": min(max_intensity, 10.0),
            "emotion_trend": "stable",
            "dominant_emotions": detected_emotions[:3],
            "confidence": 0.6 if detected_emotions == ["neutral"] else 0.8,
        }

    def _detect_crisis(self, user_input: str) -> bool:
        """检测危机信号"""
        return any(kw in user_input for kw in self._crisis_keywords)
