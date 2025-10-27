"""
多模态处理器
统一处理文本、语音、图像等多种模态的输入
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import tempfile
import os

from ..services.asr_service import ASRService
from ..services.tts_service import TTSService
from ..services.image_service import ImageService
from ..services.emotion_fusion import EmotionFusionService

logger = logging.getLogger(__name__)


class MultimodalProcessor:
    """
    多模态处理器
    负责协调各种模态的处理，实现统一的情感理解
    """
    
    def __init__(self):
        """初始化多模态处理器"""
        self.asr_service = ASRService()
        self.tts_service = TTSService()
        self.image_service = ImageService()
        self.emotion_fusion = EmotionFusionService()
        
        logger.info("多模态处理器初始化完成")
    
    async def process_audio(self, audio_file_path: str) -> Dict[str, Any]:
        """
        处理音频文件
        
        Args:
            audio_file_path: 音频文件路径
            
        Returns:
            包含文本、情感、语音特征等信息的字典
        """
        try:
            logger.info(f"开始处理音频文件: {audio_file_path}")
            
            # 语音识别
            text_result = await self.asr_service.transcribe(audio_file_path)
            
            # 语音情感分析
            emotion_result = await self.asr_service.analyze_emotion(audio_file_path)
            
            # 语音特征提取
            features = await self.asr_service.extract_features(audio_file_path)
            
            result = {
                "text": text_result.get("text", ""),
                "confidence": text_result.get("confidence", 0.0),
                "emotion": emotion_result.get("emotion", "neutral"),
                "emotion_intensity": emotion_result.get("intensity", 0.0),
                "voice_features": features,
                "modality": "audio",
                "processing_time": text_result.get("processing_time", 0.0)
            }
            
            logger.info(f"音频处理完成: {result['emotion']} (强度: {result['emotion_intensity']})")
            return result
            
        except Exception as e:
            logger.error(f"音频处理失败: {e}")
            return {
                "text": "",
                "confidence": 0.0,
                "emotion": "neutral",
                "emotion_intensity": 0.0,
                "voice_features": {},
                "modality": "audio",
                "error": str(e)
            }
    
    async def process_image(self, image_file_path: str) -> Dict[str, Any]:
        """
        处理图像文件
        
        Args:
            image_file_path: 图像文件路径
            
        Returns:
            包含场景、情感、文字等信息的字典
        """
        try:
            logger.info(f"开始处理图像文件: {image_file_path}")
            
            # 场景识别
            scene_result = await self.image_service.analyze_scene(image_file_path)
            
            # 人脸情感分析
            face_result = await self.image_service.analyze_faces(image_file_path)
            
            # OCR文字提取
            text_result = await self.image_service.extract_text(image_file_path)
            
            # 图像情感分析
            emotion_result = await self.image_service.analyze_emotion(image_file_path)
            
            result = {
                "scene": scene_result.get("scene", "unknown"),
                "scene_confidence": scene_result.get("confidence", 0.0),
                "faces": face_result.get("faces", []),
                "text": text_result.get("text", ""),
                "emotion": emotion_result.get("emotion", "neutral"),
                "emotion_intensity": emotion_result.get("intensity", 0.0),
                "modality": "image",
                "processing_time": scene_result.get("processing_time", 0.0)
            }
            
            logger.info(f"图像处理完成: {result['emotion']} (强度: {result['emotion_intensity']})")
            return result
            
        except Exception as e:
            logger.error(f"图像处理失败: {e}")
            return {
                "scene": "unknown",
                "scene_confidence": 0.0,
                "faces": [],
                "text": "",
                "emotion": "neutral",
                "emotion_intensity": 0.0,
                "modality": "image",
                "error": str(e)
            }
    
    async def process_text(self, text: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        处理文本输入
        
        Args:
            text: 输入文本
            context: 上下文信息
            
        Returns:
            包含情感分析等信息的字典
        """
        try:
            logger.info(f"开始处理文本: {text[:50]}...")
            
            # 文本情感分析
            emotion_result = await self.emotion_fusion.analyze_text_emotion(text)
            
            result = {
                "text": text,
                "emotion": emotion_result.get("emotion", "neutral"),
                "emotion_intensity": emotion_result.get("intensity", 0.0),
                "keywords": emotion_result.get("keywords", []),
                "modality": "text",
                "processing_time": emotion_result.get("processing_time", 0.0)
            }
            
            logger.info(f"文本处理完成: {result['emotion']} (强度: {result['emotion_intensity']})")
            return result
            
        except Exception as e:
            logger.error(f"文本处理失败: {e}")
            return {
                "text": text,
                "emotion": "neutral",
                "emotion_intensity": 0.0,
                "keywords": [],
                "modality": "text",
                "error": str(e)
            }
    
    async def fuse_modalities(self, modalities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        融合多种模态的信息
        
        Args:
            modalities: 多种模态的处理结果列表
            
        Returns:
            融合后的情感和理解结果
        """
        try:
            logger.info(f"开始融合 {len(modalities)} 种模态")
            
            # 使用情感融合服务
            fusion_result = await self.emotion_fusion.fuse_emotions(modalities)
            
            # 构建统一的理解结果
            result = {
                "fused_emotion": fusion_result.get("emotion", "neutral"),
                "fused_intensity": fusion_result.get("intensity", 0.0),
                "confidence": fusion_result.get("confidence", 0.0),
                "modalities": modalities,
                "fusion_reasoning": fusion_result.get("reasoning", ""),
                "suggestions": fusion_result.get("suggestions", []),
                "processing_time": fusion_result.get("processing_time", 0.0)
            }
            
            logger.info(f"模态融合完成: {result['fused_emotion']} (强度: {result['fused_intensity']})")
            return result
            
        except Exception as e:
            logger.error(f"模态融合失败: {e}")
            return {
                "fused_emotion": "neutral",
                "fused_intensity": 0.0,
                "confidence": 0.0,
                "modalities": modalities,
                "fusion_reasoning": "融合失败",
                "suggestions": [],
                "error": str(e)
            }
    
    async def generate_tts_response(self, text: str, emotion: str = "neutral") -> Dict[str, Any]:
        """
        生成语音回复
        
        Args:
            text: 要合成的文本
            emotion: 目标情感
            
        Returns:
            包含音频文件路径等信息的字典
        """
        try:
            logger.info(f"开始生成语音回复: {text[:50]}...")
            
            # 调用TTS服务
            tts_result = await self.tts_service.synthesize(text, emotion)
            
            result = {
                "audio_file": tts_result.get("audio_file", ""),
                "duration": tts_result.get("duration", 0.0),
                "emotion": emotion,
                "text": text,
                "processing_time": tts_result.get("processing_time", 0.0)
            }
            
            logger.info(f"语音回复生成完成: {result['duration']}秒")
            return result
            
        except Exception as e:
            logger.error(f"语音回复生成失败: {e}")
            return {
                "audio_file": "",
                "duration": 0.0,
                "emotion": emotion,
                "text": text,
                "error": str(e)
            }
    
    async def process_multimodal_input(
        self, 
        text: Optional[str] = None,
        audio_file: Optional[str] = None,
        image_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        处理多模态输入
        
        Args:
            text: 文本输入
            audio_file: 音频文件路径
            image_file: 图像文件路径
            
        Returns:
            统一的多模态处理结果
        """
        try:
            logger.info("开始处理多模态输入")
            
            modalities = []
            
            # 处理文本
            if text and text.strip():
                text_result = await self.process_text(text)
                modalities.append(text_result)
            
            # 处理音频
            if audio_file and os.path.exists(audio_file):
                audio_result = await self.process_audio(audio_file)
                modalities.append(audio_result)
            
            # 处理图像
            if image_file and os.path.exists(image_file):
                image_result = await self.process_image(image_file)
                modalities.append(image_result)
            
            if not modalities:
                return {
                    "fused_emotion": "neutral",
                    "fused_intensity": 0.0,
                    "confidence": 0.0,
                    "modalities": [],
                    "fusion_reasoning": "没有有效的输入",
                    "suggestions": [],
                    "error": "没有有效的输入"
                }
            
            # 融合多种模态
            if len(modalities) > 1:
                fusion_result = await self.fuse_modalities(modalities)
                return fusion_result
            else:
                # 单一模态直接返回
                single_modality = modalities[0]
                return {
                    "fused_emotion": single_modality.get("emotion", "neutral"),
                    "fused_intensity": single_modality.get("emotion_intensity", 0.0),
                    "confidence": single_modality.get("confidence", 1.0),
                    "modalities": modalities,
                    "fusion_reasoning": "单一模态输入",
                    "suggestions": [],
                    "processing_time": single_modality.get("processing_time", 0.0)
                }
                
        except Exception as e:
            logger.error(f"多模态输入处理失败: {e}")
            return {
                "fused_emotion": "neutral",
                "fused_intensity": 0.0,
                "confidence": 0.0,
                "modalities": [],
                "fusion_reasoning": "处理失败",
                "suggestions": [],
                "error": str(e)
            }

