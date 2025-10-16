#!/usr/bin/env python3
"""
辅助函数模块
包含各种实用工具函数
"""

import uuid
import hashlib
import re
import string
import random
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime, timedelta
import json
import asyncio
from functools import wraps


def generate_id(prefix: str = "", length: int = 8) -> str:
    """生成唯一ID"""
    if prefix:
        return f"{prefix}_{uuid.uuid4().hex[:length]}"
    return uuid.uuid4().hex[:length]


def generate_session_id() -> str:
    """生成会话ID"""
    return str(uuid.uuid4())


def generate_user_id(prefix: str = "user") -> str:
    """生成用户ID"""
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def generate_short_code(length: int = 6) -> str:
    """生成短码"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def calculate_hash(text: str, algorithm: str = "sha256") -> str:
    """计算文本哈希值"""
    if algorithm == "md5":
        return hashlib.md5(text.encode()).hexdigest()
    elif algorithm == "sha1":
        return hashlib.sha1(text.encode()).hexdigest()
    elif algorithm == "sha256":
        return hashlib.sha256(text.encode()).hexdigest()
    else:
        raise ValueError(f"不支持的哈希算法: {algorithm}")


def sanitize_text(text: str, max_length: int = 2000) -> str:
    """清理文本"""
    if not isinstance(text, str):
        return ""
    
    # 移除控制字符
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    
    # 标准化空白字符
    text = re.sub(r'\s+', ' ', text.strip())
    
    # 限制长度
    if len(text) > max_length:
        text = text[:max_length]
    
    return text


def extract_emotion_keywords(text: str) -> List[str]:
    """从文本中提取情绪关键词"""
    emotion_keywords = {
        "positive": ["开心", "快乐", "兴奋", "满足", "幸福", "愉悦", "轻松", "平静", "好", "棒", "赞"],
        "negative": ["难过", "悲伤", "愤怒", "焦虑", "恐惧", "失望", "沮丧", "紧张", "坏", "糟", "烦"],
        "neutral": ["正常", "一般", "平淡", "无聊", "困惑", "思考", "还行", "可以"]
    }
    
    found_keywords = []
    text_lower = text.lower()
    
    for category, keywords in emotion_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
    
    return found_keywords


def calculate_similarity(text1: str, text2: str) -> float:
    """计算文本相似度（简单的Jaccard相似度）"""
    if not text1 or not text2:
        return 0.0
    
    # 分词
    words1 = set(re.findall(r'\w+', text1.lower()))
    words2 = set(re.findall(r'\w+', text2.lower()))
    
    if not words1 and not words2:
        return 1.0
    
    if not words1 or not words2:
        return 0.0
    
    # 计算Jaccard相似度
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    
    return intersection / union if union > 0 else 0.0


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """合并多个字典"""
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """深度合并字典"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """扁平化嵌套字典"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """将列表分块"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def remove_duplicates(lst: List[Any], key_func: Optional[callable] = None) -> List[Any]:
    """移除列表中的重复项"""
    if key_func is None:
        return list(dict.fromkeys(lst))
    
    seen = set()
    result = []
    for item in lst:
        key = key_func(item)
        if key not in seen:
            seen.add(key)
            result.append(item)
    
    return result


def safe_get(data: Dict[str, Any], keys: Union[str, List[str]], default: Any = None) -> Any:
    """安全获取嵌套字典的值"""
    if isinstance(keys, str):
        keys = keys.split('.')
    
    try:
        result = data
        for key in keys:
            result = result[key]
        return result
    except (KeyError, TypeError):
        return default


def safe_set(data: Dict[str, Any], keys: Union[str, List[str]], value: Any) -> bool:
    """安全设置嵌套字典的值"""
    if isinstance(keys, str):
        keys = keys.split('.')
    
    try:
        result = data
        for key in keys[:-1]:
            if key not in result or not isinstance(result[key], dict):
                result[key] = {}
            result = result[key]
        result[keys[-1]] = value
        return True
    except (TypeError, KeyError):
        return False


def format_duration(seconds: float) -> str:
    """格式化持续时间"""
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}分钟"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}小时"


def format_file_size(bytes_size: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f}{unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f}PB"


