#!/usr/bin/env python3
"""
工厂模式实现
创建和管理各种服务的实例
"""

from typing import Any, Dict, Type, TypeVar, Optional, Callable
from abc import ABC, abstractmethod
import threading
from functools import lru_cache

from .config import get_config
from .interfaces import (
    IChatEngine,
    IMemoryService,
    IContextService,
    IEmotionAnalyzer,
    IRAGService,
    IEvaluationService,
    IFeedbackService,
    IDatabaseService,
    ICacheService,
    ILogger,
    IValidationService
)
from .exceptions import ConfigurationError

T = TypeVar('T')


class ServiceFactory(ABC):
    """服务工厂基类"""
    
    @abstractmethod
    def create_service(self, *args, **kwargs) -> Any:
        """创建服务实例"""
        pass
    
    @abstractmethod
    def get_service_type(self) -> Type:
        """获取服务类型"""
        pass


class ChatEngineFactory(ServiceFactory):
    """聊天引擎工厂"""
    
    def create_service(self, *args, **kwargs) -> IChatEngine:
        """创建聊天引擎实例"""
        try:
            from ..modules.llm.core.llm_core import SimpleEmotionalChatEngine
            return SimpleEmotionalChatEngine(*args, **kwargs)
        except ImportError as e:
            raise ConfigurationError(f"无法导入聊天引擎: {e}")
    
    def get_service_type(self) -> Type[IChatEngine]:
        return IChatEngine


class MemoryServiceFactory(ServiceFactory):
    """记忆服务工厂"""
    
    def create_service(self, *args, **kwargs) -> IMemoryService:
        """创建记忆服务实例"""
        try:
            from ..services.memory_service import MemoryService
            return MemoryService(*args, **kwargs)
        except ImportError as e:
            raise ConfigurationError(f"无法导入记忆服务: {e}")
    
    def get_service_type(self) -> Type[IMemoryService]:
        return IMemoryService


class ContextServiceFactory(ServiceFactory):
    """上下文服务工厂"""
    
    def create_service(self, memory_service: Optional[IMemoryService] = None, *args, **kwargs) -> IContextService:
        """创建上下文服务实例"""
        try:
            from ..services.context_service import ContextService
            return ContextService(memory_service=memory_service, *args, **kwargs)
        except ImportError as e:
            raise ConfigurationError(f"无法导入上下文服务: {e}")
    
    def get_service_type(self) -> Type[IContextService]:
        return IContextService


class EmotionAnalyzerFactory(ServiceFactory):
    """情绪分析器工厂"""
    
    def create_service(self, *args, **kwargs) -> IEmotionAnalyzer:
        """创建情绪分析器实例"""
        try:
            from ..emotion_analyzer import EmotionAnalyzer
            return EmotionAnalyzer(*args, **kwargs)
        except ImportError as e:
            raise ConfigurationError(f"无法导入情绪分析器: {e}")
    
    def get_service_type(self) -> Type[IEmotionAnalyzer]:
        return IEmotionAnalyzer


class RAGServiceFactory(ServiceFactory):
    """RAG服务工厂"""
    
    def create_service(self, *args, **kwargs) -> IRAGService:
        """创建RAG服务实例"""
        try:
            from ..services.rag_service import RAGService
            return RAGService(*args, **kwargs)
        except ImportError as e:
            raise ConfigurationError(f"无法导入RAG服务: {e}")
    
    def get_service_type(self) -> Type[IRAGService]:
        return IRAGService


class DatabaseServiceFactory(ServiceFactory):
    """数据库服务工厂"""
    
    def create_service(self, *args, **kwargs) -> IDatabaseService:
        """创建数据库服务实例"""
        try:
            from ..database import DatabaseManager
            return DatabaseManager(*args, **kwargs)
        except ImportError as e:
            raise ConfigurationError(f"无法导入数据库服务: {e}")
    
    def get_service_type(self) -> Type[IDatabaseService]:
        return IDatabaseService


