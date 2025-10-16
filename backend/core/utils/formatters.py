#!/usr/bin/env python3
"""
格式化器模块
包含各种数据格式化函数
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timezone
import json
import uuid

from ..exceptions import EmotionalChatException
from .interfaces import EmotionResult


def format_response(
    data: Any = None,
    message: str = "success",
    status_code: int = 200,
    success: bool = True,
    timestamp: Optional[str] = None
) -> Dict[str, Any]:
    """格式化API响应"""
    if timestamp is None:
        timestamp = datetime.now(timezone.utc).isoformat()
    
    response = {
        "success": success,
        "message": message,
        "timestamp": timestamp,
        "status_code": status_code
    }
    
    if data is not None:
        response["data"] = data
    
    return response


def format_error(
    error: Union[str, Exception],
    error_code: Optional[str] = None,
    status_code: int = 500,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """格式化错误响应"""
    if isinstance(error, Exception):
        message = str(error)
        if hasattr(error, 'error_code'):
            error_code = getattr(error, 'error_code')
        if hasattr(error, 'details'):
            details = getattr(error, 'details')
    else:
        message = str(error)
    
    return {
        "success": False,
        "error": {
            "code": error_code or "UNKNOWN_ERROR",
            "message": message,
            "details": details or {}
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status_code": status_code
    }


def format_timestamp(
    dt: Optional[datetime] = None,
    format_type: str = "iso",
    timezone_info: Optional[timezone] = None
) -> str:
    """格式化时间戳"""
    if dt is None:
        dt = datetime.now(timezone_info or timezone.utc)
    
    if format_type == "iso":
        return dt.isoformat()
    elif format_type == "rfc":
        return dt.strftime("%a, %d %b %Y %H:%M:%S GMT")
    elif format_type == "unix":
        return str(int(dt.timestamp()))
    elif format_type == "readable":
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return dt.strftime(format_type)


def format_emotion_result(emotion_result: EmotionResult) -> Dict[str, Any]:
    """格式化情绪分析结果"""
    return {
        "emotion": emotion_result.emotion,
        "intensity": round(emotion_result.intensity, 2),
        "confidence": round(emotion_result.confidence, 3),
        "details": emotion_result.details,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def format_chat_message(
    role: str,
    content: str,
    emotion: Optional[str] = None,
    emotion_intensity: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """格式化聊天消息"""
    message = {
        "id": str(uuid.uuid4()),
        "role": role,
        "content": content,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    if emotion:
        message["emotion"] = emotion
    
    if emotion_intensity is not None:
        message["emotion_intensity"] = round(emotion_intensity, 2)
    
    if metadata:
        message["metadata"] = metadata
    
    return message


def format_session_info(
    session_id: str,
    user_id: str,
    created_at: Optional[datetime] = None,
    last_activity: Optional[datetime] = None,
    message_count: int = 0,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """格式化会话信息"""
    session_info = {
        "session_id": session_id,
        "user_id": user_id,
        "message_count": message_count,
        "created_at": format_timestamp(created_at) if created_at else None,
        "last_activity": format_timestamp(last_activity) if last_activity else None
    }
    
    if metadata:
        session_info["metadata"] = metadata
    
    return session_info


def format_memory_info(
    memory_id: str,
    content: str,
    emotion: str,
    importance: float,
    created_at: Optional[datetime] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """格式化记忆信息"""
    memory_info = {
        "id": memory_id,
        "content": content,
        "emotion": emotion,
        "importance": round(importance, 3),
        "created_at": format_timestamp(created_at) if created_at else None
    }
    
    if metadata:
        memory_info["metadata"] = metadata
    
    return memory_info


def format_user_profile(
    user_id: str,
    preferences: Optional[Dict[str, Any]] = None,
    emotion_history: Optional[List[Dict[str, Any]]] = None,
    session_count: int = 0,
    total_messages: int = 0,
    created_at: Optional[datetime] = None,
    last_active: Optional[datetime] = None
) -> Dict[str, Any]:
    """格式化用户档案"""
    profile = {
        "user_id": user_id,
        "session_count": session_count,
        "total_messages": total_messages,
        "created_at": format_timestamp(created_at) if created_at else None,
        "last_active": format_timestamp(last_active) if last_active else None
    }
    
    if preferences:
        profile["preferences"] = preferences
    
    if emotion_history:
        profile["emotion_history"] = emotion_history[:10]  # 只保留最近10条
    
    return profile


def format_rag_result(
    answer: str,
    sources: List[Dict[str, Any]],
    confidence: float,
    knowledge_count: int,
    used_context: bool = False,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """格式化RAG结果"""
    result = {
        "answer": answer,
        "sources": sources,
        "confidence": round(confidence, 3),
        "knowledge_count": knowledge_count,
        "used_context": used_context,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    if metadata:
        result["metadata"] = metadata
    
    return result


def format_evaluation_result(
    user_message: str,
    bot_response: str,
    scores: Dict[str, float],
    feedback: Optional[str] = None,
    evaluator_id: Optional[str] = None
) -> Dict[str, Any]:
    """格式化评估结果"""
    return {
        "user_message": user_message,
        "bot_response": bot_response,
        "scores": {k: round(v, 3) for k, v in scores.items()},
        "overall_score": round(sum(scores.values()) / len(scores), 3),
        "feedback": feedback,
        "evaluator_id": evaluator_id,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def format_feedback_info(
    feedback_id: str,
    user_id: str,
    session_id: str,
    feedback_type: str,
    content: str,
    rating: Optional[int] = None,
    created_at: Optional[datetime] = None,
    analyzed: bool = False
) -> Dict[str, Any]:
    """格式化反馈信息"""
    feedback_info = {
        "id": feedback_id,
        "user_id": user_id,
        "session_id": session_id,
        "type": feedback_type,
        "content": content,
        "analyzed": analyzed,
        "created_at": format_timestamp(created_at) if created_at else None
    }
    
    if rating is not None:
        feedback_info["rating"] = rating
    
    return feedback_info


def format_statistics(
    total_users: int,
    total_sessions: int,
    total_messages: int,
    active_sessions: int,
    emotion_distribution: Optional[Dict[str, int]] = None,
    time_range: Optional[str] = None
) -> Dict[str, Any]:
    """格式化统计信息"""
    stats = {
        "total_users": total_users,
        "total_sessions": total_sessions,
        "total_messages": total_messages,
        "active_sessions": active_sessions,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    if emotion_distribution:
        stats["emotion_distribution"] = emotion_distribution
    
    if time_range:
        stats["time_range"] = time_range
    
    return stats


def format_pagination_info(
    page: int,
    page_size: int,
    total: int,
    items: List[Any]
) -> Dict[str, Any]:
    """格式化分页信息"""
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "items": items,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }


def format_health_check(
    status: str,
    services: Dict[str, str],
    version: str,
    uptime: Optional[str] = None
) -> Dict[str, Any]:
    """格式化健康检查结果"""
    health_info = {
        "status": status,
        "version": version,
        "services": services,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    if uptime:
        health_info["uptime"] = uptime
    
    return health_info


def format_config_info(config_dict: Dict[str, Any]) -> Dict[str, Any]:
    """格式化配置信息（隐藏敏感信息）"""
    sensitive_keys = {
        "password", "secret", "key", "token", "api_key", "private_key"
    }
    
    formatted_config = {}
    for key, value in config_dict.items():
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            formatted_config[key] = "***"
        elif isinstance(value, dict):
            formatted_config[key] = format_config_info(value)
        else:
            formatted_config[key] = value
    
    return formatted_config


def format_log_entry(
    level: str,
    message: str,
    module: str,
    function: str,
    line_number: int,
    exception: Optional[Exception] = None,
    extra_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """格式化日志条目"""
    log_entry = {
        "level": level,
        "message": message,
        "module": module,
        "function": function,
        "line_number": line_number,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    if exception:
        log_entry["exception"] = {
            "type": type(exception).__name__,
            "message": str(exception)
        }
    
    if extra_data:
        log_entry["extra_data"] = extra_data
    
    return log_entry


def format_json_safe(obj: Any) -> Any:
    """确保对象可以JSON序列化"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, dict):
        return {k: format_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [format_json_safe(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        return format_json_safe(obj.__dict__)
    else:
        try:
            json.dumps(obj)
            return obj
        except (TypeError, ValueError):
            return str(obj)


def pretty_print_json(data: Any, indent: int = 2) -> str:
    """美化JSON输出"""
    return json.dumps(
        format_json_safe(data),
        indent=indent,
        ensure_ascii=False,
        sort_keys=True
    )


# 使用示例
if __name__ == "__main__":
    # 测试格式化函数
    print("测试响应格式化:")
    print(format_response({"test": "data"}, "操作成功"))
    
    print("\n测试错误格式化:")
    print(format_error("测试错误", "TEST_ERROR", 400))
    
    print("\n测试时间戳格式化:")
    print(format_timestamp())
    
    print("\n测试聊天消息格式化:")
    print(format_chat_message("user", "你好", "开心", 7.5))
    
    print("\n测试JSON美化:")
    test_data = {
        "name": "测试",
        "age": 25,
        "created_at": datetime.now(),
        "items": [1, 2, 3]
    }
    print(pretty_print_json(test_data))