def parse_duration(duration_str: str) -> int:
    """解析持续时间字符串为秒数"""
    duration_str = duration_str.lower().strip()
    
    if duration_str.endswith('s'):
        return int(duration_str[:-1])
    elif duration_str.endswith('m'):
        return int(duration_str[:-1]) * 60
    elif duration_str.endswith('h'):
        return int(duration_str[:-1]) * 3600
    elif duration_str.endswith('d'):
        return int(duration_str[:-1]) * 86400
    else:
        return int(duration_str)


def is_valid_email(email: str) -> bool:
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_valid_phone(phone: str) -> bool:
    """验证手机号格式"""
    pattern = r'^(\+?86)?1[3-9]\d{9}$'
    return re.match(pattern, phone) is not None


def mask_sensitive_data(text: str, mask_char: str = '*') -> str:
    """遮蔽敏感数据"""
    if len(text) <= 4:
        return mask_char * len(text)
    
    return text[:2] + mask_char * (len(text) - 4) + text[-2:]


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """截断文本"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def normalize_text(text: str) -> str:
    """标准化文本"""
    # 转换为小写
    text = text.lower()
    
    # 移除多余空格
    text = re.sub(r'\s+', ' ', text.strip())
    
    # 移除特殊字符（保留中文、英文、数字、基本标点）
    text = re.sub(r'[^\u4e00-\u9fff\w\s.,!?;:()""''""''-]', '', text)
    
    return text


def extract_urls(text: str) -> List[str]:
    """从文本中提取URL"""
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(url_pattern, text)


def extract_emails(text: str) -> List[str]:
    """从文本中提取邮箱"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, text)


def extract_phone_numbers(text: str) -> List[str]:
    """从文本中提取手机号"""
    phone_pattern = r'(\+?86)?1[3-9]\d{9}'
    return re.findall(phone_pattern, text)


def create_timestamp(timezone_offset: int = 0) -> str:
    """创建时间戳"""
    dt = datetime.now() + timedelta(hours=timezone_offset)
    return dt.isoformat()


def parse_timestamp(timestamp: str) -> Optional[datetime]:
    """解析时间戳"""
    try:
        return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    except ValueError:
        return None


def is_within_timeframe(
    timestamp: str,
    timeframe: str,
    reference_time: Optional[datetime] = None
) -> bool:
    """检查时间戳是否在指定时间范围内"""
    if reference_time is None:
        reference_time = datetime.now()
    
    parsed_time = parse_timestamp(timestamp)
    if parsed_time is None:
        return False
    
    duration_seconds = parse_duration(timeframe)
    time_diff = (reference_time - parsed_time).total_seconds()
    
    return 0 <= time_diff <= duration_seconds


def retry_async(max_attempts: int = 3, delay: float = 1.0):
    """异步重试装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(delay * (2 ** attempt))
                    else:
                        raise last_exception
            
            return None
        return wrapper
    return decorator


def timeout_async(seconds: float):
    """异步超时装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
        return wrapper
    return decorator


def batch_process(items: List[Any], batch_size: int, processor: callable) -> List[Any]:
    """批量处理"""
    results = []
    for batch in chunk_list(items, batch_size):
        batch_result = processor(batch)
        results.extend(batch_result)
    return results


def create_progress_tracker(total: int):
    """创建进度跟踪器"""
    class ProgressTracker:
        def __init__(self, total: int):
            self.total = total
            self.current = 0
        
        def update(self, increment: int = 1):
            self.current += increment
        
        def get_progress(self) -> float:
            return self.current / self.total if self.total > 0 else 0
        
        def is_complete(self) -> bool:
            return self.current >= self.total
    
    return ProgressTracker(total)


# 使用示例
if __name__ == "__main__":
    # 测试辅助函数
    print("生成ID:", generate_id("test", 8))
    print("计算哈希:", calculate_hash("hello world"))
    print("文本相似度:", calculate_similarity("hello world", "hello there"))
    print("提取情绪关键词:", extract_emotion_keywords("我今天很开心，但有点焦虑"))
    print("格式化持续时间:", format_duration(3661))
    print("格式化文件大小:", format_file_size(1024000))
    print("遮蔽敏感数据:", mask_sensitive_data("13812345678"))
    print("标准化文本:", normalize_text("  Hello   World!  "))
