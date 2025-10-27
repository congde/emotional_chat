"""
多模态情感交互服务
支持语音识别(ASR)、语音合成(TTS)、图像理解等功能
"""
import os
import io
import base64
import logging
from typing import Dict, Any, Optional, Tuple
import numpy as np
from pathlib import Path

# 语音处理
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logging.warning("Whisper not available, ASR functionality will be limited")

try:
    import pydub
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    logging.warning("Pydub not available, audio processing will be limited")

# 图像处理
try:
    from PIL import Image
    import cv2
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL/CV2 not available, image processing will be limited")

try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False
    logging.warning("DeepFace not available, facial emotion recognition will be limited")

try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logging.warning("Pytesseract not available, OCR functionality will be limited")

logger = logging.getLogger(__name__)


class VoiceRecognitionService:
    """语音识别服务 - 使用Whisper"""
    
    def __init__(self):
        self.model = None
        if WHISPER_AVAILABLE:
            try:
                self.model = whisper.load_model("base")
                logger.info("Whisper model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
    
    def transcribe(self, audio_path: str) -> Dict[str, Any]:
        """将音频文件转换为文本"""
        if not self.model:
            return {
                "text": "",
                "success": False,
                "error": "Whisper model not available"
            }
        
        try:
            # 转录音频
            result = self.model.transcribe(audio_path)
            
            # 提取语音特征
            audio_features = self._extract_audio_features(audio_path)
            
            return {
                "text": result["text"],
                "language": result.get("language", "zh"),
                "audio_features": audio_features,
                "success": True
            }
        except Exception as e:
            logger.error(f"ASR error: {e}")
            return {
                "text": "",
                "success": False,
                "error": str(e)
            }
    
    def _extract_audio_features(self, audio_path: str) -> Dict[str, Any]:
        """提取音频特征（音量、语速等）"""
        if not PYDUB_AVAILABLE:
            return {}
        
        try:
            audio = AudioSegment.from_file(audio_path)
            
            # 计算平均音量
            avg_volume = audio.rms
            
            # 计算时长
            duration = len(audio) / 1000.0  # 转换为秒
            
            # 分析音频特征
            features = {
                "duration": duration,
                "avg_volume": avg_volume,
                "max_volume": audio.max_possible_amplitude,
                "sample_rate": audio.frame_rate
            }
            
            # 判断音频特征（简单的情绪线索）
            if avg_volume < audio.max_possible_amplitude * 0.3:
                features["energy_level"] = "low"  # 可能低情绪
            elif avg_volume > audio.max_possible_amplitude * 0.7:
                features["energy_level"] = "high"  # 可能高情绪
            else:
                features["energy_level"] = "medium"
            
            return features
        except Exception as e:
            logger.error(f"Error extracting audio features: {e}")
            return {}


class VoiceSynthesisService:
    """语音合成服务 - 使用本地TTS或云服务"""
    
    def __init__(self, use_cloud: bool = False):
        self.use_cloud = use_cloud
        
    def synthesize(self, text: str, voice: str = "warm_female") -> bytes:
        """
        将文本转换为语音
        Args:
            text: 要转换的文本
            voice: 音色选择 (warm_female, gentle_male, caring_neutral)
        Returns:
            音频数据 (bytes)
        """
        if self.use_cloud:
            # 使用云TTS服务（阿里云等）
            return self._cloud_tts(text, voice)
        else:
            # 使用本地TTS（如gTTS）
            return self._local_tts(text, voice)
    
    def _cloud_tts(self, text: str, voice: str) -> bytes:
        """云TTS服务"""
        # TODO: 集成阿里云TTS
        # 这里返回占位符
        logger.info(f"Cloud TTS: {text}")
        return b""
    
    def _local_tts(self, text: str, voice: str) -> bytes:
        """本地TTS服务"""
        try:
            from gtts import gTTS
            from io import BytesIO
            
            tts = gTTS(text=text, lang='zh', slow=False)
            
            audio_buffer = BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            return audio_buffer.read()
        except Exception as e:
            logger.error(f"Local TTS error: {e}")
            return b""


class ImageAnalysisService:
    """图像分析服务"""
    
    def __init__(self):
        self.face_analysis_enabled = DEEPFACE_AVAILABLE
        self.ocr_enabled = OCR_AVAILABLE
    
    def analyze(self, image_path: str) -> Dict[str, Any]:
        """
        分析图像内容
        Returns:
            {
                "emotion": "情感识别",
                "scene": "场景描述",
                "color_mood": "色彩情绪",
                "ocr_text": "图片中的文字",
                "face_emotion": "人脸情绪"
            }
        """
        result = {
            "emotion": "neutral",
            "scene": "",
            "color_mood": "",
            "ocr_text": "",
            "face_emotion": None,
            "success": True
        }
        
        try:
            # 1. 基础图像分析
            image = Image.open(image_path)
            basic_analysis = self._analyze_basic_features(image)
            result.update(basic_analysis)
            
            # 2. 人脸情绪分析
            if self.face_analysis_enabled:
                face_result = self._analyze_face_emotion(image_path)
                if face_result:
                    result["face_emotion"] = face_result
            
            # 3. OCR文字提取
            if self.ocr_enabled:
                ocr_text = self._extract_text(image_path)
                result["ocr_text"] = ocr_text
            
            # 4. 综合情感判断
            result["emotion"] = self._determine_emotion(result)
            
        except Exception as e:
            logger.error(f"Image analysis error: {e}")
            result["success"] = False
            result["error"] = str(e)
        
        return result
    
    def _analyze_basic_features(self, image: Image.Image) -> Dict[str, Any]:
        """分析基础图像特征"""
        analysis = {}
        
        # 转换为RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # 获取图像大小
        width, height = image.size
        analysis["size"] = {"width": width, "height": height}
        
        # 转换为numpy数组进行颜色分析
        img_array = np.array(image)
        
        # 计算平均颜色
        avg_color = img_array.mean(axis=(0, 1))
        analysis["avg_color"] = {
            "r": int(avg_color[0]),
            "g": int(avg_color[1]),
            "b": int(avg_color[2])
        }
        
        # 判断亮度（明暗）
        brightness = avg_color.mean()
        if brightness < 80:
            analysis["brightness"] = "dark"
            analysis["color_mood"] = "可能负面、忧郁"
        elif brightness > 180:
            analysis["brightness"] = "bright"
            analysis["color_mood"] = "可能积极、明亮"
        else:
            analysis["brightness"] = "medium"
            analysis["color_mood"] = "中性"
        
        # 简化场景判断（基于颜色分布）
        analysis["scene"] = self._detect_scene_type(img_array)
        
        return analysis
    
    def _detect_scene_type(self, img_array: np.ndarray) -> str:
        """检测场景类型"""
        # 简化的场景检测
        # 实际应用中可以接入更复杂的场景识别模型
        height, width = img_array.shape[:2]
        
        # 检测天空区域
        sky_region = img_array[:height//3, :]
        sky_color = sky_region.mean(axis=(0, 1))
        
        # 如果上半部分比较亮且偏蓝色，可能是室外场景
        if sky_color[2] > sky_color[0] and sky_color[2] > 120:
            return "outdoor"
        else:
            return "indoor or unknown"
    
    def _analyze_face_emotion(self, image_path: str) -> Optional[Dict[str, Any]]:
        """分析人脸情绪"""
        try:
            result = DeepFace.analyze(
                img_path=image_path,
                actions=['emotion', 'age', 'gender'],
                enforce_detection=False
            )
            
            if isinstance(result, list):
                result = result[0]
            
            return {
                "dominant_emotion": result.get('dominant_emotion', 'neutral'),
                "emotion_scores": result.get('emotion', {}),
                "age": result.get('age'),
                "gender": result.get('dominant_gender'),
                "confidence": 0.8  # 简化处理
            }
        except Exception as e:
            logger.warning(f"Face analysis failed: {e}")
            return None
    
    def _extract_text(self, image_path: str) -> str:
        """OCR提取文字"""
        try:
            text = pytesseract.image_to_string(Image.open(image_path), lang='chi_sim+eng')
            return text.strip()
        except Exception as e:
            logger.warning(f"OCR failed: {e}")
            return ""
    
    def _determine_emotion(self, analysis: Dict[str, Any]) -> str:
        """综合判断图像情绪"""
        factors = []
        
        # 色彩情绪
        color_mood = analysis.get("color_mood", "")
        if "负面" in color_mood or "忧郁" in color_mood:
            factors.append("negative")
        elif "积极" in color_mood or "明亮" in color_mood:
            factors.append("positive")
        
        # 亮度
        brightness = analysis.get("brightness", "")
        if brightness == "dark":
            factors.append("negative")
        elif brightness == "bright":
            factors.append("positive")
        
        # 人脸情绪
        face_emotion = analysis.get("face_emotion", {})
        if face_emotion:
            dominant = face_emotion.get("dominant_emotion", "neutral")
            if dominant in ["sad", "angry", "fear"]:
                factors.append("negative")
            elif dominant in ["happy", "surprise"]:
                factors.append("positive")
        
        # 综合判断
        positive_count = factors.count("positive")
        negative_count = factors.count("negative")
        
        if negative_count > positive_count:
            return "negative"
        elif positive_count > negative_count:
            return "positive"
        else:
            return "neutral"


class MultimodalFusionService:
    """多模态情感融合服务"""
    
    def __init__(self):
        self.voice_service = VoiceRecognitionService()
        self.image_service = ImageAnalysisService()
    
    def fuse_modalities(
        self,
        text: str,
        audio_data: Optional[Dict[str, Any]] = None,
        image_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        融合多模态数据，生成统一的情感理解
        """
        # 1. 文本情感分析（基础）
        text_emotion = self._analyze_text_emotion(text)
        
        # 2. 音频情感分析
        audio_emotion = self._analyze_audio_emotion(audio_data) if audio_data else None
        
        # 3. 图像情感分析
        image_emotion = self._analyze_image_emotion(image_data) if image_data else None
        
        # 4. 多模态融合
        fused_result = self._fuse_emotions(text_emotion, audio_emotion, image_emotion)
        
        return fused_result
    
    def _analyze_text_emotion(self, text: str) -> Dict[str, Any]:
        """分析文本情感"""
        # 简化的情感关键词匹配
        # 实际应用中应接入更强大的情感分析模型
        negative_keywords = ["难过", "伤心", "沮丧", "害怕", "孤独", "痛苦", "绝望"]
        positive_keywords = ["开心", "高兴", "快乐", "幸福", "兴奋", "满足", "感激"]
        
        text_lower = text.lower()
        
        negative_score = sum(1 for keyword in negative_keywords if keyword in text_lower)
        positive_score = sum(1 for keyword in positive_keywords if keyword in text_lower)
        
        if negative_score > positive_score:
            emotion = "negative"
            intensity = min(negative_score / 3, 1.0)  # 归一化
        elif positive_score > negative_score:
            emotion = "positive"
            intensity = min(positive_score / 3, 1.0)
        else:
            emotion = "neutral"
            intensity = 0.5
        
        return {"emotion": emotion, "intensity": intensity, "modality": "text"}
    
    def _analyze_audio_emotion(self, audio_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """分析音频情感"""
        features = audio_data.get("audio_features", {})
        energy = features.get("energy_level", "medium")
        
        if energy == "low":
            return {"emotion": "negative", "intensity": 0.6, "modality": "audio"}
        elif energy == "high":
            return {"emotion": "positive", "intensity": 0.7, "modality": "audio"}
        else:
            return {"emotion": "neutral", "intensity": 0.5, "modality": "audio"}
    
    def _analyze_image_emotion(self, image_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """分析图像情感"""
        emotion = image_data.get("emotion", "neutral")
        
        if emotion == "negative":
            intensity = 0.7
        elif emotion == "positive":
            intensity = 0.7
        else:
            intensity = 0.5
        
        return {"emotion": emotion, "intensity": intensity, "modality": "image"}
    
    def _fuse_emotions(
        self,
        text_emotion: Dict[str, Any],
        audio_emotion: Optional[Dict[str, Any]],
        image_emotion: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """融合多模态情感"""
        modalities = [text_emotion]
        if audio_emotion:
            modalities.append(audio_emotion)
        if image_emotion:
            modalities.append(image_emotion)
        
        # 加权融合
        emotion_scores = {"positive": 0, "negative": 0, "neutral": 0}
        total_weight = 0
        
        for mod in modalities:
            emotion = mod["emotion"]
            intensity = mod["intensity"]
            
            # 分配权重
            emotion_scores[emotion] += intensity
            total_weight += 1
        
        # 归一化
        if total_weight > 0:
            for emotion in emotion_scores:
                emotion_scores[emotion] /= total_weight
        
        # 确定主导情感
        dominant_emotion = max(emotion_scores, key=emotion_scores.get)
        dominant_intensity = emotion_scores[dominant_emotion]
        
        # 检测一致性（多模态是否一致）
        consistent = False
        if len(modalities) > 1:
            emotions = [m["emotion"] for m in modalities]
            if len(set(emotions)) == 1:  # 所有模态情感一致
                consistent = True
        
        # 检测矛盾（文本说"没事"但音调低）
        contradictory = False
        if len(modalities) >= 2:
            text_emotion_val = text_emotion["emotion"]
            other_emotions = [m["emotion"] for m in modalities if m != text_emotion]
            if text_emotion_val == "neutral" and any(e == "negative" for e in other_emotions):
                contradictory = True
                # 如果出现矛盾，倾向于非文本模态
                dominant_emotion = "negative"
                dominant_intensity = 0.8
        
        return {
            "dominant_emotion": dominant_emotion,
            "dominant_intensity": dominant_intensity,
            "emotion_scores": emotion_scores,
            "modalities_consistent": consistent,
            "contradictory_signals": contradictory,
            "modalities": [
                {
                    "type": m["modality"],
                    "emotion": m["emotion"],
                    "intensity": m["intensity"]
                }
                for m in modalities
            ]
        }


# 全局服务实例
voice_recognition = VoiceRecognitionService()
voice_synthesis = VoiceSynthesisService(use_cloud=False)
image_analysis = ImageAnalysisService()
multimodal_fusion = MultimodalFusionService()
