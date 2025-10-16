"""
测试模块
包含单元测试、集成测试和端到端测试
"""

import pytest
import asyncio
from typing import Any, Dict, Optional
from unittest.mock import Mock, AsyncMock

# 测试配置
pytest_plugins = ["pytest_asyncio"]


class TestConfig:
    """测试配置"""
    TEST_DATABASE_URL = "sqlite:///./test.db"
    TEST_REDIS_URL = "redis://localhost:6379/1"
    TEST_OPENAI_API_KEY = "test-key"
    TEST_ENVIRONMENT = "testing"


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_config():
    """模拟配置"""
    from unittest.mock import Mock
    
    config = Mock()
    config.database.url = TestConfig.TEST_DATABASE_URL
    config.redis.url = TestConfig.TEST_REDIS_URL
    config.openai.api_key = TestConfig.TEST_OPENAI_API_KEY
    config.environment = TestConfig.TEST_ENVIRONMENT
    config.debug = True
    
    return config


@pytest.fixture
def mock_logger():
    """模拟日志器"""
    from unittest.mock import Mock
    
    logger = Mock()
    logger.debug = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.critical = Mock()
    
    return logger


@pytest.fixture
async def mock_database():
    """模拟数据库"""
    from unittest.mock import AsyncMock
    
    db = AsyncMock()
    db.connect = AsyncMock(return_value=True)
    db.disconnect = AsyncMock(return_value=True)
    db.execute_query = AsyncMock(return_value=[])
    db.health_check = AsyncMock(return_value={"status": "healthy"})
    
    return db


@pytest.fixture
async def mock_cache():
    """模拟缓存"""
    from unittest.mock import AsyncMock
    
    cache = AsyncMock()
    cache.get = AsyncMock(return_value=None)
    cache.set = AsyncMock(return_value=True)
    cache.delete = AsyncMock(return_value=True)
    cache.exists = AsyncMock(return_value=False)
    
    return cache


@pytest.fixture
def sample_chat_request():
    """示例聊天请求"""
    return {
        "message": "你好，我今天心情不好",
        "user_id": "test_user_123",
        "session_id": "test_session_456",
        "emotion": "难过",
        "emotion_intensity": 6.5,
        "use_memory": True,
        "use_rag": True
    }


@pytest.fixture
def sample_chat_response():
    """示例聊天响应"""
    return {
        "success": True,
        "message": "回复生成成功",
        "response": "我理解你现在的心情不好，能告诉我发生了什么吗？",
        "emotion": "难过",
        "emotion_intensity": 6.5,
        "session_id": "test_session_456",
        "timestamp": "2025-10-16T14:30:00Z",
        "status_code": 200,
        "context": {
            "memories_count": 3,
            "emotion_trend": "上升",
            "has_profile": True,
            "used_rag": False
        }
    }


@pytest.fixture
def sample_memory():
    """示例记忆"""
    return {
        "id": "memory_123",
        "content": "用户今天心情不好",
        "emotion": "难过",
        "importance": 0.8,
        "timestamp": "2025-10-16T14:30:00Z",
        "metadata": {
            "user_id": "test_user_123",
            "session_id": "test_session_456",
            "source": "user_message"
        }
    }


@pytest.fixture
def sample_rag_result():
    """示例RAG结果"""
    return {
        "answer": "根据心理学研究，当你感到难过时，可以尝试以下方法...",
        "sources": [
            {
                "content": "心理学研究表明...",
                "metadata": {
                    "topic": "情绪管理",
                    "source": "内置知识库"
                }
            }
        ],
        "confidence": 0.85,
        "knowledge_count": 1,
        "used_context": True
    }


# 测试工具函数
def assert_response_structure(response: Dict[str, Any]):
    """断言响应结构"""
    assert "success" in response
    assert "message" in response
    assert "timestamp" in response
    assert "status_code" in response


def assert_error_response(response: Dict[str, Any], expected_status: int = 400):
    """断言错误响应"""
    assert_response_structure(response)
    assert response["success"] is False
    assert response["status_code"] == expected_status
    assert "error" in response


def assert_success_response(response: Dict[str, Any], expected_status: int = 200):
    """断言成功响应"""
    assert_response_structure(response)
    assert response["success"] is True
    assert response["status_code"] == expected_status


async def wait_for_condition(condition_func, timeout: float = 5.0, interval: float = 0.1):
    """等待条件满足"""
    import time
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        if await condition_func() if asyncio.iscoroutinefunction(condition_func) else condition_func():
            return True
        await asyncio.sleep(interval)
    
    return False


def create_mock_openai_response(content: str = "测试回复"):
    """创建模拟OpenAI响应"""
    return {
        "choices": [
            {
                "message": {
                    "content": content,
                    "role": "assistant"
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150
        }
    }


def create_mock_emotion_analysis(emotion: str = "neutral", intensity: float = 5.0):
    """创建模拟情绪分析结果"""
    return {
        "emotion": emotion,
        "intensity": intensity,
        "confidence": 0.85,
        "details": {
            "positive_score": 0.3,
            "negative_score": 0.7,
            "neutral_score": 0.5
        }
    }
