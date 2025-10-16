#!/usr/bin/env python3
"""
核心模块单元测试
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from backend.core.config import Config, get_config, Environment
from backend.core.exceptions import (
    EmotionalChatException,
    ValidationError,
    ConfigurationError,
    DatabaseError
)
from backend.core.utils.validators import (
    validate_email,
    validate_phone,
    validate_text_length,
    validate_session_id
)
from backend.core.utils.formatters import (
    format_response,
    format_error,
    format_timestamp
)
from backend.core.utils.helpers import (
    generate_id,
    sanitize_text,
    extract_emotion_keywords,
    calculate_similarity
)


class TestConfig:
    """配置测试"""
    
    def test_config_creation(self):
        """测试配置创建"""
        config = Config()
        assert config.environment == Environment.DEVELOPMENT
        assert config.debug is True
        assert config.api.port == 8000
    
    def test_config_environment_validation(self):
        """测试环境验证"""
        config = Config()
        assert config.is_development() is True
        assert config.is_production() is False
        assert config.is_testing() is False
    
    def test_config_to_dict(self):
        """测试配置转字典"""
        config = Config()
        config_dict = config.to_dict()
        
        assert "environment" in config_dict
        assert "debug" in config_dict
        assert "database" in config_dict
        assert "openai" in config_dict
        assert "api" in config_dict
    
    @patch.dict('os.environ', {'ENVIRONMENT': 'production', 'DEBUG': 'false'})
    def test_config_from_env(self):
        """测试从环境变量加载配置"""
        config = Config()
        assert config.environment == Environment.PRODUCTION
        assert config.debug is False


class TestExceptions:
    """异常测试"""
    
    def test_emotional_chat_exception(self):
        """测试基础异常"""
        exc = EmotionalChatException("测试错误", "TEST_ERROR")
        assert exc.message == "测试错误"
        assert exc.error_code == "TEST_ERROR"
        
        error_dict = exc.to_dict()
        assert error_dict["error_code"] == "TEST_ERROR"
        assert error_dict["message"] == "测试错误"
    
    def test_validation_error(self):
        """测试验证异常"""
        exc = ValidationError("验证失败", field="email", value="invalid")
        assert exc.field == "email"
        assert exc.value == "invalid"
        
        error_dict = exc.to_dict()
        assert error_dict["field"] == "email"
        assert error_dict["value"] == "invalid"
    
    def test_configuration_error(self):
        """测试配置异常"""
        exc = ConfigurationError("配置错误")
        assert isinstance(exc, EmotionalChatException)
        assert exc.message == "配置错误"
    
    def test_database_error(self):
        """测试数据库异常"""
        exc = DatabaseError("数据库连接失败")
        assert isinstance(exc, EmotionalChatException)
        assert exc.message == "数据库连接失败"


class TestValidators:
    """验证器测试"""
    
    def test_validate_email(self):
        """测试邮箱验证"""
        # 有效邮箱
        valid, msg = validate_email("test@example.com")
        assert valid is True
        assert "正确" in msg
        
        # 无效邮箱
        valid, msg = validate_email("invalid-email")
        assert valid is False
        assert "格式不正确" in msg
        
        # 空邮箱
        valid, msg = validate_email("")
        assert valid is False
        assert "不能为空" in msg
    
    def test_validate_phone(self):
        """测试手机号验证"""
        # 有效手机号
        valid, msg = validate_phone("13812345678")
        assert valid is True
        
        # 无效手机号
        valid, msg = validate_phone("12345678901")
        assert valid is False
        
        # 带国际区号
        valid, msg = validate_phone("+8613812345678")
        assert valid is True
    
    def test_validate_text_length(self):
        """测试文本长度验证"""
        # 有效文本
        valid, msg = validate_text_length("Hello World", 1, 100)
        assert valid is True
        
        # 过短文本
        valid, msg = validate_text_length("", 1, 100)
        assert valid is False
        
        # 过长文本
        valid, msg = validate_text_length("x" * 200, 1, 100)
        assert valid is False
    
    def test_validate_session_id(self):
        """测试会话ID验证"""
        import uuid
        
        # 有效UUID
        session_id = str(uuid.uuid4())
        valid, msg = validate_session_id(session_id)
        assert valid is True
        
        # 无效格式
        valid, msg = validate_session_id("invalid-id")
        assert valid is False


class TestFormatters:
    """格式化器测试"""
    
    def test_format_response(self):
        """测试响应格式化"""
        response = format_response(
            data={"test": "data"},
            message="成功",
            status_code=200
        )
        
        assert response["success"] is True
        assert response["message"] == "成功"
        assert response["status_code"] == 200
        assert response["data"]["test"] == "data"
        assert "timestamp" in response
    
    def test_format_error(self):
        """测试错误格式化"""
        error = format_error(
            error="测试错误",
            error_code="TEST_ERROR",
            status_code=400
        )
        
        assert error["success"] is False
        assert error["error"]["code"] == "TEST_ERROR"
        assert error["error"]["message"] == "测试错误"
        assert error["status_code"] == 400
    
    def test_format_timestamp(self):
        """测试时间戳格式化"""
        dt = datetime(2025, 10, 16, 14, 30, 0)
        
        # ISO格式
        iso_timestamp = format_timestamp(dt, "iso")
        assert "2025-10-16T14:30:00" in iso_timestamp
        
        # 可读格式
        readable = format_timestamp(dt, "readable")
        assert "2025-10-16 14:30:00" in readable


class TestHelpers:
    """辅助函数测试"""
    
    def test_generate_id(self):
        """测试ID生成"""
        # 无前缀
        id1 = generate_id()
        assert len(id1) == 8
        assert id1.isalnum()
        
        # 有前缀
        id2 = generate_id("test", 12)
        assert id2.startswith("test_")
        assert len(id2) == len("test_") + 12
    
    def test_sanitize_text(self):
        """测试文本清理"""
        # 正常文本
        text = "Hello World"
        sanitized = sanitize_text(text)
        assert sanitized == "Hello World"
        
        # 包含控制字符
        text_with_control = "Hello\x00World"
        sanitized = sanitize_text(text_with_control)
        assert "\x00" not in sanitized
        
        # 过长文本
        long_text = "x" * 3000
        sanitized = sanitize_text(long_text, max_length=100)
        assert len(sanitized) <= 100
    
    def test_extract_emotion_keywords(self):
        """测试情绪关键词提取"""
        text = "我今天很开心，但是有点焦虑"
        keywords = extract_emotion_keywords(text)
        
        assert "开心" in keywords
        assert "焦虑" in keywords
    
    def test_calculate_similarity(self):
        """测试相似度计算"""
        # 相同文本
        similarity = calculate_similarity("hello world", "hello world")
        assert similarity == 1.0
        
        # 不同文本
        similarity = calculate_similarity("hello world", "goodbye world")
        assert 0 < similarity < 1
        
        # 完全不同的文本
        similarity = calculate_similarity("hello", "goodbye")
        assert similarity == 0.0


class TestIntegration:
    """集成测试"""
    
    @pytest.mark.asyncio
    async def test_config_with_mock_env(self):
        """测试配置与模拟环境变量"""
        with patch.dict('os.environ', {
            'ENVIRONMENT': 'testing',
            'DEBUG': 'true',
            'API_PORT': '9000'
        }):
            config = get_config()
            assert config.environment == Environment.TESTING
            assert config.debug is True
            assert config.api.port == 9000
    
    def test_exception_handling_chain(self):
        """测试异常处理链"""
        try:
            raise ValidationError("测试验证错误", field="test")
        except ValidationError as e:
            error_dict = e.to_dict()
            assert error_dict["error_code"] == "ValidationError"
            assert error_dict["field"] == "test"
    
    def test_validator_and_formatter_integration(self):
        """测试验证器和格式化器集成"""
        # 验证输入
        valid, msg = validate_email("test@example.com")
        assert valid is True
        
        # 格式化响应
        response = format_response(
            data={"email_valid": valid},
            message=msg
        )
        
        assert response["success"] is True
        assert response["data"]["email_valid"] is True


if __name__ == "__main__":
    pytest.main([__file__])
