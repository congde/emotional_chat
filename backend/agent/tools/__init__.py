"""
External Tools - 外部工具模块

提供各种外部工具实现：
- 日历API
- 音频播放服务
- 心理资源数据库
- 定时提醒服务
- Agent核心工具函数
"""

from .calendar_api import CalendarAPI
from .audio_player import AudioPlayer
from .psychology_db import PsychologyDB
from .scheduler_service import SchedulerService

# 延迟导入Agent核心工具函数，避免循环依赖
def __getattr__(name):
    """延迟导入 agent_tools 中的函数"""
    _agent_tools_funcs = [
        "get_user_mood_trend",
        "play_meditation_audio",
        "set_daily_reminder",
        "search_mental_health_resources",
        "send_follow_up_message"
    ]
    if name in _agent_tools_funcs:
        from . import agent_tools
        return getattr(agent_tools, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "CalendarAPI",
    "AudioPlayer",
    "PsychologyDB",
    "SchedulerService",
    # Agent核心工具函数（延迟导入）
    "get_user_mood_trend",
    "play_meditation_audio",
    "set_daily_reminder",
    "search_mental_health_resources",
    "send_follow_up_message"
]

