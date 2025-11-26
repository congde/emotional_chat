"""
Agent Tools - Agent工具函数集合

提供文档中提到的核心工具函数：
1. get_user_mood_trend() - 获取用户情绪趋势
2. play_meditation_audio() - 播放冥想音频
3. set_daily_reminder() - 设置每日提醒
4. search_mental_health_resources() - 搜索心理健康资源
5. send_follow_up_message() - 发送回访消息
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

# 延迟导入，避免循环依赖
# 使用 importlib 直接加载文件，避免触发 backend/agent/__init__.py
import importlib.util

def _load_module_from_file(module_name: str, file_path: str):
    """直接从文件加载模块，避免包导入触发 __init__.py"""
    import os
    full_path = os.path.join(project_root, file_path)
    spec = importlib.util.spec_from_file_location(module_name, full_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def _get_db_session():
    from backend.database import SessionLocal
    return SessionLocal()

def _get_emotion_analysis_model():
    from backend.database import EmotionAnalysis
    return EmotionAnalysis

def _get_audio_player():
    module = _load_module_from_file('audio_player', 'backend/agent/tools/audio_player.py')
    return module.get_audio_player()

def _get_scheduler():
    module = _load_module_from_file('scheduler_service', 'backend/agent/tools/scheduler_service.py')
    return module.get_scheduler_service()

def _get_reminder_type():
    module = _load_module_from_file('scheduler_service', 'backend/agent/tools/scheduler_service.py')
    return module.ReminderType

def _get_psychology_db():
    module = _load_module_from_file('psychology_db', 'backend/agent/tools/psychology_db.py')
    return module.get_psychology_db()


def get_user_mood_trend(user_id: str, days: int = 7) -> Dict[str, Any]:
    """
    获取近N天情绪变化曲线，判断是否需干预
    
    Args:
        user_id: 用户ID
        days: 查询天数，默认7天
        
    Returns:
        {
            "trend": List[Dict],  # 每日情绪数据
            "average_intensity": float,  # 平均情绪强度
            "trend_direction": str,  # "improving" / "declining" / "stable"
            "needs_intervention": bool,  # 是否需要干预
            "intervention_reason": str,  # 干预原因
            "summary": str  # 趋势摘要
        }
    """
    db = _get_db_session()
    EmotionAnalysis = _get_emotion_analysis_model()
    try:
        # 计算查询时间范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 查询情绪分析记录
        emotion_records = db.query(EmotionAnalysis).filter(
            EmotionAnalysis.user_id == user_id,
            EmotionAnalysis.created_at >= start_date,
            EmotionAnalysis.created_at <= end_date
        ).order_by(EmotionAnalysis.created_at).all()
        
        # 如果没有记录，返回默认值
        if not emotion_records:
            return {
                "trend": [],
                "average_intensity": 5.0,
                "trend_direction": "stable",
                "needs_intervention": False,
                "intervention_reason": "数据不足，无法判断",
                "summary": f"近{days}天暂无情绪记录"
            }
        
        # 按日期分组统计
        daily_data = {}
        for record in emotion_records:
            date_key = record.created_at.date().isoformat()
            if date_key not in daily_data:
                daily_data[date_key] = {
                    "date": date_key,
                    "emotions": [],
                    "intensities": [],
                    "count": 0
                }
            
            daily_data[date_key]["emotions"].append(record.emotion)
            if record.intensity:
                daily_data[date_key]["intensities"].append(record.intensity)
            daily_data[date_key]["count"] += 1
        
        # 构建趋势数据
        trend = []
        all_intensities = []
        
        for date_key in sorted(daily_data.keys()):
            day_data = daily_data[date_key]
            avg_intensity = sum(day_data["intensities"]) / len(day_data["intensities"]) if day_data["intensities"] else 5.0
            
            # 统计最频繁的情绪
            emotion_counts = {}
            for emotion in day_data["emotions"]:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else "neutral"
            
            trend.append({
                "date": date_key,
                "dominant_emotion": dominant_emotion,
                "average_intensity": round(avg_intensity, 2),
                "message_count": day_data["count"]
            })
            
            all_intensities.extend(day_data["intensities"])
        
        # 计算平均强度
        average_intensity = sum(all_intensities) / len(all_intensities) if all_intensities else 5.0
        
        # 判断趋势方向
        if len(trend) >= 2:
            recent_avg = sum([t["average_intensity"] for t in trend[-3:]]) / min(3, len(trend))
            earlier_avg = sum([t["average_intensity"] for t in trend[:3]]) / min(3, len(trend))
            
            if recent_avg < earlier_avg - 0.5:
                trend_direction = "improving"
            elif recent_avg > earlier_avg + 0.5:
                trend_direction = "declining"
            else:
                trend_direction = "stable"
        else:
            trend_direction = "stable"
        
        # 判断是否需要干预
        needs_intervention = False
        intervention_reason = ""
        
        # 判断条件：
        # 1. 平均强度过低（< 3.0，表示持续负面情绪）
        if average_intensity < 3.0:
            needs_intervention = True
            intervention_reason = f"平均情绪强度较低（{average_intensity:.1f}/10），可能存在持续负面情绪"
        
        # 2. 趋势下降
        elif trend_direction == "declining":
            needs_intervention = True
            intervention_reason = "情绪趋势呈下降态势，需要关注"
        
        # 3. 连续多天高强度负面情绪
        negative_days = sum(1 for t in trend if t["average_intensity"] < 4.0 and t["dominant_emotion"] in ["sad", "anxious", "angry", "depressed"])
        if negative_days >= 3:
            needs_intervention = True
            intervention_reason = f"连续{negative_days}天出现负面情绪，建议关注"
        
        # 生成摘要
        if needs_intervention:
            summary = f"近{days}天情绪分析：平均强度{average_intensity:.1f}/10，趋势{trend_direction}，建议主动关怀"
        else:
            summary = f"近{days}天情绪分析：平均强度{average_intensity:.1f}/10，趋势{trend_direction}，状态稳定"
        
        return {
            "trend": trend,
            "average_intensity": round(average_intensity, 2),
            "trend_direction": trend_direction,
            "needs_intervention": needs_intervention,
            "intervention_reason": intervention_reason,
            "summary": summary
        }
        
    except Exception as e:
        return {
            "trend": [],
            "average_intensity": 5.0,
            "trend_direction": "stable",
            "needs_intervention": False,
            "intervention_reason": f"查询出错: {str(e)}",
            "summary": "无法获取情绪趋势数据",
            "error": str(e)
        }
    finally:
        db.close()


def play_meditation_audio(genre: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    播放冥想音频，缓解焦虑
    
    Args:
        genre: 音频类型（"sleep"/"anxiety"/"relaxation"/"breathing"等）
        user_id: 用户ID（可选）
        
    Returns:
        {
            "success": bool,
            "audio": Dict,  # 音频信息
            "message": str
        }
    """
    try:
        audio_player = _get_audio_player()
        
        # 映射genre到主题
        genre_map = {
            "sleep": "sleep",
            "anxiety": "anxiety",
            "relaxation": "relaxation",
            "breathing": "breathing",
            "meditation": "relaxation"
        }
        
        theme = genre_map.get(genre.lower(), "relaxation")
        
        # 搜索音频
        audio_list = audio_player.search_audio(
            theme=theme,
            category="meditation"
        )
        
        if not audio_list:
            # 如果没有找到，尝试搜索白噪音
            audio_list = audio_player.search_audio(category="white_noise")
        
        if not audio_list:
            return {
                "success": False,
                "error": f"未找到类型为'{genre}'的音频资源",
                "message": "抱歉，暂时没有可用的音频资源"
            }
        
        # 选择第一个音频
        selected_audio = audio_list[0]
        
        # 如果提供了user_id，记录播放历史
        if user_id:
            result = audio_player.play_audio(user_id, selected_audio["id"])
            return result
        
        return {
            "success": True,
            "audio": {
                "id": selected_audio["id"],
                "title": selected_audio["title"],
                "url": selected_audio.get("url", ""),
                "duration": selected_audio.get("duration", 0),
                "description": selected_audio.get("description", "")
            },
            "message": f"已为你准备：{selected_audio['title']}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "播放音频时出错"
        }


