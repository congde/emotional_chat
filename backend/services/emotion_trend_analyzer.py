#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
情绪趋势分析器
支持多维度情绪建模、趋势预测和可视化数据生成
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from backend.database import DatabaseManager, ChatMessage

logger = logging.getLogger(__name__)


class EmotionTrendAnalyzer:
    """
    情绪趋势分析器
    分析用户的情绪变化趋势、模式识别和风险预警
    """
    
    def __init__(self):
        """初始化情绪趋势分析器"""
        self.db_manager = DatabaseManager()
        logger.info("✓ 情绪趋势分析器初始化完成")
    
    def analyze_user_emotion_trend(
        self,
        user_id: str,
        days: int = 7,
        include_visualization_data: bool = True
    ) -> Dict[str, Any]:
        """
        分析用户的情绪趋势
        
        Args:
            user_id: 用户ID
            days: 分析的天数
            include_visualization_data: 是否包含可视化数据
        
        Returns:
            情绪趋势分析结果
        """
        try:
            with DatabaseManager() as db:
                # 获取指定时间范围内的消息
                start_date = datetime.now() - timedelta(days=days)
                
                messages = db.db.query(ChatMessage)\
                    .filter(ChatMessage.user_id == user_id)\
                    .filter(ChatMessage.role == 'user')\
                    .filter(ChatMessage.created_at >= start_date)\
                    .order_by(ChatMessage.created_at.asc())\
                    .all()
                
                if not messages:
                    return self._empty_trend_result()
                
                # 提取情绪数据
                emotions = []
                intensities = []
                timestamps = []
                
                for msg in messages:
                    if msg.emotion:
                        emotions.append(msg.emotion)
                        intensities.append(msg.emotion_intensity or 5.0)
                        timestamps.append(msg.created_at)
                
                if not emotions:
                    return self._empty_trend_result()
                
                # 1. 基础统计
                emotion_distribution = self._calculate_emotion_distribution(emotions)
                dominant_emotion = max(emotion_distribution, key=emotion_distribution.get)
                average_intensity = sum(intensities) / len(intensities)
                
                # 2. 趋势分析
                trend_analysis = self._analyze_trend(emotions, intensities, timestamps)
                
                # 3. 情绪波动分析
                volatility = self._calculate_volatility(intensities)
                
                # 4. 风险评估
                risk_assessment = self._assess_risk(
                    emotions,
                    intensities,
                    trend_analysis
                )
                
                # 5. 情绪模式识别
                patterns = self._identify_patterns(emotions, timestamps)
                
                # 6. 建议生成
                recommendations = self._generate_recommendations(
                    dominant_emotion,
                    average_intensity,
                    trend_analysis,
                    risk_assessment
                )
                
                result = {
                    "user_id": user_id,
                    "analysis_period": {
                        "start_date": start_date.isoformat(),
                        "end_date": datetime.now().isoformat(),
                        "days": days
                    },
                    "sample_size": len(emotions),
                    "emotion_distribution": emotion_distribution,
                    "dominant_emotion": dominant_emotion,
                    "average_intensity": round(average_intensity, 2),
                    "trend": trend_analysis,
                    "volatility": volatility,
                    "risk_assessment": risk_assessment,
                    "patterns": patterns,
                    "recommendations": recommendations
                }
                
                # 添加可视化数据
                if include_visualization_data:
                    result["visualization_data"] = self._prepare_visualization_data(
                        emotions,
                        intensities,
                        timestamps
                    )
                
                return result
                
        except Exception as e:
            logger.error(f"情绪趋势分析失败: {e}")
            return self._empty_trend_result()
    
    def _calculate_emotion_distribution(self, emotions: List[str]) -> Dict[str, float]:
        """计算情绪分布"""
        total = len(emotions)
        counts = Counter(emotions)
        return {
            emotion: round(count / total, 3)
            for emotion, count in counts.items()
        }
    
    def _analyze_trend(
        self,
        emotions: List[str],
        intensities: List[float],
        timestamps: List[datetime]
    ) -> Dict[str, Any]:
        """
        分析情绪趋势
        
        使用滑动窗口比较早期和近期的情绪状态
        """
        if len(emotions) < 4:
            return {"trend": "insufficient_data", "direction": "unknown"}
        
        # 分成两半：早期 vs 近期
        mid_point = len(emotions) // 2
        early_emotions = emotions[:mid_point]
        recent_emotions = emotions[mid_point:]
        early_intensities = intensities[:mid_point]
        recent_intensities = intensities[mid_point:]
        
        # 计算极性得分
        def emotion_to_polarity(emotion):
            positive = ["happy", "excited", "grateful"]
            negative = ["sad", "angry", "anxious", "frustrated", "lonely"]
            if emotion in positive:
                return 1
            elif emotion in negative:
                return -1
            return 0
        
        early_polarity = sum(emotion_to_polarity(e) for e in early_emotions) / len(early_emotions)
        recent_polarity = sum(emotion_to_polarity(e) for e in recent_emotions) / len(recent_emotions)
        
        early_avg_intensity = sum(early_intensities) / len(early_intensities)
        recent_avg_intensity = sum(recent_intensities) / len(recent_intensities)
        
        # 判断趋势方向
        polarity_change = recent_polarity - early_polarity
        intensity_change = recent_avg_intensity - early_avg_intensity
        
        if polarity_change > 0.3:
            direction = "improving"
            description = "情绪状态呈改善趋势"
        elif polarity_change < -0.3:
            direction = "declining"
            description = "情绪状态呈下降趋势"
        else:
            direction = "stable"
            description = "情绪状态相对稳定"
        
        return {
            "trend": direction,
            "description": description,
            "polarity_change": round(polarity_change, 3),
            "intensity_change": round(intensity_change, 2),
            "early_polarity": round(early_polarity, 3),
            "recent_polarity": round(recent_polarity, 3)
        }
    
    def _calculate_volatility(self, intensities: List[float]) -> Dict[str, Any]:
        """计算情绪波动性"""
        if len(intensities) < 2:
            return {"level": "unknown", "score": 0.0}
        
        # 计算标准差
        mean = sum(intensities) / len(intensities)
        variance = sum((x - mean) ** 2 for x in intensities) / len(intensities)
        std_dev = variance ** 0.5
        
        # 计算相邻点的变化幅度
        changes = [abs(intensities[i] - intensities[i-1]) for i in range(1, len(intensities))]
        avg_change = sum(changes) / len(changes) if changes else 0
        
        # 综合评分
        volatility_score = (std_dev + avg_change) / 2
        
        # 分级
        if volatility_score < 1.5:
            level = "low"
            description = "情绪相对稳定"
        elif volatility_score < 3.0:
            level = "moderate"
            description = "情绪有一定波动"
        else:
            level = "high"
            description = "情绪波动较大"
        
        return {
            "level": level,
            "score": round(volatility_score, 2),
            "std_dev": round(std_dev, 2),
            "avg_change": round(avg_change, 2),
            "description": description
        }
    
    def _assess_risk(
        self,
        emotions: List[str],
        intensities: List[float],
        trend_analysis: Dict
    ) -> Dict[str, Any]:
        """
        风险评估
        
        识别潜在的心理健康风险信号
        """
        risk_level = "low"
        risk_factors = []
        
        # 1. 检查负面情绪比例
        negative_emotions = ["sad", "anxious", "angry", "frustrated", "lonely"]
        negative_count = sum(1 for e in emotions if e in negative_emotions)
        negative_ratio = negative_count / len(emotions)
        
        if negative_ratio > 0.7:
            risk_factors.append("高比例负面情绪")
            risk_level = "high"
        elif negative_ratio > 0.5:
            risk_factors.append("较多负面情绪")
            risk_level = "moderate"
        
        # 2. 检查高强度负面情绪
        high_intensity_negative = sum(
            1 for e, i in zip(emotions, intensities)
            if e in negative_emotions and i >= 7
        )
        
        if high_intensity_negative >= 3:
            risk_factors.append("多次高强度负面情绪")
            risk_level = "high"
        
        # 3. 检查趋势
        if trend_analysis.get("trend") == "declining":
            risk_factors.append("情绪呈下降趋势")
            if risk_level == "low":
                risk_level = "moderate"
        
        # 4. 检查特定高风险情绪
        high_risk_emotions = ["lonely", "anxious"]
        high_risk_count = sum(1 for e in emotions if e in high_risk_emotions)
        
        if high_risk_count > len(emotions) * 0.4:
            risk_factors.append("频繁出现焦虑/孤独情绪")
            risk_level = "high"
        
        # 5. 生成建议
        if risk_level == "high":
            recommendation = "建议关注用户心理状态，考虑提供专业心理支持资源"
        elif risk_level == "moderate":
            recommendation = "建议密切关注，增加关怀和支持"
        else:
            recommendation = "情绪状态良好，保持现有支持"
        
        return {
            "level": risk_level,
            "factors": risk_factors,
            "recommendation": recommendation,
            "negative_emotion_ratio": round(negative_ratio, 3)
        }
    
    def _identify_patterns(
        self,
        emotions: List[str],
        timestamps: List[datetime]
    ) -> Dict[str, Any]:
        """
        识别情绪模式
        
        分析时间模式、循环模式等
        """
        patterns = {}
        
        # 1. 时间段模式（如果有足够数据）
        if len(timestamps) >= 7:
            hour_emotion_map = defaultdict(list)
            for emotion, ts in zip(emotions, timestamps):
                hour_emotion_map[ts.hour].append(emotion)
            
            # 找出特定时间段的主导情绪
            time_patterns = {}
            for hour, hour_emotions in hour_emotion_map.items():
                if len(hour_emotions) >= 2:
                    most_common = Counter(hour_emotions).most_common(1)[0][0]
                    time_patterns[hour] = most_common
            
            if time_patterns:
                patterns["time_of_day"] = time_patterns
        
        # 2. 情绪序列模式（常见的情绪转换）
        if len(emotions) >= 5:
            transitions = []
            for i in range(len(emotions) - 1):
                transitions.append(f"{emotions[i]}->{emotions[i+1]}")
            
            common_transitions = Counter(transitions).most_common(3)
            if common_transitions:
                patterns["common_transitions"] = [
                    {"transition": t, "count": c}
                    for t, c in common_transitions
                ]
        
        # 3. 周期性模式检测（简化版）
        if len(emotions) >= 14:
            # 检查是否有周期性的情绪波动
            # 这里简化为检查相同情绪在相似时间间隔出现
            same_emotion_intervals = defaultdict(list)
            
            for emotion in set(emotions):
                indices = [i for i, e in enumerate(emotions) if e == emotion]
                if len(indices) >= 3:
                    intervals = [indices[i+1] - indices[i] for i in range(len(indices)-1)]
                    avg_interval = sum(intervals) / len(intervals)
                    
                    # 如果间隔相对稳定，可能是周期性的
                    if max(intervals) - min(intervals) < 3:
                        same_emotion_intervals[emotion] = {
                            "average_interval": round(avg_interval, 1),
                            "occurrences": len(indices)
                        }
            
            if same_emotion_intervals:
                patterns["periodic_emotions"] = dict(same_emotion_intervals)
        
        return patterns if patterns else {"found": False, "message": "数据不足以识别明显模式"}
    
    def _generate_recommendations(
        self,
        dominant_emotion: str,
        average_intensity: float,
        trend_analysis: Dict,
        risk_assessment: Dict
    ) -> List[str]:
        """生成个性化建议"""
        recommendations = []
        
        # 基于风险等级的建议
        if risk_assessment["level"] == "high":
            recommendations.append("🔴 高风险警告：建议尽快联系专业心理咨询师或拨打心理援助热线（希望24热线：400-161-9995）")
        
        # 基于趋势的建议
        if trend_analysis["trend"] == "declining":
            recommendations.append("⚠️ 情绪趋势：近期情绪呈下降趋势，建议增加关注和支持")
        elif trend_analysis["trend"] == "improving":
            recommendations.append("✅ 积极趋势：情绪状态持续改善，继续保持！")
        
        # 基于主导情绪的建议
        emotion_recommendations = {
            "sad": "建议增加温暖陪伴，提供情感支持，避免说教式建议",
            "anxious": "建议提供平静稳定的支持，帮助分步骤处理问题",
            "angry": "建议保持接纳态度，先倾听再引导",
            "lonely": "建议强化陪伴感，多使用'我在这里'类似的表达",
            "happy": "继续共享喜悦，可适度引导表达更多积极细节",
            "frustrated": "建议提供新视角，避免直接的励志话语"
        }
        
        if dominant_emotion in emotion_recommendations:
            recommendations.append(f"💡 主导情绪({dominant_emotion})建议：{emotion_recommendations[dominant_emotion]}")
        
        # 基于强度的建议
        if average_intensity >= 7:
            recommendations.append("⚡ 情绪强度较高，需要更多关注和深度共情")
        
        return recommendations if recommendations else ["情绪状态稳定，继续保持日常支持"]
    
    def _prepare_visualization_data(
        self,
        emotions: List[str],
        intensities: List[float],
        timestamps: List[datetime]
    ) -> Dict[str, Any]:
        """
        准备可视化数据
        
        返回适合前端图表展示的数据格式
        """
        # 1. 时间序列数据（情绪强度曲线）
        timeline_data = [
            {
                "timestamp": ts.isoformat(),
                "emotion": emotion,
                "intensity": intensity
            }
            for ts, emotion, intensity in zip(timestamps, emotions, intensities)
        ]
        
        # 2. 情绪分布饼图数据
        emotion_counts = Counter(emotions)
        pie_chart_data = [
            {"emotion": emotion, "count": count, "percentage": round(count/len(emotions)*100, 1)}
            for emotion, count in emotion_counts.most_common()
        ]
        
        # 3. 每日平均强度（柱状图）
        daily_intensity = defaultdict(list)
        for ts, intensity in zip(timestamps, intensities):
            date_key = ts.strftime("%Y-%m-%d")
            daily_intensity[date_key].append(intensity)
        
        bar_chart_data = [
            {
                "date": date,
                "average_intensity": round(sum(intensities) / len(intensities), 2),
                "count": len(intensities)
            }
            for date, intensities in sorted(daily_intensity.items())
        ]
        
        # 4. 情绪转换矩阵（热力图）
        if len(emotions) >= 2:
            transitions = defaultdict(int)
            for i in range(len(emotions) - 1):
                from_emotion = emotions[i]
                to_emotion = emotions[i + 1]
                transitions[(from_emotion, to_emotion)] += 1
            
            heatmap_data = [
                {
                    "from": from_e,
                    "to": to_e,
                    "count": count
                }
                for (from_e, to_e), count in transitions.items()
            ]
        else:
            heatmap_data = []
        
        return {
            "timeline": timeline_data,
            "pie_chart": pie_chart_data,
            "bar_chart": bar_chart_data,
            "heatmap": heatmap_data
        }
    
    def _empty_trend_result(self) -> Dict[str, Any]:
        """返回空结果"""
        return {
            "user_id": None,
            "analysis_period": None,
            "sample_size": 0,
            "emotion_distribution": {},
            "dominant_emotion": "neutral",
            "average_intensity": 0.0,
            "trend": {"trend": "unknown", "description": "数据不足"},
            "volatility": {"level": "unknown", "score": 0.0},
            "risk_assessment": {"level": "unknown", "factors": [], "recommendation": "需要更多数据"},
            "patterns": {},
            "recommendations": ["需要更多交互数据才能进行分析"],
            "visualization_data": None
        }
    
    def get_multi_dimensional_emotion_profile(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """
        获取多维度情绪画像
        
        综合分析用户的情绪特征，生成完整的情绪画像
        
        Args:
            user_id: 用户ID
            days: 分析天数
        
        Returns:
            多维度情绪画像
        """
        try:
            # 1. 获取基础趋势分析
            trend_result = self.analyze_user_emotion_trend(user_id, days, include_visualization_data=False)
            
            if trend_result["sample_size"] == 0:
                return {"error": "数据不足"}
            
            with DatabaseManager() as db:
                start_date = datetime.now() - timedelta(days=days)
                
                messages = db.db.query(ChatMessage)\
                    .filter(ChatMessage.user_id == user_id)\
                    .filter(ChatMessage.role == 'user')\
                    .filter(ChatMessage.created_at >= start_date)\
                    .order_by(ChatMessage.created_at.asc())\
                    .all()
                
                # 2. 情绪稳定性分析
                emotions = [msg.emotion for msg in messages if msg.emotion]
                emotion_changes = sum(1 for i in range(1, len(emotions)) if emotions[i] != emotions[i-1])
                stability_score = 1 - (emotion_changes / len(emotions)) if len(emotions) > 1 else 0.5
                
                # 3. 情绪复杂度（有多少种不同情绪）
                unique_emotions = len(set(emotions))
                emotion_complexity = min(unique_emotions / 10, 1.0)  # 归一化到0-1
                
                # 4. 积极性指数
                positive_emotions = ["happy", "excited", "grateful"]
                positive_count = sum(1 for e in emotions if e in positive_emotions)
                positivity_index = positive_count / len(emotions) if emotions else 0
                
                # 5. 压力指数
                stress_emotions = ["anxious", "frustrated", "angry"]
                stress_count = sum(1 for e in emotions if e in stress_emotions)
                stress_index = stress_count / len(emotions) if emotions else 0
                
                # 6. 社交性指标（基于孤独情绪）
                lonely_count = sum(1 for e in emotions if e == "lonely")
                social_connectedness = 1 - (lonely_count / len(emotions)) if emotions else 0.5
                
                # 7. 情绪弹性（从负面情绪恢复的能力）
                resilience_score = self._calculate_resilience(emotions)
                
                return {
                    "user_id": user_id,
                    "analysis_period_days": days,
                    "sample_size": len(emotions),
                    "dimensions": {
                        "stability": {
                            "score": round(stability_score, 3),
                            "level": "高" if stability_score > 0.7 else "中" if stability_score > 0.4 else "低",
                            "description": "情绪稳定性" if stability_score > 0.7 else "情绪波动较大"
                        },
                        "complexity": {
                            "score": round(emotion_complexity, 3),
                            "unique_emotions": unique_emotions,
                            "description": "情绪体验丰富" if emotion_complexity > 0.6 else "情绪相对单一"
                        },
                        "positivity": {
                            "score": round(positivity_index, 3),
                            "level": "高" if positivity_index > 0.5 else "中" if positivity_index > 0.3 else "低",
                            "description": "积极情绪占主导" if positivity_index > 0.5 else "需要增强积极体验"
                        },
                        "stress": {
                            "score": round(stress_index, 3),
                            "level": "高" if stress_index > 0.4 else "中" if stress_index > 0.2 else "低",
                            "description": "压力水平较高" if stress_index > 0.4 else "压力在可控范围"
                        },
                        "social_connectedness": {
                            "score": round(social_connectedness, 3),
                            "level": "高" if social_connectedness > 0.7 else "中" if social_connectedness > 0.5 else "低",
                            "description": "社交连接良好" if social_connectedness > 0.7 else "可能需要更多社交支持"
                        },
                        "resilience": {
                            "score": round(resilience_score, 3),
                            "level": "高" if resilience_score > 0.6 else "中" if resilience_score > 0.4 else "低",
                            "description": "情绪恢复能力强" if resilience_score > 0.6 else "可能需要支持情绪调节"
                        }
                    },
                    "overall_wellbeing_score": round(
                        (stability_score + positivity_index + social_connectedness + resilience_score - stress_index) / 4, 3
                    ),
                    "key_characteristics": self._generate_characteristics(
                        stability_score, positivity_index, stress_index, social_connectedness, resilience_score
                    )
                }
                
        except Exception as e:
            logger.error(f"多维度情绪画像生成失败: {e}")
            return {"error": str(e)}
    
    def _calculate_resilience(self, emotions: List[str]) -> float:
        """
        计算情绪弹性（从负面情绪恢复的能力）
        
        检测从负面情绪到正面情绪的转换比例
        """
        if len(emotions) < 2:
            return 0.5
        
        negative_emotions = ["sad", "angry", "anxious", "frustrated", "lonely"]
        positive_emotions = ["happy", "excited", "grateful"]
        
        recovery_count = 0
        negative_to_negative = 0
        
        for i in range(len(emotions) - 1):
            if emotions[i] in negative_emotions:
                if emotions[i + 1] in positive_emotions or emotions[i + 1] == "neutral":
                    recovery_count += 1
                elif emotions[i + 1] in negative_emotions:
                    negative_to_negative += 1
        
        total_negative_episodes = recovery_count + negative_to_negative
        
        if total_negative_episodes == 0:
            return 0.8  # 没有负面情绪，弹性默认较高
        
        return recovery_count / total_negative_episodes
    
    def _generate_characteristics(
        self,
        stability: float,
        positivity: float,
        stress: float,
        social: float,
        resilience: float
    ) -> List[str]:
        """生成关键特征描述"""
        characteristics = []
        
        if stability > 0.7:
            characteristics.append("情绪稳定")
        elif stability < 0.4:
            characteristics.append("情绪波动较大")
        
        if positivity > 0.5:
            characteristics.append("乐观积极")
        elif positivity < 0.3:
            characteristics.append("需要积极情绪支持")
        
        if stress > 0.4:
            characteristics.append("压力较高")
        
        if social < 0.5:
            characteristics.append("可能需要社交连接")
        
        if resilience > 0.6:
            characteristics.append("情绪恢复能力强")
        elif resilience < 0.4:
            characteristics.append("需要情绪调节支持")
        
        return characteristics if characteristics else ["情绪状态平衡"]


# 便捷函数
def analyze_emotion_trend(user_id: str, days: int = 7) -> Dict[str, Any]:
    """
    便捷函数：分析用户情绪趋势
    
    Args:
        user_id: 用户ID
        days: 天数
    
    Returns:
        趋势分析结果
    """
    analyzer = EmotionTrendAnalyzer()
    return analyzer.analyze_user_emotion_trend(user_id, days)


def get_emotion_profile(user_id: str, days: int = 30) -> Dict[str, Any]:
    """
    便捷函数：获取多维度情绪画像
    
    Args:
        user_id: 用户ID
        days: 天数
    
    Returns:
        情绪画像
    """
    analyzer = EmotionTrendAnalyzer()
    return analyzer.get_multi_dimensional_emotion_profile(user_id, days)


# 测试代码
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 需要实际的数据库数据才能测试
    print("情绪趋势分析器已就绪")
    print("使用示例:")
    print("  analyzer = EmotionTrendAnalyzer()")
    print("  trend = analyzer.analyze_user_emotion_trend('user_123', days=7)")
    print("  profile = analyzer.get_multi_dimensional_emotion_profile('user_123', days=30)")

