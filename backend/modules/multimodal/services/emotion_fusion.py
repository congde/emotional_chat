"""
情感融合服务
统一处理多种模态的情感信息，实现多模态情感理解
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional
import numpy as np
from collections import Counter

logger = logging.getLogger(__name__)


class EmotionFusionService:
    """
    情感融合服务
    负责融合文本、语音、图像等多种模态的情感信息
    """
    
    def __init__(self):
        """初始化情感融合服务"""
        # 情感权重配置
        self.emotion_weights = {
            "text": 0.4,
            "audio": 0.3,
            "image": 0.3
        }
        
        # 情感强度映射
        self.intensity_mapping = {
            "very_low": 0.2,
            "low": 0.4,
            "medium": 0.6,
            "high": 0.8,
            "very_high": 1.0
        }
        
        logger.info("情感融合服务初始化完成")
    
    async def analyze_text_emotion(self, text: str) -> Dict[str, Any]:
        """
        分析文本情感
        
        Args:
            text: 输入文本
            
        Returns:
            包含情感分析结果的字典
        """
        try:
            start_time = time.time()
            
            # 情感关键词映射
            emotion_keywords = {
                "happy": ["开心", "高兴", "快乐", "兴奋", "愉快", "满意", "喜欢", "爱", "棒", "好"],
                "sad": ["难过", "伤心", "痛苦", "失望", "沮丧", "孤独", "寂寞", "哭", "泪", "痛"],
                "angry": ["生气", "愤怒", "恼火", "烦躁", "讨厌", "恨", "气", "怒", "烦", "火"],
                "anxious": ["焦虑", "担心", "紧张", "害怕", "恐惧", "不安", "着急", "慌", "怕", "忧"],
                "excited": ["兴奋", "激动", "期待", "兴奋", "振奋", "热情", "激动", "兴奋", "期待"],
                "calm": ["平静", "安静", "冷静", "放松", "舒适", "安心", "宁静", "平和", "稳定"],
                "confused": ["困惑", "迷茫", "不解", "疑惑", "糊涂", "不清楚", "不明白", "不懂", "迷"],
                "frustrated": ["沮丧", "挫败", "失望", "无奈", "无助", "绝望", "放弃", "失败", "不行"]
            }
            
            # 情感强度关键词
            intensity_keywords = {
                "very_high": ["非常", "极其", "特别", "超级", "太", "很", "十分", "极度"],
                "high": ["很", "非常", "特别", "相当", "比较", "挺", "蛮"],
                "medium": ["有点", "稍微", "一些", "一点", "还算", "还可以"],
                "low": ["稍微", "一点", "有点", "略微", "轻微"],
                "very_low": ["稍微", "一点", "轻微", "略微"]
            }
            
            # 分析情感
            emotion_scores = self._analyze_emotion_keywords(text, emotion_keywords)
            intensity_score = self._analyze_intensity_keywords(text, intensity_keywords)
            
            # 确定主导情感
            dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])
            
            # 计算最终强度
            final_intensity = min(dominant_emotion[1] * intensity_score, 1.0)
            
            processing_time = time.time() - start_time
            
            return {
                "emotion": dominant_emotion[0],
                "intensity": final_intensity,
                "confidence": 0.8,
                "keywords": self._extract_emotion_keywords(text, emotion_keywords),
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"文本情感分析失败: {e}")
            return {
                "emotion": "neutral",
                "intensity": 0.0,
                "confidence": 0.0,
                "keywords": [],
                "error": str(e)
            }
    
    def _analyze_emotion_keywords(self, text: str, emotion_keywords: Dict) -> Dict[str, float]:
        """分析情感关键词"""
        try:
            emotion_scores = {emotion: 0.0 for emotion in emotion_keywords.keys()}
            
            text_lower = text.lower()
            
            for emotion, keywords in emotion_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        emotion_scores[emotion] += 1.0
            
            # 归一化
            total_keywords = sum(emotion_scores.values())
            if total_keywords > 0:
                for emotion in emotion_scores:
                    emotion_scores[emotion] /= total_keywords
            
            return emotion_scores
            
        except Exception as e:
            logger.error(f"情感关键词分析失败: {e}")
            return {emotion: 0.0 for emotion in emotion_keywords.keys()}
    
    def _analyze_intensity_keywords(self, text: str, intensity_keywords: Dict) -> float:
        """分析强度关键词"""
        try:
            text_lower = text.lower()
            max_intensity = 0.0
            
            for intensity, keywords in intensity_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        max_intensity = max(max_intensity, self.intensity_mapping[intensity])
            
            return max_intensity if max_intensity > 0 else 0.5
            
        except Exception as e:
            logger.error(f"强度关键词分析失败: {e}")
            return 0.5
    
    def _extract_emotion_keywords(self, text: str, emotion_keywords: Dict) -> List[str]:
        """提取情感关键词"""
        try:
            found_keywords = []
            text_lower = text.lower()
            
            for emotion, keywords in emotion_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        found_keywords.append(keyword)
            
            return found_keywords
            
        except Exception as e:
            logger.error(f"关键词提取失败: {e}")
            return []
    
    async def fuse_emotions(self, modalities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        融合多种模态的情感信息
        
        Args:
            modalities: 多种模态的处理结果列表
            
        Returns:
            融合后的情感结果
        """
        try:
            start_time = time.time()
            
            if not modalities:
                return {
                    "emotion": "neutral",
                    "intensity": 0.0,
                    "confidence": 0.0,
                    "reasoning": "没有输入模态",
                    "suggestions": []
                }
            
            # 单一模态直接返回
            if len(modalities) == 1:
                modality = modalities[0]
                return {
                    "emotion": modality.get("emotion", "neutral"),
                    "intensity": modality.get("emotion_intensity", 0.0),
                    "confidence": modality.get("confidence", 0.8),
                    "reasoning": "单一模态输入",
                    "suggestions": self._generate_suggestions(modality.get("emotion", "neutral"))
                }
            
            # 多模态融合
            fusion_result = self._fuse_multiple_modalities(modalities)
            
            processing_time = time.time() - start_time
            fusion_result["processing_time"] = processing_time
            
            logger.info(f"多模态情感融合完成: {fusion_result['emotion']} (强度: {fusion_result['intensity']})")
            return fusion_result
            
        except Exception as e:
            logger.error(f"情感融合失败: {e}")
            return {
                "emotion": "neutral",
                "intensity": 0.0,
                "confidence": 0.0,
                "reasoning": "融合失败",
                "suggestions": [],
                "error": str(e)
            }
    
    def _fuse_multiple_modalities(self, modalities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """融合多种模态"""
        try:
            # 按模态类型分组
            modality_groups = {
                "text": [],
                "audio": [],
                "image": []
            }
            
            for modality in modalities:
                modality_type = modality.get("modality", "text")
                if modality_type in modality_groups:
                    modality_groups[modality_type].append(modality)
            
            # 计算各模态的情感
            modality_emotions = {}
            for modality_type, modality_list in modality_groups.items():
                if modality_list:
                    modality_emotions[modality_type] = self._aggregate_modality_emotions(modality_list)
            
            # 融合不同模态的情感
            fused_emotion = self._weighted_emotion_fusion(modality_emotions)
            
            # 生成融合推理
            reasoning = self._generate_fusion_reasoning(modality_emotions, fused_emotion)
            
            # 生成建议
            suggestions = self._generate_suggestions(fused_emotion["emotion"])
            
            return {
                "emotion": fused_emotion["emotion"],
                "intensity": fused_emotion["intensity"],
                "confidence": fused_emotion["confidence"],
                "reasoning": reasoning,
                "suggestions": suggestions,
                "modality_emotions": modality_emotions
            }
            
        except Exception as e:
            logger.error(f"多模态融合失败: {e}")
            return {
                "emotion": "neutral",
                "intensity": 0.0,
                "confidence": 0.0,
                "reasoning": "融合失败",
                "suggestions": []
            }
    
    def _aggregate_modality_emotions(self, modality_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """聚合同一模态的多个情感"""
        try:
            if not modality_list:
                return {"emotion": "neutral", "intensity": 0.0, "confidence": 0.0}
            
            # 计算平均情感
            emotions = [modality.get("emotion", "neutral") for modality in modality_list]
            intensities = [modality.get("emotion_intensity", 0.0) for modality in modality_list]
            confidences = [modality.get("confidence", 0.0) for modality in modality_list]
            
            # 使用投票机制确定主导情感
            emotion_counter = Counter(emotions)
            dominant_emotion = emotion_counter.most_common(1)[0][0]
            
            # 计算平均强度和置信度
            avg_intensity = np.mean(intensities)
            avg_confidence = np.mean(confidences)
            
            return {
                "emotion": dominant_emotion,
                "intensity": avg_intensity,
                "confidence": avg_confidence,
                "count": len(modality_list)
            }
            
        except Exception as e:
            logger.error(f"模态情感聚合失败: {e}")
            return {"emotion": "neutral", "intensity": 0.0, "confidence": 0.0}
    
    def _weighted_emotion_fusion(self, modality_emotions: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """加权情感融合"""
        try:
            if not modality_emotions:
                return {"emotion": "neutral", "intensity": 0.0, "confidence": 0.0}
            
            # 情感权重
            emotion_weights = {
                "happy": 1.0,
                "sad": 1.0,
                "angry": 1.2,  # 愤怒情感权重更高
                "anxious": 1.1,
                "excited": 1.0,
                "calm": 0.8,
                "confused": 0.9,
                "frustrated": 1.1,
                "neutral": 0.5
            }
            
            # 计算加权情感分数
            emotion_scores = {}
            total_weight = 0
            
            for modality_type, emotion_data in modality_emotions.items():
                emotion = emotion_data.get("emotion", "neutral")
                intensity = emotion_data.get("intensity", 0.0)
                confidence = emotion_data.get("confidence", 0.0)
                modality_weight = self.emotion_weights.get(modality_type, 0.3)
                
                # 计算加权分数
                weight = modality_weight * confidence * emotion_weights.get(emotion, 1.0)
                
                if emotion not in emotion_scores:
                    emotion_scores[emotion] = 0
                
                emotion_scores[emotion] += intensity * weight
                total_weight += weight
            
            # 找到主导情感
            if total_weight == 0:
                return {"emotion": "neutral", "intensity": 0.0, "confidence": 0.0}
            
            dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])
            final_intensity = min(dominant_emotion[1] / total_weight, 1.0)
            
            # 计算整体置信度
            overall_confidence = np.mean([data.get("confidence", 0.0) for data in modality_emotions.values()])
            
            return {
                "emotion": dominant_emotion[0],
                "intensity": final_intensity,
                "confidence": overall_confidence
            }
            
        except Exception as e:
            logger.error(f"加权情感融合失败: {e}")
            return {"emotion": "neutral", "intensity": 0.0, "confidence": 0.0}
    
    def _generate_fusion_reasoning(
        self, 
        modality_emotions: Dict[str, Dict[str, Any]], 
        fused_emotion: Dict[str, Any]
    ) -> str:
        """生成融合推理说明"""
        try:
            reasoning_parts = []
            
            for modality_type, emotion_data in modality_emotions.items():
                emotion = emotion_data.get("emotion", "neutral")
                intensity = emotion_data.get("intensity", 0.0)
                confidence = emotion_data.get("confidence", 0.0)
                
                if emotion != "neutral" and intensity > 0.3:
                    modality_name = {
                        "text": "文本",
                        "audio": "语音",
                        "image": "图像"
                    }.get(modality_type, modality_type)
                    
                    reasoning_parts.append(f"{modality_name}显示{emotion}情感(强度:{intensity:.2f})")
            
            if reasoning_parts:
                reasoning = f"基于{'、'.join(reasoning_parts)}的分析，综合判断为{fused_emotion['emotion']}情感"
            else:
                reasoning = "各模态情感信息不足，默认为中性情感"
            
            return reasoning
            
        except Exception as e:
            logger.error(f"融合推理生成失败: {e}")
            return "情感融合分析"
    
    def _generate_suggestions(self, emotion: str) -> List[str]:
        """根据情感生成建议"""
        try:
            suggestions_map = {
                "happy": [
                    "继续保持这种积极的心态！",
                    "分享你的快乐，让更多人感受到正能量",
                    "记录下这个美好的时刻"
                ],
                "sad": [
                    "我理解你的感受，难过是人之常情",
                    "试着做一些让自己放松的事情",
                    "如果需要，可以寻求朋友或专业人士的帮助"
                ],
                "angry": [
                    "深呼吸，给自己一些时间冷静下来",
                    "试着表达你的感受，而不是压抑",
                    "考虑一下是否有更好的解决方式"
                ],
                "anxious": [
                    "尝试一些放松技巧，如深呼吸或冥想",
                    "把担心的事情写下来，可能会有所帮助",
                    "专注于当下，不要过度担心未来"
                ],
                "excited": [
                    "这种兴奋的感觉很棒！",
                    "保持这种积极的状态",
                    "分享你的兴奋，让周围的人也能感受到"
                ],
                "calm": [
                    "这种平静的感觉很好",
                    "保持内心的宁静",
                    "享受当下的平和时光"
                ],
                "confused": [
                    "困惑是成长的一部分",
                    "试着把问题分解成小步骤",
                    "寻求他人的建议或帮助"
                ],
                "frustrated": [
                    "挫折感是暂时的，不要放弃",
                    "回顾一下已经取得的进步",
                    "考虑调整目标或方法"
                ],
                "neutral": [
                    "保持开放的心态",
                    "观察自己的感受变化",
                    "随时分享你的想法"
                ]
            }
            
            return suggestions_map.get(emotion, suggestions_map["neutral"])
            
        except Exception as e:
            logger.error(f"建议生成失败: {e}")
            return ["感谢你的分享"]
    
    async def analyze_emotion_consistency(self, modalities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析多模态情感一致性
        
        Args:
            modalities: 多种模态的处理结果
            
        Returns:
            包含一致性分析结果的字典
        """
        try:
            if len(modalities) < 2:
                return {
                    "consistent": True,
                    "consistency_score": 1.0,
                    "analysis": "单一模态，无需一致性检查"
                }
            
            # 提取各模态的情感
            emotions = [modality.get("emotion", "neutral") for modality in modalities]
            intensities = [modality.get("emotion_intensity", 0.0) for modality in modalities]
            
            # 计算情感一致性
            emotion_counter = Counter(emotions)
            most_common_emotion = emotion_counter.most_common(1)[0][0]
            consistency_ratio = emotion_counter[most_common_emotion] / len(emotions)
            
            # 计算强度一致性
            intensity_std = np.std(intensities)
            intensity_consistency = 1.0 - min(intensity_std, 1.0)
            
            # 综合一致性分数
            overall_consistency = (consistency_ratio + intensity_consistency) / 2
            
            # 判断是否一致
            is_consistent = overall_consistency > 0.6
            
            analysis = self._generate_consistency_analysis(emotions, intensities, is_consistent)
            
            return {
                "consistent": is_consistent,
                "consistency_score": overall_consistency,
                "emotion_distribution": dict(emotion_counter),
                "intensity_std": float(intensity_std),
                "analysis": analysis
            }
            
        except Exception as e:
            logger.error(f"情感一致性分析失败: {e}")
            return {
                "consistent": False,
                "consistency_score": 0.0,
                "analysis": "一致性分析失败",
                "error": str(e)
            }
    
    def _generate_consistency_analysis(
        self, 
        emotions: List[str], 
        intensities: List[float], 
        is_consistent: bool
    ) -> str:
        """生成一致性分析说明"""
        try:
            if is_consistent:
                return "各模态情感表现一致，情感识别可信度高"
            else:
                emotion_counter = Counter(emotions)
                dominant_emotion = emotion_counter.most_common(1)[0][0]
                return f"各模态情感存在差异，主导情感为{dominant_emotion}，建议结合上下文进一步分析"
                
        except Exception as e:
            logger.error(f"一致性分析说明生成失败: {e}")
            return "情感一致性分析"