def set_daily_reminder(time: str, message: str, user_id: str) -> Dict[str, Any]:
    """
    设置每日提醒，养成作息习惯
    
    Args:
        time: 提醒时间，格式 "HH:MM" 或 "HH:MM:SS"
        message: 提醒消息内容
        user_id: 用户ID
        
    Returns:
        {
            "success": bool,
            "reminder_id": str,
            "message": str
        }
    """
    try:
        scheduler = _get_scheduler()
        
        # 解析时间
        time_parts = time.split(":")
        hour = int(time_parts[0])
        minute = int(time_parts[1]) if len(time_parts) > 1 else 0
        
        # 计算今天的提醒时间
        today = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # 如果今天的时间已过，设置为明天
        if today < datetime.now():
            today = today + timedelta(days=1)
        
        # 创建每日重复提醒
        reminder_id = scheduler.create_reminder(
            user_id=user_id,
            content=message,
            schedule_time=today,
            reminder_type=_get_reminder_type().DAILY,
            metadata={
                "source": "agent_tool",
                "created_at": datetime.now().isoformat()
            }
        )
        
        return {
            "success": True,
            "reminder_id": reminder_id,
            "scheduled_time": today.isoformat(),
            "time": time,
            "message": f"已设置每日提醒：每天{time}提醒你「{message}」"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "设置提醒时出错"
        }


