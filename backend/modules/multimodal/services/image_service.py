"""
图像理解服务
支持场景识别、人脸情感分析、OCR等功能
"""

import asyncio
import logging
import os
import tempfile
import time
from typing import Dict, Any, List, Optional
import cv2
import numpy as np
from PIL import Image
import pytesseract
from deepface import DeepFace
import face_recognition

logger = logging.getLogger(__name__)


class ImageService:
    """
    图像理解服务
    支持场景识别、人脸情感分析、OCR等功能
    """
    
    def __init__(self):
        """初始化图像服务"""
        self.aliyun_client = None
        self._init_aliyun_client()
    
    def _init_aliyun_client(self):
        """初始化阿里云图像识别客户端"""
        try:
            if os.getenv("ALIYUN_ACCESS_KEY_ID"):
                from aliyunsdkcore.client import AcsClient
                from aliyunsdkimageprocess.request.v20200320 import RecognizeImageRequest
                
                access_key_id = os.getenv("ALIYUN_ACCESS_KEY_ID")
                access_key_secret = os.getenv("ALIYUN_ACCESS_KEY_SECRET")
                region = os.getenv("ALIYUN_REGION", "cn-shanghai")
                
                self.aliyun_client = AcsClient(access_key_id, access_key_secret, region)
                logger.info("阿里云图像识别客户端初始化完成")
            else:
                logger.warning("未配置阿里云API密钥，图像识别功能将受限")
                
        except Exception as e:
            logger.error(f"阿里云图像识别客户端初始化失败: {e}")
    
    async def analyze_scene(self, image_file_path: str) -> Dict[str, Any]:
        """
        场景识别
        
        Args:
            image_file_path: 图像文件路径
            
        Returns:
            包含场景信息的字典
        """
        try:
            start_time = time.time()
            
            # 加载图像
            image = cv2.imread(image_file_path)
            if image is None:
                raise ValueError(f"无法加载图像: {image_file_path}")
            
            # 基本场景分析
            scene_info = await self._analyze_basic_scene(image)
            
            # 使用阿里云进行高级场景识别
            if self.aliyun_client:
                cloud_scene = await self._analyze_scene_with_aliyun(image_file_path)
                scene_info.update(cloud_scene)
            
            processing_time = time.time() - start_time
            scene_info["processing_time"] = processing_time
            
            logger.info(f"场景识别完成: {scene_info.get('scene', 'unknown')}")
            return scene_info
            
        except Exception as e:
            logger.error(f"场景识别失败: {e}")
            return {
                "scene": "unknown",
                "confidence": 0.0,
                "lighting": "unknown",
                "colors": [],
                "objects": [],
                "error": str(e)
            }
    
    async def _analyze_basic_scene(self, image: np.ndarray) -> Dict[str, Any]:
        """基础场景分析"""
        try:
            # 转换为HSV进行颜色分析
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # 亮度分析
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            
            # 颜色分析
            dominant_colors = self._extract_dominant_colors(image)
            
            # 边缘检测
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            # 基于特征判断场景
            scene = self._classify_scene(brightness, edge_density, dominant_colors)
            
            return {
                "scene": scene,
                "confidence": 0.7,
                "lighting": "bright" if brightness > 127 else "dark",
                "brightness": float(brightness),
                "colors": dominant_colors,
                "edge_density": float(edge_density)
            }
            
        except Exception as e:
            logger.error(f"基础场景分析失败: {e}")
            return {
                "scene": "unknown",
                "confidence": 0.0,
                "lighting": "unknown",
                "colors": [],
                "error": str(e)
            }
    
    def _extract_dominant_colors(self, image: np.ndarray, k: int = 5) -> List[str]:
        """提取主要颜色"""
        try:
            # 重塑图像数据
            data = image.reshape((-1, 3))
            data = np.float32(data)
            
            # K-means聚类
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
            _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # 转换颜色空间
            colors = []
            for center in centers:
                b, g, r = center
                colors.append(f"rgb({int(r)},{int(g)},{int(b)})")
            
            return colors
            
        except Exception as e:
            logger.error(f"颜色提取失败: {e}")
            return []
    
    def _classify_scene(self, brightness: float, edge_density: float, colors: List[str]) -> str:
        """基于特征分类场景"""
        try:
            # 简化的场景分类规则
            if brightness < 50:
                return "indoor_dark"
            elif brightness > 200:
                return "outdoor_bright"
            elif edge_density > 0.1:
                return "complex_scene"
            elif any("green" in color.lower() for color in colors):
                return "nature"
            elif any("blue" in color.lower() for color in colors):
                return "sky_water"
            else:
                return "indoor"
                
        except Exception as e:
            logger.error(f"场景分类失败: {e}")
            return "unknown"
    
    async def _analyze_scene_with_aliyun(self, image_file_path: str) -> Dict[str, Any]:
        """使用阿里云进行场景识别"""
        try:
            from aliyunsdkimageprocess.request.v20200320 import RecognizeImageRequest
            
            request = RecognizeImageRequest.RecognizeImageRequest()
            request.set_ImageURL(f"https://your-oss-bucket.oss-cn-shanghai.aliyuncs.com/{os.path.basename(image_file_path)}")
            
            response = self.aliyun_client.do_action_with_exception(request)
            
            return {
                "scene": response.get('Scene', 'unknown'),
                "confidence": response.get('Confidence', 0.0),
                "objects": response.get('Objects', [])
            }
            
        except Exception as e:
            logger.error(f"阿里云场景识别失败: {e}")
            return {}
    
    async def analyze_faces(self, image_file_path: str) -> Dict[str, Any]:
        """
        人脸情感分析
        
        Args:
            image_file_path: 图像文件路径
            
        Returns:
            包含人脸情感信息的字典
        """
        try:
            start_time = time.time()
            
            # 检测人脸
            face_locations = face_recognition.face_locations(face_recognition.load_image_file(image_file_path))
            
            if not face_locations:
                return {
                    "faces": [],
                    "emotion": "neutral",
                    "intensity": 0.0,
                    "processing_time": time.time() - start_time
                }
            
            # 使用DeepFace分析情感
            analysis = DeepFace.analyze(
                image_file_path,
                actions=['emotion', 'age', 'gender'],
                enforce_detection=False
            )
            
            faces = []
            for i, face_location in enumerate(face_locations):
                if i < len(analysis):
                    face_info = {
                        "location": face_location,
                        "emotion": analysis[i].get('dominant_emotion', 'neutral'),
                        "emotion_scores": analysis[i].get('emotion', {}),
                        "age": analysis[i].get('age', 0),
                        "gender": analysis[i].get('dominant_gender', 'unknown')
                    }
                    faces.append(face_info)
            
            # 计算整体情感
            overall_emotion = self._calculate_overall_emotion(faces)
            
            processing_time = time.time() - start_time
            
            return {
                "faces": faces,
                "emotion": overall_emotion["emotion"],
                "intensity": overall_emotion["intensity"],
                "face_count": len(faces),
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"人脸情感分析失败: {e}")
            return {
                "faces": [],
                "emotion": "neutral",
                "intensity": 0.0,
                "face_count": 0,
                "error": str(e)
            }
    
    def _calculate_overall_emotion(self, faces: List[Dict]) -> Dict[str, Any]:
        """计算整体情感"""
        try:
            if not faces:
                return {"emotion": "neutral", "intensity": 0.0}
            
            # 情感权重映射
            emotion_weights = {
                'angry': 0.9,
                'fear': 0.8,
                'sad': 0.7,
                'disgust': 0.6,
                'surprise': 0.5,
                'neutral': 0.3,
                'happy': 0.2
            }
            
            # 计算加权平均
            total_weight = 0
            weighted_emotions = {}
            
            for face in faces:
                emotion = face.get('emotion', 'neutral')
                intensity = face.get('emotion_scores', {}).get(emotion, 0.0)
                weight = emotion_weights.get(emotion, 0.5)
                
                if emotion not in weighted_emotions:
                    weighted_emotions[emotion] = 0
                
                weighted_emotions[emotion] += intensity * weight
                total_weight += weight
            
            if total_weight == 0:
                return {"emotion": "neutral", "intensity": 0.0}
            
            # 找到最高权重的情感
            dominant_emotion = max(weighted_emotions.items(), key=lambda x: x[1])
            
            return {
                "emotion": dominant_emotion[0],
                "intensity": min(dominant_emotion[1] / total_weight, 1.0)
            }
            
        except Exception as e:
            logger.error(f"整体情感计算失败: {e}")
            return {"emotion": "neutral", "intensity": 0.0}
    
    async def extract_text(self, image_file_path: str) -> Dict[str, Any]:
        """
        OCR文字提取
        
        Args:
            image_file_path: 图像文件路径
            
        Returns:
            包含提取文字信息的字典
        """
        try:
            start_time = time.time()
            
            # 使用pytesseract进行OCR
            image = Image.open(image_file_path)
            text = pytesseract.image_to_string(image, lang='chi_sim+eng')
            
            # 清理文本
            cleaned_text = self._clean_ocr_text(text)
            
            # 使用阿里云OCR进行增强
            if self.aliyun_client:
                cloud_text = await self._extract_text_with_aliyun(image_file_path)
                if cloud_text.get('text'):
                    cleaned_text = cloud_text['text']
            
            processing_time = time.time() - start_time
            
            return {
                "text": cleaned_text,
                "confidence": 0.8,
                "language": "zh",
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"OCR文字提取失败: {e}")
            return {
                "text": "",
                "confidence": 0.0,
                "language": "zh",
                "error": str(e)
            }
    
    def _clean_ocr_text(self, text: str) -> str:
        """清理OCR文本"""
        try:
            # 移除多余的空白字符
            cleaned = ' '.join(text.split())
            
            # 移除特殊字符
            import re
            cleaned = re.sub(r'[^\w\s\u4e00-\u9fff]', '', cleaned)
            
            return cleaned.strip()
            
        except Exception as e:
            logger.error(f"文本清理失败: {e}")
            return text
    
    async def _extract_text_with_aliyun(self, image_file_path: str) -> Dict[str, Any]:
        """使用阿里云OCR提取文字"""
        try:
            from aliyunsdkocr.request.v20191230 import RecognizeCharacterRequest
            
            request = RecognizeCharacterRequest.RecognizeCharacterRequest()
            request.set_ImageURL(f"https://your-oss-bucket.oss-cn-shanghai.aliyuncs.com/{os.path.basename(image_file_path)}")
            
            response = self.aliyun_client.do_action_with_exception(request)
            
            return {
                "text": response.get('Text', ''),
                "confidence": response.get('Confidence', 0.0)
            }
            
        except Exception as e:
            logger.error(f"阿里云OCR失败: {e}")
            return {}
    
    async def analyze_emotion(self, image_file_path: str) -> Dict[str, Any]:
        """
        图像整体情感分析
        
        Args:
            image_file_path: 图像文件路径
            
        Returns:
            包含情感分析结果的字典
        """
        try:
            start_time = time.time()
            
            # 加载图像
            image = cv2.imread(image_file_path)
            if image is None:
                raise ValueError(f"无法加载图像: {image_file_path}")
            
            # 颜色情感分析
            color_emotion = self._analyze_color_emotion(image)
            
            # 人脸情感分析
            face_result = await self.analyze_faces(image_file_path)
            
            # 场景情感分析
            scene_result = await self.analyze_scene(image_file_path)
            
            # 融合多种情感线索
            overall_emotion = self._fuse_image_emotions(
                color_emotion, 
                face_result, 
                scene_result
            )
            
            processing_time = time.time() - start_time
            
            return {
                "emotion": overall_emotion["emotion"],
                "intensity": overall_emotion["intensity"],
                "color_emotion": color_emotion,
                "face_emotion": face_result.get("emotion", "neutral"),
                "scene_emotion": scene_result.get("emotion", "neutral"),
                "confidence": overall_emotion["confidence"],
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"图像情感分析失败: {e}")
            return {
                "emotion": "neutral",
                "intensity": 0.0,
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _analyze_color_emotion(self, image: np.ndarray) -> Dict[str, Any]:
        """分析颜色情感"""
        try:
            # 转换为HSV
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # 分析色调分布
            hue = hsv[:, :, 0]
            saturation = hsv[:, :, 1]
            value = hsv[:, :, 2]
            
            # 计算平均色调
            mean_hue = np.mean(hue)
            mean_saturation = np.mean(saturation)
            mean_value = np.mean(value)
            
            # 基于颜色特征判断情感
            emotion = self._classify_color_emotion(mean_hue, mean_saturation, mean_value)
            
            return {
                "emotion": emotion,
                "intensity": 0.7,
                "hue": float(mean_hue),
                "saturation": float(mean_saturation),
                "brightness": float(mean_value)
            }
            
        except Exception as e:
            logger.error(f"颜色情感分析失败: {e}")
            return {
                "emotion": "neutral",
                "intensity": 0.0
            }
    
    def _classify_color_emotion(self, hue: float, saturation: float, brightness: float) -> str:
        """基于颜色特征分类情感"""
        try:
            # 色调情感映射
            if 0 <= hue <= 30 or 330 <= hue <= 360:  # 红色系
                if brightness > 150:
                    return "excited"
                else:
                    return "angry"
            elif 30 <= hue <= 90:  # 黄色系
                if brightness > 150:
                    return "happy"
                else:
                    return "warm"
            elif 90 <= hue <= 150:  # 绿色系
                return "calm"
            elif 150 <= hue <= 210:  # 青色系
                return "peaceful"
            elif 210 <= hue <= 270:  # 蓝色系
                if brightness < 100:
                    return "sad"
                else:
                    return "calm"
            elif 270 <= hue <= 330:  # 紫色系
                return "mysterious"
            else:
                return "neutral"
                
        except Exception as e:
            logger.error(f"颜色情感分类失败: {e}")
            return "neutral"
    
    def _fuse_image_emotions(
        self, 
        color_emotion: Dict, 
        face_result: Dict, 
        scene_result: Dict
    ) -> Dict[str, Any]:
        """融合图像中的多种情感线索"""
        try:
            emotions = []
            weights = []
            
            # 颜色情感
            if color_emotion.get("emotion") != "neutral":
                emotions.append(color_emotion["emotion"])
                weights.append(0.3)
            
            # 人脸情感
            if face_result.get("emotion") != "neutral":
                emotions.append(face_result["emotion"])
                weights.append(0.5)
            
            # 场景情感
            if scene_result.get("emotion") != "neutral":
                emotions.append(scene_result["emotion"])
                weights.append(0.2)
            
            if not emotions:
                return {
                    "emotion": "neutral",
                    "intensity": 0.0,
                    "confidence": 0.5
                }
            
            # 计算加权平均
            emotion_scores = {}
            total_weight = 0
            
            for emotion, weight in zip(emotions, weights):
                if emotion not in emotion_scores:
                    emotion_scores[emotion] = 0
                emotion_scores[emotion] += weight
                total_weight += weight
            
            # 找到主导情感
            dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])
            
            return {
                "emotion": dominant_emotion[0],
                "intensity": min(dominant_emotion[1] / total_weight, 1.0),
                "confidence": 0.8
            }
            
        except Exception as e:
            logger.error(f"图像情感融合失败: {e}")
            return {
                "emotion": "neutral",
                "intensity": 0.0,
                "confidence": 0.0
            }

