#!/usr/bin/env python3
"""
基础集成测试
"""

import pytest
from unittest.mock import Mock, patch


class TestBasicIntegration:
    """基础集成测试"""
    
    def test_imports(self):
        """测试模块导入"""
        # 测试核心模块可以正常导入
        from backend.core.config import Config, get_config
        from backend.core.exceptions import EmotionalChatException
        
        assert Config is not None
        assert get_config is not None
        assert EmotionalChatException is not None
    
    @pytest.mark.asyncio
    async def test_config_loading(self):
        """测试配置加载"""
        from backend.core.config import get_config
        
        # 测试配置可以正常加载
        config = get_config()
        assert config is not None
        assert hasattr(config, 'environment')
        assert hasattr(config, 'database')
    
    def test_exception_handling(self):
        """测试异常处理"""
        from backend.core.exceptions import (
            EmotionalChatException,
            ValidationError,
            DatabaseError
        )
        
        # 测试异常可以正常创建
        exc = EmotionalChatException("测试错误")
        assert str(exc) == "测试错误"
        
        val_exc = ValidationError("验证失败", field="test")
        assert val_exc.field == "test"
        
        db_exc = DatabaseError("数据库错误")
        assert isinstance(db_exc, EmotionalChatException)

