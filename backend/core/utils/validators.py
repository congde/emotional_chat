#!/usr/bin/env python3
"""
验证器模块
包含各种输入验证函数
"""

import re
import uuid
from typing import Optional, List, Tuple, Any, Dict
from datetime import datetime

from ..exceptions import ValidationError


# 正则表达式模式
EMAIL_PATTERN = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)

PHONE_PATTERN = re.compile(
    r'^(\+?86)?1[3-9]\d{9}$|^(\+\d{1,3})?\d{10,15}$'
)

USER_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{3,50}$')

SESSION_ID_PATTERN = re.compile(r'^[a-f0-9-]{36}$')

# 敏感词列表（示例）
FORBIDDEN_WORDS = [
    "自杀", "自残", "伤害", "暴力", "仇恨", "歧视"
]

# 情绪关键词
EMOTION_KEYWORDS = {
    "positive": ["开心", "快乐", "兴奋", "满足", "幸福", "愉悦", "轻松", "平静"],
    "negative": ["难过", "悲伤", "愤怒", "焦虑", "恐惧", "失望", "沮丧", "紧张"],
    "neutral": ["正常", "一般", "平淡", "无聊", "困惑", "思考"]
}


def validate_email(email: str) -> Tuple[bool, str]:
    """验证邮箱格式"""
    if not email or not isinstance(email, str):
        return False, "邮箱不能为空"
    
    if len(email) > 254:
        return False, "邮箱长度不能超过254个字符"
    
    if not EMAIL_PATTERN.match(email):
        return False, "邮箱格式不正确"
    
    return True, "邮箱格式正确"


def validate_phone(phone: str) -> Tuple[bool, str]:
    """验证手机号格式"""
    if not phone or not isinstance(phone, str):
        return False, "手机号不能为空"
    
    # 移除空格和特殊字符
    clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    if not PHONE_PATTERN.match(clean_phone):
        return False, "手机号格式不正确"
    
    return True, "手机号格式正确"


def validate_text_length(
    text: str,
    min_length: int = 1,
    max_length: int = 1000
) -> Tuple[bool, str]:
    """验证文本长度"""
    if not isinstance(text, str):
        return False, "文本必须是字符串"
    
    if len(text.strip()) < min_length:
        return False, f"文本长度不能少于{min_length}个字符"
    
    if len(text) > max_length:
        return False, f"文本长度不能超过{max_length}个字符"
    
    return True, "文本长度符合要求"


def validate_session_id(session_id: str) -> Tuple[bool, str]:
    """验证会话ID格式"""
    if not session_id or not isinstance(session_id, str):
        return False, "会话ID不能为空"
    
    if not SESSION_ID_PATTERN.match(session_id):
        return False, "会话ID格式不正确，应为UUID格式"
    
    return True, "会话ID格式正确"


def validate_user_id(user_id: str) -> Tuple[bool, str]:
    """验证用户ID格式"""
    if not user_id or not isinstance(user_id, str):
        return False, "用户ID不能为空"
    
    if not USER_ID_PATTERN.match(user_id):
        return False, "用户ID格式不正确，应为3-50位字母、数字、下划线或连字符"
    
    return True, "用户ID格式正确"


def validate_message_content(message: str) -> Tuple[bool, str]:
    """验证消息内容"""
    # 基本验证
    valid, error = validate_text_length(message, 1, 2000)
    if not valid:
        return valid, error
    
    # 检查敏感词
    message_lower = message.lower()
    for word in FORBIDDEN_WORDS:
        if word in message_lower:
            return False, f"消息包含敏感词：{word}"
    
    # 检查是否为纯符号或数字
    if re.match(r'^[\s\d\W]+$', message):
        return False, "消息内容不能只包含符号或数字"
    
    return True, "消息内容验证通过"


def validate_emotion_value(emotion: str) -> Tuple[bool, str]:
    """验证情绪值"""
    valid_emotions = [
        "开心", "快乐", "兴奋", "满足", "幸福", "愉悦", "轻松", "平静",
        "难过", "悲伤", "愤怒", "焦虑", "恐惧", "失望", "沮丧", "紧张",
        "neutral", "正常", "一般", "平淡", "无聊", "困惑", "思考"
    ]
    
    if not emotion or not isinstance(emotion, str):
        return False, "情绪值不能为空"
    
    if emotion not in valid_emotions:
        return False, f"无效的情绪值：{emotion}"
    
    return True, "情绪值验证通过"


def validate_emotion_intensity(intensity: float) -> Tuple[bool, str]:
    """验证情绪强度"""
    if not isinstance(intensity, (int, float)):
        return False, "情绪强度必须是数字"
    
    if not (0 <= intensity <= 10):
        return False, "情绪强度必须在0-10之间"
    
    return True, "情绪强度验证通过"


def validate_rating(rating: int) -> Tuple[bool, str]:
    """验证评分"""
    if not isinstance(rating, int):
        return False, "评分必须是整数"
    
    if not (1 <= rating <= 5):
        return False, "评分必须在1-5之间"
    
    return True, "评分验证通过"


def validate_timestamp(timestamp: str) -> Tuple[bool, str]:
    """验证时间戳格式"""
    if not timestamp or not isinstance(timestamp, str):
        return False, "时间戳不能为空"
    
    try:
        datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return True, "时间戳格式正确"
    except ValueError:
        return False, "时间戳格式不正确，应为ISO格式"


