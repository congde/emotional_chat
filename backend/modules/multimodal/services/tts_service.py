"""
语音合成服务 (TTS - Text-to-Speech)
支持阿里云TTS和本地TTS
"""

import asyncio
import logging
import os
import tempfile
import time
from typing import Dict, Any, Optional
import base64
import wave
import struct

logger = logging.getLogger(__name__)


class TTSService:
    """
    语音合成服务
    支持阿里云TTS和本地TTS
    """
    
    def __init__(self):
        """初始化TTS服务"""
        self.aliyun_client = None
        self._init_aliyun_client()
    
    def _init_aliyun_client(self):
        """初始化阿里云TTS客户端"""
        try:
            if os.getenv("ALIYUN_ACCESS_KEY_ID"):
                from aliyunsdkcore.client import AcsClient
                from aliyunsdknls.cloud_api.request.v20180614 import SynthesizerRequest
                
                access_key_id = os.getenv("ALIYUN_ACCESS_KEY_ID")
                access_key_secret = os.getenv("ALIYUN_ACCESS_KEY_SECRET")
                region = os.getenv("ALIYUN_REGION", "cn-shanghai")
                
                self.aliyun_client = AcsClient(access_key_id, access_key_secret, region)
                logger.info("阿里云TTS客户端初始化完成")
            else:
                logger.warning("未配置阿里云API密钥，TTS功能将受限")
                
        except Exception as e:
            logger.error(f"阿里云TTS客户端初始化失败: {e}")
    
    async def synthesize(
        self, 
        text: str, 
        emotion: str = "neutral",
        voice: str = "xiaoyun",
        use_aliyun: bool = True
    ) -> Dict[str, Any]:
        """
        文本转语音
        
        Args:
            text: 要合成的文本
            emotion: 目标情感
            voice: 音色选择
            use_aliyun: 是否使用阿里云服务
            
        Returns:
            包含音频文件路径等信息的字典
        """
        try:
            start_time = time.time()
            
            if use_aliyun and self.aliyun_client:
                result = await self._synthesize_with_aliyun(text, emotion, voice)
            else:
                result = await self._synthesize_local(text, emotion)
            
            processing_time = time.time() - start_time
            result["processing_time"] = processing_time
            
            logger.info(f"语音合成完成: {len(text)}字符 -> {result.get('duration', 0):.2f}秒")
            return result
            
        except Exception as e:
            logger.error(f"语音合成失败: {e}")
            return {
                "audio_file": "",
                "duration": 0.0,
                "text": text,
                "emotion": emotion,
                "error": str(e)
            }
    
    async def _synthesize_with_aliyun(
        self, 
        text: str, 
        emotion: str, 
        voice: str
    ) -> Dict[str, Any]:
        """使用阿里云TTS进行语音合成"""
        try:
            from aliyunsdknls.cloud_api.request.v20180614 import SynthesizerRequest
            
            # 根据情感选择音色和参数
            voice_config = self._get_voice_config(emotion, voice)
            
            request = SynthesizerRequest.SynthesizerRequest()
            request.set_Text(text)
            request.set_Voice(voice_config["voice"])
            request.set_Format("wav")
            request.set_SampleRate(16000)
            
            # 设置情感参数
            if voice_config.get("ssml"):
                request.set_Text(voice_config["ssml"])
            
            response = self.aliyun_client.do_action_with_exception(request)
            
            # 保存音频文件
            audio_data = response.get('AudioData')
            if audio_data:
                audio_file = await self._save_audio_file(audio_data, "wav")
                duration = self._get_audio_duration(audio_file)
                
                return {
                    "audio_file": audio_file,
                    "duration": duration,
                    "text": text,
                    "emotion": emotion,
                    "voice": voice_config["voice"]
                }
            else:
                raise Exception("阿里云TTS返回空音频数据")
                
        except Exception as e:
            logger.error(f"阿里云TTS合成失败: {e}")
            raise
    
    async def _synthesize_local(self, text: str, emotion: str) -> Dict[str, Any]:
        """本地TTS合成（简化实现）"""
        try:
            # 这里可以实现本地TTS，比如使用pyttsx3或其他本地TTS库
            # 为了演示，我们创建一个简单的音频文件
            
            audio_file = await self._create_simple_audio(text, emotion)
            duration = self._get_audio_duration(audio_file)
            
            return {
                "audio_file": audio_file,
                "duration": duration,
                "text": text,
                "emotion": emotion,
                "voice": "local"
            }
            
        except Exception as e:
            logger.error(f"本地TTS合成失败: {e}")
            raise
    
    def _get_voice_config(self, emotion: str, voice: str) -> Dict[str, Any]:
        """根据情感获取音色配置"""
        emotion_configs = {
            "happy": {
                "voice": "xiaoyun",
                "rate": "fast",
                "pitch": "high",
                "ssml": f'<speak><prosody rate="fast" pitch="high">{voice}</prosody></speak>'
            },
            "sad": {
                "voice": "xiaoyun",
                "rate": "slow",
                "pitch": "low",
                "ssml": f'<speak><prosody rate="slow" pitch="low">{voice}</prosody></speak>'
            },
            "angry": {
                "voice": "xiaogang",
                "rate": "fast",
                "pitch": "high",
                "ssml": f'<speak><prosody rate="fast" pitch="high" volume="loud">{voice}</prosody></speak>'
            },
            "excited": {
                "voice": "xiaoyun",
                "rate": "fast",
                "pitch": "high",
                "ssml": f'<speak><prosody rate="fast" pitch="high" volume="loud">{voice}</prosody></speak>'
            },
            "calm": {
                "voice": "xiaoyun",
                "rate": "slow",
                "pitch": "medium",
                "ssml": f'<speak><prosody rate="slow" pitch="medium">{voice}</prosody></speak>'
            },
            "neutral": {
                "voice": voice,
                "rate": "medium",
                "pitch": "medium"
            }
        }
        
        return emotion_configs.get(emotion, emotion_configs["neutral"])
    
    async def _save_audio_file(self, audio_data: str, format: str = "wav") -> str:
        """保存音频数据到文件"""
        try:
            # 创建临时文件
            temp_dir = tempfile.mkdtemp()
            audio_file = os.path.join(temp_dir, f"tts_output.{format}")
            
            # 解码base64音频数据
            if isinstance(audio_data, str):
                audio_bytes = base64.b64decode(audio_data)
            else:
                audio_bytes = audio_data
            
            # 保存到文件
            with open(audio_file, "wb") as f:
                f.write(audio_bytes)
            
            logger.info(f"音频文件保存完成: {audio_file}")
            return audio_file
            
        except Exception as e:
            logger.error(f"音频文件保存失败: {e}")
            raise
    
    async def _create_simple_audio(self, text: str, emotion: str) -> str:
        """创建简单的音频文件（用于演示）"""
        try:
            temp_dir = tempfile.mkdtemp()
            audio_file = os.path.join(temp_dir, "simple_tts.wav")
            
            # 根据情感调整音频参数
            duration = len(text) * 0.1  # 简单的时长计算
            sample_rate = 16000
            
            # 根据情感调整频率
            base_freq = 440  # A4音符
            if emotion == "sad":
                base_freq = 330  # 更低
            elif emotion == "excited":
                base_freq = 550  # 更高
            
            # 生成简单的音频波形
            samples = []
            for i in range(int(duration * sample_rate)):
                t = i / sample_rate
                # 简单的正弦波
                sample = int(32767 * 0.3 * (1 + 0.1 * np.sin(2 * np.pi * base_freq * t)))
                samples.append(sample)
            
            # 保存为WAV文件
            with wave.open(audio_file, 'w') as wav_file:
                wav_file.setnchannels(1)  # 单声道
                wav_file.setsampwidth(2)  # 16位
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(struct.pack('<' + 'h' * len(samples), *samples))
            
            logger.info(f"简单音频文件创建完成: {audio_file}")
            return audio_file
            
        except Exception as e:
            logger.error(f"简单音频创建失败: {e}")
            raise
    
    def _get_audio_duration(self, audio_file: str) -> float:
        """获取音频文件时长"""
        try:
            with wave.open(audio_file, 'r') as wav_file:
                frames = wav_file.getnframes()
                sample_rate = wav_file.getframerate()
                duration = frames / sample_rate
                return duration
        except Exception as e:
            logger.error(f"获取音频时长失败: {e}")
            return 0.0
    
    async def synthesize_with_emotion(
        self, 
        text: str, 
        emotion: str,
        intensity: float = 0.5
    ) -> Dict[str, Any]:
        """
        根据情感强度进行语音合成
        
        Args:
            text: 要合成的文本
            emotion: 目标情感
            intensity: 情感强度 (0.0-1.0)
            
        Returns:
            包含音频文件等信息的字典
        """
        try:
            # 根据强度调整情感参数
            adjusted_emotion = self._adjust_emotion_intensity(emotion, intensity)
            
            # 选择音色
            voice = self._select_voice_for_emotion(emotion)
            
            # 生成SSML标记
            ssml_text = self._generate_ssml(text, emotion, intensity)
            
            result = await self.synthesize(ssml_text, emotion, voice)
            result["intensity"] = intensity
            result["ssml"] = ssml_text
            
            return result
            
        except Exception as e:
            logger.error(f"情感语音合成失败: {e}")
            return {
                "audio_file": "",
                "duration": 0.0,
                "text": text,
                "emotion": emotion,
                "intensity": intensity,
                "error": str(e)
            }
    
    def _adjust_emotion_intensity(self, emotion: str, intensity: float) -> str:
        """根据强度调整情感"""
        if intensity < 0.3:
            return "neutral"
        elif intensity > 0.8:
            return emotion
        else:
            return emotion
    
    def _select_voice_for_emotion(self, emotion: str) -> str:
        """根据情感选择音色"""
        voice_mapping = {
            "happy": "xiaoyun",
            "sad": "xiaoyun", 
            "angry": "xiaogang",
            "excited": "xiaoyun",
            "calm": "xiaoyun",
            "neutral": "xiaoyun"
        }
        return voice_mapping.get(emotion, "xiaoyun")
    
    def _generate_ssml(self, text: str, emotion: str, intensity: float) -> str:
        """生成SSML标记语言"""
        try:
            # 根据情感和强度设置参数
            if emotion == "sad":
                rate = "slow"
                pitch = "low"
                volume = "soft"
            elif emotion == "happy":
                rate = "fast"
                pitch = "high"
                volume = "medium"
            elif emotion == "angry":
                rate = "fast"
                pitch = "high"
                volume = "loud"
            elif emotion == "excited":
                rate = "fast"
                pitch = "high"
                volume = "loud"
            else:
                rate = "medium"
                pitch = "medium"
                volume = "medium"
            
            # 根据强度调整参数
            if intensity > 0.7:
                if rate == "slow":
                    rate = "x-slow"
                elif rate == "fast":
                    rate = "x-fast"
            
            ssml = f'<speak><prosody rate="{rate}" pitch="{pitch}" volume="{volume}">{text}</prosody></speak>'
            return ssml
            
        except Exception as e:
            logger.error(f"SSML生成失败: {e}")
            return text

