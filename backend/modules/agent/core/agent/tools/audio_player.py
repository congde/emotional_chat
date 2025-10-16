"""
Audio Player - 音频播放服务

提供音频资源管理和播放功能：
- 冥想音频
- 白噪音
- 舒缓音乐
"""

from typing import List, Dict, Any, Optional


class AudioPlayer:
    """音频播放服务"""
    
    def __init__(self):
        """初始化音频播放器"""
        # 音频资源库
        self.audio_library = self._init_audio_library()
        
        # 播放历史
        self.play_history = {}
    
    def _init_audio_library(self) -> Dict[str, List[Dict[str, Any]]]:
        """初始化音频资源库"""
        return {
            "meditation": [
                {
                    "id": "med_001",
                    "title": "深度睡眠引导冥想",
                    "duration": 15,
                    "theme": "sleep",
                    "url": "https://example.com/audio/meditation/sleep_deep.mp3",
                    "description": "通过渐进式放松帮助你快速入睡",
                    "tags": ["睡眠", "放松", "冥想"]
                },
                {
                    "id": "med_002",
                    "title": "焦虑缓解冥想",
                    "duration": 10,
                    "theme": "anxiety",
                    "url": "https://example.com/audio/meditation/anxiety_relief.mp3",
                    "description": "通过正念练习缓解焦虑情绪",
                    "tags": ["焦虑", "正念", "冥想"]
                },
                {
                    "id": "med_003",
                    "title": "全身放松扫描",
                    "duration": 12,
                    "theme": "relaxation",
                    "url": "https://example.com/audio/meditation/body_scan.mp3",
                    "description": "系统性地放松身体各个部位",
                    "tags": ["放松", "身心", "冥想"]
                },
                {
                    "id": "med_004",
                    "title": "4-7-8呼吸练习",
                    "duration": 5,
                    "theme": "breathing",
                    "url": "https://example.com/audio/meditation/478_breathing.mp3",
                    "description": "快速减压的呼吸技巧",
                    "tags": ["呼吸", "快速", "减压"]
                }
            ],
            "white_noise": [
                {
                    "id": "wn_001",
                    "title": "海浪声",
                    "duration": 30,
                    "url": "https://example.com/audio/whitenoise/ocean_waves.mp3",
                    "description": "舒缓的海浪声，帮助集中注意力",
                    "tags": ["自然", "海洋", "集中"]
                },
                {
                    "id": "wn_002",
                    "title": "雨声",
                    "duration": 30,
                    "url": "https://example.com/audio/whitenoise/rain.mp3",
                    "description": "温柔的雨声，营造宁静氛围",
                    "tags": ["自然", "雨", "宁静"]
                },
                {
                    "id": "wn_003",
                    "title": "森林鸟鸣",
                    "duration": 30,
                    "url": "https://example.com/audio/whitenoise/forest_birds.mp3",
                    "description": "清晨森林的鸟鸣声",
                    "tags": ["自然", "森林", "鸟鸣"]
                }
            ],
            "music": [
                {
                    "id": "mus_001",
                    "title": "轻音乐 - 宁静时光",
                    "duration": 20,
                    "url": "https://example.com/audio/music/peaceful_time.mp3",
                    "description": "舒缓的轻音乐，适合放松",
                    "tags": ["轻音乐", "舒缓", "放松"]
                },
                {
                    "id": "mus_002",
                    "title": "钢琴曲 - 月光",
                    "duration": 15,
                    "url": "https://example.com/audio/music/moonlight.mp3",
                    "description": "优美的钢琴曲",
                    "tags": ["钢琴", "古典", "优美"]
                }
            ]
        }
    
    def search_audio(
        self,
        theme: Optional[str] = None,
        category: Optional[str] = None,
        max_duration: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        搜索音频资源
        
        Args:
            theme: 主题（sleep/anxiety/relaxation等）
            category: 分类（meditation/white_noise/music）
            max_duration: 最大时长（分钟）
            tags: 标签列表
            
        Returns:
            匹配的音频列表
        """
        results = []
        
        # 确定搜索范围
        if category:
            categories = [category] if category in self.audio_library else []
        else:
            categories = self.audio_library.keys()
        
        # 搜索
        for cat in categories:
            for audio in self.audio_library[cat]:
                # 主题过滤
                if theme and audio.get("theme") != theme:
                    continue
                
                # 时长过滤
                if max_duration and audio.get("duration", 0) > max_duration:
                    continue
                
                # 标签过滤
                if tags:
                    audio_tags = set(audio.get("tags", []))
                    if not any(tag in audio_tags for tag in tags):
                        continue
                
                results.append({
                    **audio,
                    "category": cat
                })
        
        return results
    
    def get_recommendation(
        self,
        user_id: str,
        emotion: str,
        duration: int = 10
    ) -> List[Dict[str, Any]]:
        """
        根据用户情绪推荐音频
        
        Args:
            user_id: 用户ID
            emotion: 情绪状态
            duration: 期望时长
            
        Returns:
            推荐音频列表
        """
        # 情绪到主题的映射
        emotion_theme_map = {
            "焦虑": "anxiety",
            "压力": "relaxation",
            "失眠": "sleep",
            "难过": "relaxation",
            "愤怒": "breathing"
        }
        
        theme = emotion_theme_map.get(emotion, "relaxation")
        
        # 搜索相关音频
        results = self.search_audio(
            theme=theme,
            category="meditation",
            max_duration=duration + 5
        )
        
        # 如果没有结果，推荐白噪音
        if not results:
            results = self.search_audio(category="white_noise")
        
        # 根据播放历史调整推荐
        user_history = self.play_history.get(user_id, [])
        played_ids = set([h["audio_id"] for h in user_history])
        
        # 优先推荐未播放的
        unplayed = [r for r in results if r["id"] not in played_ids]
        if unplayed:
            return unplayed[:3]
        
        return results[:3]
    
    def play_audio(
        self,
        user_id: str,
        audio_id: str
    ) -> Dict[str, Any]:
        """
        播放音频
        
        Args:
            user_id: 用户ID
            audio_id: 音频ID
            
        Returns:
            播放信息
        """
        # 查找音频
        audio = self._find_audio_by_id(audio_id)
        
        if not audio:
            return {
                "success": False,
                "error": "音频不存在"
            }
        
        # 记录播放历史
        if user_id not in self.play_history:
            self.play_history[user_id] = []
        
        from datetime import datetime
        self.play_history[user_id].append({
            "audio_id": audio_id,
            "played_at": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "audio": audio,
            "message": f"正在播放：{audio['title']}"
        }
    
    def get_play_history(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取播放历史
        
        Args:
            user_id: 用户ID
            limit: 返回数量限制
            
        Returns:
            播放历史
        """
        history = self.play_history.get(user_id, [])
        
        # 获取音频详情
        detailed_history = []
        for record in history[-limit:]:
            audio = self._find_audio_by_id(record["audio_id"])
            if audio:
                detailed_history.append({
                    **record,
                    "audio": audio
                })
        
        return detailed_history
    
    def _find_audio_by_id(self, audio_id: str) -> Optional[Dict[str, Any]]:
        """根据ID查找音频"""
        for category, audios in self.audio_library.items():
            for audio in audios:
                if audio["id"] == audio_id:
                    return {**audio, "category": category}
        return None


# 单例模式
_audio_player_instance = None

def get_audio_player() -> AudioPlayer:
    """获取全局AudioPlayer实例"""
    global _audio_player_instance
    if _audio_player_instance is None:
        _audio_player_instance = AudioPlayer()
    return _audio_player_instance

