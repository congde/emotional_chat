"""
插件基类 - 定义所有插件必须实现的接口
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BasePlugin(ABC):
    """插件基类"""
    
    def __init__(self, name: str, description: str, api_key: Optional[str] = None):
        self.name = name
        self.description = description
        self.api_key = api_key
        self.enabled = True
        
    @property
    def function_schema(self) -> Dict[str, Any]:
        """
        返回该插件对应的 Function Calling Schema
        必须由子类实现
        """
        raise NotImplementedError
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行插件功能
        
        Args:
            **kwargs: 插件参数
            
        Returns:
            执行结果字典
        """
        pass
    
    def validate_params(self, **kwargs) -> bool:
        """
        验证参数是否有效
        
        Args:
            **kwargs: 待验证的参数
            
        Returns:
            是否有效
        """
        return True
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        获取插件使用统计
        
        Returns:
            统计信息字典
        """
        return {
            "name": self.name,
            "enabled": self.enabled,
            "total_calls": 0
        }
    
    def __repr__(self):
        return f"<{self.__class__.__name__} name='{self.name}'>"