class CacheServiceFactory(ServiceFactory):
    """缓存服务工厂"""
    
    def create_service(self, *args, **kwargs) -> ICacheService:
        """创建缓存服务实例"""
        try:
            from ..cache_service import CacheService
            return CacheService(*args, **kwargs)
        except ImportError as e:
            # 如果没有Redis缓存，返回内存缓存
            from .utils.memory_cache import MemoryCacheService
            return MemoryCacheService(*args, **kwargs)
    
    def get_service_type(self) -> Type[ICacheService]:
        return ICacheService


class LoggerFactory(ServiceFactory):
    """日志服务工厂"""
    
    def create_service(self, name: str = __name__, *args, **kwargs) -> ILogger:
        """创建日志服务实例"""
        try:
            from ..logging_config import get_logger
            return get_logger(name)
        except ImportError as e:
            raise ConfigurationError(f"无法导入日志服务: {e}")
    
    def get_service_type(self) -> Type[ILogger]:
        return ILogger


class ValidationServiceFactory(ServiceFactory):
    """验证服务工厂"""
    
    def create_service(self, *args, **kwargs) -> IValidationService:
        """创建验证服务实例"""
        try:
            from ..validation_service import ValidationService
            return ValidationService(*args, **kwargs)
        except ImportError as e:
            from .utils.simple_validator import SimpleValidationService
            return SimpleValidationService(*args, **kwargs)
    
    def get_service_type(self) -> Type[IValidationService]:
        return IValidationService


class ServiceRegistry:
    """服务注册表"""
    
    def __init__(self):
        self._factories: Dict[Type, ServiceFactory] = {}
        self._instances: Dict[Type, Any] = {}
        self._singletons: Dict[Type, Any] = {}
        self._lock = threading.Lock()
    
    def register_factory(self, service_type: Type[T], factory: ServiceFactory, singleton: bool = False):
        """注册服务工厂"""
        with self._lock:
            self._factories[service_type] = factory
            if singleton:
                self._singletons[service_type] = None
    
    def get_service(self, service_type: Type[T], *args, **kwargs) -> T:
        """获取服务实例"""
        with self._lock:
            # 检查是否为单例
            if service_type in self._singletons:
                if self._singletons[service_type] is None:
                    factory = self._factories.get(service_type)
                    if not factory:
                        raise ConfigurationError(f"未注册的服务类型: {service_type}")
                    self._singletons[service_type] = factory.create_service(*args, **kwargs)
                return self._singletons[service_type]
            
            # 非单例，创建新实例
            factory = self._factories.get(service_type)
            if not factory:
                raise ConfigurationError(f"未注册的服务类型: {service_type}")
            
            return factory.create_service(*args, **kwargs)
    
    def register_instance(self, service_type: Type[T], instance: T):
        """注册服务实例"""
        with self._lock:
            self._instances[service_type] = instance
    
    def get_instance(self, service_type: Type[T]) -> Optional[T]:
        """获取已注册的实例"""
        return self._instances.get(service_type)
    
    def is_registered(self, service_type: Type[T]) -> bool:
        """检查服务是否已注册"""
        return service_type in self._factories or service_type in self._instances
    
    def clear_singleton(self, service_type: Type[T]):
        """清除单例实例"""
        with self._lock:
            if service_type in self._singletons:
                self._singletons[service_type] = None
    
    def clear_all(self):
        """清除所有注册的服务"""
        with self._lock:
            self._factories.clear()
            self._instances.clear()
            self._singletons.clear()


