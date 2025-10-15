#!/usr/bin/env python3
"""
依赖注入
提供全局的服务实例和依赖管理
"""

from functools import lru_cache
from backend.services.chat_service import ChatService
from backend.services.memory_service import MemoryService
from backend.services.context_service import ContextService
from backend.evaluation_engine import EvaluationEngine
from backend.database import DatabaseManager


class ServiceContainer:
    """服务容器 - 管理所有服务实例"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # 初始化服务
        self._memory_service = None
        self._context_service = None
        self._chat_service = None
        self._evaluation_engine = None
        
        self._initialized = True
    
    @property
    def memory_service(self) -> MemoryService:
        """获取记忆服务实例"""
        if self._memory_service is None:
            self._memory_service = MemoryService()
        return self._memory_service
    
    @property
    def context_service(self) -> ContextService:
        """获取上下文服务实例"""
        if self._context_service is None:
            self._context_service = ContextService(memory_service=self.memory_service)
        return self._context_service
    
    @property
    def chat_service(self) -> ChatService:
        """获取聊天服务实例"""
        if self._chat_service is None:
            self._chat_service = ChatService(
                memory_service=self.memory_service,
                context_service=self.context_service
            )
        return self._chat_service
    
    @property
    def evaluation_engine(self) -> EvaluationEngine:
        """获取评估引擎实例"""
        if self._evaluation_engine is None:
            self._evaluation_engine = EvaluationEngine()
        return self._evaluation_engine


# 全局服务容器实例
_service_container = ServiceContainer()


# 依赖注入函数
def get_memory_service() -> MemoryService:
    """获取记忆服务"""
    return _service_container.memory_service


def get_context_service() -> ContextService:
    """获取上下文服务"""
    return _service_container.context_service


def get_chat_service() -> ChatService:
    """获取聊天服务"""
    return _service_container.chat_service


def get_evaluation_engine() -> EvaluationEngine:
    """获取评估引擎"""
    return _service_container.evaluation_engine


def get_db():
    """获取数据库会话（FastAPI依赖）"""
    db = DatabaseManager()
    try:
        yield db
    finally:
        db.db.close()