def validate_pagination_params(page: int, page_size: int) -> Tuple[bool, str]:
    """验证分页参数"""
    if not isinstance(page, int) or page < 1:
        return False, "页码必须是大于0的整数"
    
    if not isinstance(page_size, int) or not (1 <= page_size <= 100):
        return False, "每页大小必须在1-100之间"
    
    return True, "分页参数验证通过"


def validate_search_query(query: str) -> Tuple[bool, str]:
    """验证搜索查询"""
    if not query or not isinstance(query, str):
        return False, "搜索查询不能为空"
    
    if len(query.strip()) < 2:
        return False, "搜索查询至少需要2个字符"
    
    if len(query) > 100:
        return False, "搜索查询不能超过100个字符"
    
    return True, "搜索查询验证通过"


def validate_file_upload(
    filename: str,
    file_size: int,
    allowed_extensions: List[str] = None,
    max_size: int = 10 * 1024 * 1024  # 10MB
) -> Tuple[bool, str]:
    """验证文件上传"""
    if not filename or not isinstance(filename, str):
        return False, "文件名不能为空"
    
    if not isinstance(file_size, int) or file_size <= 0:
        return False, "文件大小必须大于0"
    
    if file_size > max_size:
        return False, f"文件大小不能超过{max_size // (1024*1024)}MB"
    
    if allowed_extensions:
        file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
        if file_ext not in allowed_extensions:
            return False, f"不支持的文件格式，允许的格式：{', '.join(allowed_extensions)}"
    
    return True, "文件上传验证通过"


def validate_config_value(key: str, value: Any, config_type: str) -> Tuple[bool, str]:
    """验证配置值"""
    if not key or not isinstance(key, str):
        return False, "配置键不能为空"
    
    if config_type == "string" and not isinstance(value, str):
        return False, f"配置{key}必须是字符串"
    
    elif config_type == "int" and not isinstance(value, int):
        return False, f"配置{key}必须是整数"
    
    elif config_type == "float" and not isinstance(value, (int, float)):
        return False, f"配置{key}必须是数字"
    
    elif config_type == "bool" and not isinstance(value, bool):
        return False, f"配置{key}必须是布尔值"
    
    return True, "配置值验证通过"


def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, str]:
    """简单的JSON模式验证"""
    try:
        for field, rules in schema.items():
            if field not in data:
                if rules.get("required", False):
                    return False, f"缺少必需字段：{field}"
                continue
            
            value = data[field]
            field_type = rules.get("type")
            
            if field_type == "string" and not isinstance(value, str):
                return False, f"字段{field}必须是字符串"
            
            elif field_type == "int" and not isinstance(value, int):
                return False, f"字段{field}必须是整数"
            
            elif field_type == "float" and not isinstance(value, (int, float)):
                return False, f"字段{field}必须是数字"
            
            elif field_type == "bool" and not isinstance(value, bool):
                return False, f"字段{field}必须是布尔值"
            
            elif field_type == "list" and not isinstance(value, list):
                return False, f"字段{field}必须是列表"
            
            elif field_type == "dict" and not isinstance(value, dict):
                return False, f"字段{field}必须是字典"
            
            # 检查长度限制
            if "min_length" in rules:
                if len(str(value)) < rules["min_length"]:
                    return False, f"字段{field}长度不能少于{rules['min_length']}个字符"
            
            if "max_length" in rules:
                if len(str(value)) > rules["max_length"]:
                    return False, f"字段{field}长度不能超过{rules['max_length']}个字符"
            
            # 检查值范围
            if "min_value" in rules and isinstance(value, (int, float)):
                if value < rules["min_value"]:
                    return False, f"字段{field}值不能小于{rules['min_value']}"
            
            if "max_value" in rules and isinstance(value, (int, float)):
                if value > rules["max_value"]:
                    return False, f"字段{field}值不能大于{rules['max_value']}"
        
        return True, "JSON模式验证通过"
    
    except Exception as e:
        return False, f"验证过程中发生错误：{str(e)}"


def sanitize_input(text: str) -> str:
    """清理输入文本"""
    if not isinstance(text, str):
        return ""
    
    # 移除多余的空白字符
    text = re.sub(r'\s+', ' ', text.strip())
    
    # 移除控制字符
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    
    # 限制长度
    if len(text) > 2000:
        text = text[:2000]
    
    return text


def extract_emotion_keywords(text: str) -> List[str]:
    """从文本中提取情绪关键词"""
    if not isinstance(text, str):
        return []
    
    text_lower = text.lower()
    found_keywords = []
    
    for category, keywords in EMOTION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
    
    return found_keywords


# 验证装饰器
def validate_request_data(schema: Dict[str, Any]):
    """请求数据验证装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 查找request参数
            request_data = None
            for arg in args:
                if isinstance(arg, dict):
                    request_data = arg
                    break
            
            if request_data:
                valid, error = validate_json_schema(request_data, schema)
                if not valid:
                    raise ValidationError(error)
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


# 使用示例
if __name__ == "__main__":
    # 测试验证函数
    print("测试邮箱验证:", validate_email("test@example.com"))
    print("测试手机号验证:", validate_phone("13812345678"))
    print("测试文本长度验证:", validate_text_length("Hello World"))
    print("测试会话ID验证:", validate_session_id(str(uuid.uuid4())))
    print("测试消息内容验证:", validate_message_content("你好，今天天气不错"))
    print("测试情绪关键词提取:", extract_emotion_keywords("我今天很开心，但有点焦虑"))