class ApplicationContext:
    """应用程序上下文"""
    
    def __init__(self):
        self._registry = ServiceRegistry()
        self._config = get_config()
        self._initialized = False
        self._lock = threading.Lock()
    
    def initialize(self):
        """初始化应用程序上下文"""
        with self._lock:
            if self._initialized:
                return
            
            # 注册默认服务工厂
            self._register_default_factories()
            
            # 预加载单例服务
            self._preload_singletons()
            
            self._initialized = True
    
    def _register_default_factories(self):
        """注册默认服务工厂"""
        # 注册各种服务工厂
        self._registry.register_factory(ILogger, LoggerFactory(), singleton=True)
        self._registry.register_factory(ICacheService, CacheServiceFactory(), singleton=True)
        self._registry.register_factory(IDatabaseService, DatabaseServiceFactory(), singleton=True)
        self._registry.register_factory(IValidationService, ValidationServiceFactory(), singleton=True)
        
        self._registry.register_factory(IEmotionAnalyzer, EmotionAnalyzerFactory())
        self._registry.register_factory(IMemoryService, MemoryServiceFactory())
        self._registry.register_factory(IContextService, ContextServiceFactory())
        self._registry.register_factory(IChatEngine, ChatEngineFactory())
        self._registry.register_factory(IRAGService, RAGServiceFactory())
    
    def _preload_singletons(self):
        """预加载单例服务"""
        try:
            # 预加载关键的单例服务
            self._registry.get_service(ILogger)
            self._registry.get_service(ICacheService)
            self._registry.get_service(IDatabaseService)
        except Exception as e:
            # 记录错误但不阻止初始化
            print(f"预加载服务时出错: {e}")
    
    def get_service(self, service_type: Type[T], *args, **kwargs) -> T:
        """获取服务实例"""
        if not self._initialized:
            self.initialize()
        return self._registry.get_service(service_type, *args, **kwargs)
    
    def register_service(self, service_type: Type[T], factory: ServiceFactory, singleton: bool = False):
        """注册服务"""
        self._registry.register_factory(service_type, factory, singleton)
    
    def register_instance(self, service_type: Type[T], instance: T):
        """注册服务实例"""
        self._registry.register_instance(service_type, instance)
    
    def get_config(self):
        """获取配置"""
        return self._config
    
    def shutdown(self):
        """关闭应用程序上下文"""
        with self._lock:
            # 清理资源
            self._registry.clear_all()
            self._initialized = False


# 全局应用程序上下文
_app_context: Optional[ApplicationContext] = None


def get_app_context() -> ApplicationContext:
    """获取全局应用程序上下文"""
    global _app_context
    if _app_context is None:
        _app_context = ApplicationContext()
        _app_context.initialize()
    return _app_context


@lru_cache()
def get_service(service_type: Type[T]) -> T:
    """获取服务实例（缓存版本）"""
    return get_app_context().get_service(service_type)


def shutdown_app_context():
    """关闭应用程序上下文"""
    global _app_context
    if _app_context:
        _app_context.shutdown()
        _app_context = None


# 便捷函数
def get_chat_engine() -> IChatEngine:
    """获取聊天引擎"""
    return get_service(IChatEngine)


def get_memory_service() -> IMemoryService:
    """获取记忆服务"""
    return get_service(IMemoryService)


def get_context_service() -> IContextService:
    """获取上下文服务"""
    return get_service(IContextService)


def get_emotion_analyzer() -> IEmotionAnalyzer:
    """获取情绪分析器"""
    return get_service(IEmotionAnalyzer)


def get_rag_service() -> IRAGService:
    """获取RAG服务"""
    return get_service(IRAGService)


def get_database_service() -> IDatabaseService:
    """获取数据库服务"""
    return get_service(IDatabaseService)


def get_cache_service() -> ICacheService:
    """获取缓存服务"""
    return get_service(ICacheService)


def get_logger(name: str = __name__) -> ILogger:
    """获取日志服务"""
    return get_service(ILogger)


def get_validation_service() -> IValidationService:
    """获取验证服务"""
    return get_service(IValidationService)


# 使用示例
if __name__ == "__main__":
    # 初始化应用上下文
    context = get_app_context()
    
    # 获取服务
    logger = get_logger("test")
    cache = get_cache_service()
    db = get_database_service()
    
    print(f"Logger: {logger}")
    print(f"Cache: {cache}")
    print(f"Database: {db}")
    
    # 关闭上下文
    shutdown_app_context()
