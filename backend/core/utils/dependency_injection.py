#!/usr/bin/env python3
"""
依赖注入容器
实现依赖注入模式，管理服务生命周期
"""

from typing import Any, Callable, Dict, Type, TypeVar, Optional, Union
from functools import wraps
import inspect
from threading import Lock

T = TypeVar('T')


class Dependency:
    """依赖项定义"""
    
    def __init__(
        self,
        factory: Callable[..., Any],
        lifetime: str = "transient",
        dependencies: Optional[Dict[str, Any]] = None
    ):
        self.factory = factory
        self.lifetime = lifetime
        self.dependencies = dependencies or {}
        self._instance: Optional[Any] = None
        self._lock = Lock()
    
    def get_instance(self, container: 'Container') -> Any:
        """获取实例"""
        if self.lifetime == "singleton":
            with self._lock:
                if self._instance is None:
                    self._instance = self._create_instance(container)
                return self._instance
        else:  # transient
            return self._create_instance(container)
    
    def _create_instance(self, container: 'Container') -> Any:
        """创建实例"""
        # 解析依赖
        resolved_deps = {}
        for name, dep_type in self.dependencies.items():
            resolved_deps[name] = container.get(dep_type)
        
        # 创建实例
        if inspect.isfunction(self.factory):
            # 如果是函数，直接调用
            return self.factory(**resolved_deps)
        else:
            # 如果是类，实例化
            return self.factory(**resolved_deps)


class Container:
    """依赖注入容器"""
    
    def __init__(self):
        self._services: Dict[Type, Dependency] = {}
        self._instances: Dict[Type, Any] = {}
        self._lock = Lock()
    
    def register_singleton(
        self,
        service_type: Type[T],
        factory: Union[Type[T], Callable[..., T]],
        dependencies: Optional[Dict[str, Type]] = None
    ) -> 'Container':
        """注册单例服务"""
        return self._register(service_type, factory, "singleton", dependencies)
    
    def register_transient(
        self,
        service_type: Type[T],
        factory: Union[Type[T], Callable[..., T]],
        dependencies: Optional[Dict[str, Type]] = None
    ) -> 'Container':
        """注册瞬时服务"""
        return self._register(service_type, factory, "transient", dependencies)
    
    def _register(
        self,
        service_type: Type[T],
        factory: Union[Type[T], Callable[..., T]],
        lifetime: str,
        dependencies: Optional[Dict[str, Type]] = None
    ) -> 'Container':
        """注册服务"""
        with self._lock:
            self._services[service_type] = Dependency(
                factory=factory,
                lifetime=lifetime,
                dependencies=dependencies or {}
            )
        return self
    
    def get(self, service_type: Type[T]) -> T:
        """获取服务实例"""
        with self._lock:
            if service_type not in self._services:
                raise ValueError(f"Service {service_type} is not registered")
            
            dependency = self._services[service_type]
            return dependency.get_instance(self)
    
    def get_optional(self, service_type: Type[T]) -> Optional[T]:
        """获取可选服务实例"""
        try:
            return self.get(service_type)
        except ValueError:
            return None
    
    def is_registered(self, service_type: Type[T]) -> bool:
        """检查服务是否已注册"""
        return service_type in self._services
    
    def unregister(self, service_type: Type[T]) -> bool:
        """取消注册服务"""
        with self._lock:
            return self._services.pop(service_type, None) is not None
    
    def clear(self):
        """清空容器"""
        with self._lock:
            self._services.clear()
            self._instances.clear()
    
    def get_all_registered(self) -> Dict[Type, str]:
        """获取所有已注册的服务"""
        return {
            service_type: dependency.lifetime
            for service_type, dependency in self._services.items()
        }


# 全局容器实例
_container = Container()


def get_container() -> Container:
    """获取全局容器实例"""
    return _container


# 装饰器
def Singleton(cls: Type[T]) -> Type[T]:
    """单例装饰器"""
    original_new = cls.__new__
    instance = None
    lock = Lock()
    
    @wraps(cls.__new__)
    def __new__(cls, *args, **kwargs):
        nonlocal instance
        if instance is None:
            with lock:
                if instance is None:
                    instance = original_new(cls)
        return instance
    
    cls.__new__ = __new__
    return cls


def Transient(cls: Type[T]) -> Type[T]:
    """瞬时装饰器（默认行为）"""
    return cls


# 注入装饰器
def inject(*dependencies: Type):
    """依赖注入装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 解析依赖
            resolved_deps = []
            for dep_type in dependencies:
                resolved_deps.append(_container.get(dep_type))
            
            # 调用原函数
            return func(*resolved_deps, *args, **kwargs)
        
        return wrapper
    return decorator


# 自动注册装饰器
def auto_register(lifetime: str = "transient"):
    """自动注册装饰器"""
    def decorator(cls: Type[T]) -> Type[T]:
        # 自动分析依赖
        signature = inspect.signature(cls.__init__)
        dependencies = {}
        
        for name, param in signature.parameters.items():
            if name == 'self':
                continue
            if param.annotation != inspect.Parameter.empty:
                dependencies[name] = param.annotation
        
        # 注册到容器
        _container._register(cls, cls, lifetime, dependencies)
        return cls
    
    return decorator


# 使用示例和测试
class ExampleService:
    """示例服务"""
    def __init__(self, config):
        self.config = config
    
    def get_value(self):
        return self.config.get("value", "default")


class ExampleConfig:
    """示例配置"""
    def get(self, key, default=None):
        return {"value": "test_value"}.get(key, default)


def setup_example_container():
    """设置示例容器"""
    container = get_container()
    
    # 注册配置为单例
    container.register_singleton(ExampleConfig, ExampleConfig)
    
    # 注册服务，依赖配置
    container.register_transient(
        ExampleService,
        ExampleService,
        {"config": ExampleConfig}
    )
    
    return container


if __name__ == "__main__":
    # 测试依赖注入
    container = setup_example_container()
    
    # 获取服务实例
    service = container.get(ExampleService)
    print(f"Service value: {service.get_value()}")
    
    # 验证单例
    config1 = container.get(ExampleConfig)
    config2 = container.get(ExampleConfig)
    print(f"Config instances are same: {config1 is config2}")
    
    # 验证瞬时
    service1 = container.get(ExampleService)
    service2 = container.get(ExampleService)
    print(f"Service instances are same: {service1 is service2}")
