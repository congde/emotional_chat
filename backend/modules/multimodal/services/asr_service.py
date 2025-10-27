"""
语音识别服务 (ASR - Automatic Speech Recognition)
支持Whisper和阿里云语音识别
"""

import asyncio
import logging
import os
import tempfile
import time
from typing import Dict, Any, Optional
import whisper
import librosa
import numpy as np
from pydub import AudioSegment
import noisereduce as nr

logger = logging.getLogger(__name__)


class ASRService:
    """
    语音识别服务
    支持Whisper本地识别和阿里云语音识别
    """
    
    def __init__(self):
        """初始化ASR服务"""
        self.whisper_model = None
        self.aliyun_client = None
        self._load_models()
    
    def _load_models(self):
        """加载语音识别模型"""
        try:
            # 加载Whisper模型
            logger.info("正在加载Whisper模型...")
            self.whisper_model = whisper.load_model("base")
            logger.info("Whisper模型加载完成")
            
            # 初始化阿里云客户端（如果配置了API密钥）
            if os.getenv("ALIYUN_ACCESS_KEY_ID"):
                self._init_aliyun_client()
                
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
    
    def _init_aliyun_client(self):
        """初始化阿里云语音识别客户端"""
        try:
            from aliyunsdkcore.client import AcsClient
            from aliyunsdknls.cloud_api.request.v20180614 import SubmitTaskRequest
            
            access_key_id = os.getenv("ALIYUN_ACCESS_KEY_ID")
            access_key_secret = os.getenv("ALIYUN_ACCESS_KEY_SECRET")
            region = os.getenv("ALIYUN_REGION", "cn-shanghai")
            
            self.aliyun_client = AcsClient(access_key_id, access_key_secret, region)
            logger.info("阿里云语音识别客户端初始化完成")
            
        except Exception as e:
            logger.error(f"阿里云客户端初始化失败: {e}")
    
    async def transcribe(self, audio_file_path: str, use_aliyun: bool = False) -> Dict[str, Any]:
        """
        语音转文字
        
        Args:
            audio_file_path: 音频文件路径
            use_aliyun: 是否使用阿里云服务
            
        Returns:
            包含识别文本和置信度的字典
        """
        try:
            start_time = time.time()
            
            # 预处理音频
            processed_audio_path = await self._preprocess_audio(audio_file_path)
            
            if use_aliyun and self.aliyun_client:
                result = await self._transcribe_with_aliyun(processed_audio_path)
            else:
                result = await self._transcribe_with_whisper(processed_audio_path)
            
            processing_time = time.time() - start_time
            result["processing_time"] = processing_time
            
            logger.info(f"语音识别完成: {result.get('text', '')[:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"语音识别失败: {e}")
            return {
                "text": "",
                "confidence": 0.0,
                "language": "zh",
                "processing_time": 0.0,
                "error": str(e)
            }
    
    async def _transcribe_with_whisper(self, audio_file_path: str) -> Dict[str, Any]:
        """使用Whisper进行语音识别"""
        try:
            # 在异步环境中运行Whisper
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self.whisper_model.transcribe, 
                audio_file_path
            )
            
            return {
                "text": result["text"].strip(),
                "confidence": 0.9,  # Whisper不直接提供置信度
                "language": result.get("language", "zh"),
                "segments": result.get("segments", [])
            }
            
        except Exception as e:
            logger.error(f"Whisper识别失败: {e}")
            raise
    
    async def _transcribe_with_aliyun(self, audio_file_path: str) -> Dict[str, Any]:
        """使用阿里云进行语音识别"""
        try:
            # 上传音频文件到阿里云OSS（这里简化处理）
            # 实际应用中需要先上传到OSS获取URL
            
            from aliyunsdknls.cloud_api.request.v20180614 import SubmitTaskRequest
            
            request = SubmitTaskRequest.SubmitTaskRequest()
            request.set_Task({
                'AudioUrl': f"https://your-oss-bucket.oss-cn-shanghai.aliyuncs.com/{os.path.basename(audio_file_path)}",
                'Mode': 'Sync'
            })
            
            response = self.aliyun_client.do_action_with_exception(request)
            
            return {
                "text": response.get('Result', ''),
                "confidence": response.get('Confidence', 0.0),
                "language": "zh"
            }
            
        except Exception as e:
            logger.error(f"阿里云识别失败: {e}")
            raise
    
    async def _preprocess_audio(self, audio_file_path: str) -> str:
        """
        预处理音频文件
        包括降噪、格式转换、采样率调整等
        """
        try:
            # 创建临时文件
            temp_dir = tempfile.mkdtemp()
            processed_path = os.path.join(temp_dir, "processed_audio.wav")
            
            # 加载音频
            audio = AudioSegment.from_file(audio_file_path)
            
            # 转换为单声道
            if audio.channels > 1:
                audio = audio.set_channels(1)
            
            # 调整采样率到16kHz
            if audio.frame_rate != 16000:
                audio = audio.set_frame_rate(16000)
            
            # 降噪处理
            audio_array = np.array(audio.get_array_of_samples())
            if audio.channels == 1:
                audio_array = audio_array.reshape(-1, 1)
            
            # 应用降噪
            reduced_noise = nr.reduce_noise(y=audio_array, sr=16000)
            
            # 保存处理后的音频
            processed_audio = AudioSegment(
                reduced_noise.tobytes(),
                frame_rate=16000,
                sample_width=audio.sample_width,
                channels=1
            )
            
            processed_audio.export(processed_path, format="wav")
            
            logger.info(f"音频预处理完成: {processed_path}")
            return processed_path
            
        except Exception as e:
            logger.error(f"音频预处理失败: {e}")
            return audio_file_path
    
    async def analyze_emotion(self, audio_file_path: str) -> Dict[str, Any]:
        """
        分析语音中的情感
        
        Args:
            audio_file_path: 音频文件路径
            
        Returns:
            包含情感类型和强度的字典
        """
        try:
            # 加载音频文件
            y, sr = librosa.load(audio_file_path, sr=16000)
            
            # 提取音频特征
            features = self._extract_audio_features(y, sr)
            
            # 基于特征进行情感分析
            emotion, intensity = self._classify_emotion(features)
            
            return {
                "emotion": emotion,
                "intensity": intensity,
                "features": features
            }
            
        except Exception as e:
            logger.error(f"语音情感分析失败: {e}")
            return {
                "emotion": "neutral",
                "intensity": 0.0,
                "features": {}
            }
    
    def _extract_audio_features(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """提取音频特征"""
        try:
            # 基本特征
            duration = len(y) / sr
            energy = np.sum(y ** 2) / len(y)
            
            # 频谱特征
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            zero_crossing_rate = librosa.feature.zero_crossing_rate(y)[0]
            
            # MFCC特征
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            
            # 音调特征
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            pitch_mean = np.mean(pitches[pitches > 0])
            
            # 节奏特征
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            
            return {
                "duration": float(duration),
                "energy": float(energy),
                "spectral_centroid_mean": float(np.mean(spectral_centroids)),
                "spectral_rolloff_mean": float(np.mean(spectral_rolloff)),
                "zero_crossing_rate_mean": float(np.mean(zero_crossing_rate)),
                "mfcc_mean": float(np.mean(mfccs)),
                "pitch_mean": float(pitch_mean) if not np.isnan(pitch_mean) else 0.0,
                "tempo": float(tempo)
            }
            
        except Exception as e:
            logger.error(f"音频特征提取失败: {e}")
            return {}
    
    def _classify_emotion(self, features: Dict[str, float]) -> tuple:
        """
        基于音频特征分类情感
        
        Args:
            features: 音频特征字典
            
        Returns:
            (emotion, intensity) 元组
        """
        try:
            # 简化的情感分类规则
            # 实际应用中应该使用训练好的机器学习模型
            
            energy = features.get("energy", 0.0)
            pitch = features.get("pitch_mean", 0.0)
            tempo = features.get("tempo", 0.0)
            zcr = features.get("zero_crossing_rate_mean", 0.0)
            
            # 基于特征判断情感
            if energy > 0.1 and pitch > 200 and tempo > 120:
                return "excited", 0.8
            elif energy < 0.05 and pitch < 150 and tempo < 80:
                return "sad", 0.7
            elif zcr > 0.1 and energy > 0.08:
                return "angry", 0.8
            elif pitch > 250 and tempo > 100:
                return "happy", 0.7
            elif energy < 0.03 and pitch < 100:
                return "tired", 0.6
            else:
                return "neutral", 0.5
                
        except Exception as e:
            logger.error(f"情感分类失败: {e}")
            return "neutral", 0.0
    
    async def extract_features(self, audio_file_path: str) -> Dict[str, Any]:
        """
        提取语音特征
        
        Args:
            audio_file_path: 音频文件路径
            
        Returns:
            包含各种语音特征的字典
        """
        try:
            y, sr = librosa.load(audio_file_path, sr=16000)
            features = self._extract_audio_features(y, sr)
            
            # 添加更多高级特征
            features.update({
                "file_path": audio_file_path,
                "sample_rate": sr,
                "length": len(y),
                "timestamp": time.time()
            })
            
            return features
            
        except Exception as e:
            logger.error(f"语音特征提取失败: {e}")
            return {}