def search_mental_health_resources(query: str, resource_type: Optional[str] = None) -> Dict[str, Any]:
    """
    检索专业心理文章，提供知识支持
    
    Args:
        query: 搜索关键词
        resource_type: 资源类型（"article"/"video"/"exercise"），可选
        
    Returns:
        {
            "count": int,
            "resources": List[Dict],
            "message": str
        }
    """
    try:
        psychology_db = _get_psychology_db()
        
        # 从查询中提取可能的分类
        category_map = {
            "焦虑": "anxiety",
            "抑郁": "depression",
            "睡眠": "sleep",
            "压力": "anxiety",
            "失眠": "sleep",
            "正念": "mindfulness",
            "冥想": "mindfulness"
        }
        
        category = None
        for keyword, cat in category_map.items():
            if keyword in query:
                category = cat
                break
        
        # 搜索资源
        resources = psychology_db.search_resources(
            category=category,
            resource_type=resource_type,
            tags=[query] if query else None
        )
        
        # 如果指定了资源类型，只返回该类型
        if resource_type:
            resources = [r for r in resources if r.get("resource_type") == resource_type]
        
        # 限制返回数量
        resources = resources[:5]
        
        # 格式化结果
        formatted_resources = []
        for resource in resources:
            formatted_resources.append({
                "id": resource.get("id", ""),
                "title": resource.get("title", ""),
                "type": resource.get("resource_type", ""),
                "url": resource.get("url", ""),
                "summary": resource.get("summary") or resource.get("description", ""),
                "read_time": resource.get("read_time", 0),
                "duration": resource.get("duration", 0),
                "tags": resource.get("tags", [])
            })
        
        return {
            "count": len(formatted_resources),
            "resources": formatted_resources,
            "query": query,
            "message": f"找到{len(formatted_resources)}个相关资源" if formatted_resources else "未找到相关资源"
        }
        
    except Exception as e:
        return {
            "count": 0,
            "resources": [],
            "error": str(e),
            "message": "搜索资源时出错"
        }


def send_follow_up_message(user_id: str, days_ago: int = 1, custom_message: Optional[str] = None) -> Dict[str, Any]:
    """
    发送回访消息，验证效果
    
    Args:
        user_id: 用户ID
        days_ago: 回访几天前的对话，默认1天前
        custom_message: 自定义消息内容（可选）
        
    Returns:
        {
            "success": bool,
            "message": str,
            "scheduled_at": str
        }
    """
    try:
        scheduler = _get_scheduler()
        
        # 计算回访时间（默认明天）
        follow_up_time = datetime.now() + timedelta(days=1)
        
        # 如果没有自定义消息，生成默认回访消息
        if not custom_message:
            # 查询用户最近的情绪状态
            mood_trend = get_user_mood_trend(user_id, days=days_ago + 1)
            
            if mood_trend.get("needs_intervention"):
                custom_message = f"你好，我注意到你最近的情绪有些波动。现在感觉怎么样？有什么想聊的吗？"
            else:
                custom_message = f"你好，距离我们上次聊天已经过去{days_ago}天了。最近感觉怎么样？有什么想分享的吗？"
        
        # 创建一次性提醒（回访消息）
        reminder_id = scheduler.create_reminder(
            user_id=user_id,
            content=custom_message,
            schedule_time=follow_up_time,
            reminder_type=_get_reminder_type().ONE_TIME,
            metadata={
                "source": "agent_follow_up",
                "follow_up_days": days_ago,
                "created_at": datetime.now().isoformat()
            }
        )
        
        return {
            "success": True,
            "reminder_id": reminder_id,
            "message": custom_message,
            "scheduled_at": follow_up_time.isoformat(),
            "days_ago": days_ago
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "发送回访消息时出错"
        }


# 导出所有工具函数
__all__ = [
    "get_user_mood_trend",
    "play_meditation_audio",
    "set_daily_reminder",
    "search_mental_health_resources",
    "send_follow_up_message"
]

