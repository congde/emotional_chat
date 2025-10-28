"""
插件管理器 - 统一管理所有插件的注册、调用、权限控制
"""
from typing import Dict, Any, List, Optional
import logging
from .base_plugin import BasePlugin

logger = logging.getLogger(__name__)


class PluginManager:
    """插件管理器"""
    
    def __init__(self):
        self.plugins: Dict[str, BasePlugin] = {}
        self.call_history: List[Dict[str, Any]] = []
        self.max_history = 100
    
    def register(self, plugin: BasePlugin):
        """注册插件"""
        if not isinstance(plugin, BasePlugin):
            raise ValueError("插件必须是 BasePlugin 的实例")
        
        self.plugins[plugin.name] = plugin
        logger.info(f"注册插件: {plugin.name} - {plugin.description}")
    
    def register_many(self, plugins: List[BasePlugin]):
        """批量注册插件"""
        for plugin in plugins:
            self.register(plugin)
    
    def unregister(self, plugin_name: str):
        """注销插件"""
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]
            logger.info(f"注销插件: {plugin_name}")
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """获取插件"""
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> List[str]:
        """列出所有已注册的插件名称"""
        return list(self.plugins.keys())
    
    def get_function_schemas(self) -> List[Dict[str, Any]]:
        """获取所有插件的 Function Calling Schemas"""
        return [plugin.function_schema for plugin in self.plugins.values() if plugin.enabled]
    
    def execute_plugin(self, plugin_name: str, **kwargs) -> Dict[str, Any]:
        """执行插件"""
        plugin = self.get_plugin(plugin_name)
        
        if not plugin:
            return {"error": f"插件 '{plugin_name}' 未找到"}
        
        if not plugin.enabled:
            return {"error": f"插件 '{plugin_name}' 已禁用"}
        
        try:
            # 记录调用历史
            call_record = {
                "plugin": plugin_name,
                "params": kwargs,
                "timestamp": None  # 可以添加时间戳
            }
            self.call_history.append(call_record)
            
            # 限制历史记录长度
            if len(self.call_history) > self.max_history:
                self.call_history = self.call_history[-self.max_history:]
            
            # 执行插件
            result = plugin.execute(**kwargs)
            
            call_record["result"] = "success" if "error" not in result else "failed"
            
            logger.info(f"插件调用: {plugin_name} - 成功")
            return result
        
        except Exception as e:
            logger.error(f"插件调用失败: {plugin_name} - {e}")
            return {"error": str(e)}
    
    def can_call_plugin(self, plugin_name: str) -> bool:
        """检查是否可以调用插件"""
        plugin = self.get_plugin(plugin_name)
        return plugin is not None and plugin.enabled
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """获取插件使用统计"""
        return {
            "total_plugins": len(self.plugins),
            "enabled_plugins": sum(1 for p in self.plugins.values() if p.enabled),
            "total_calls": len(self.call_history),
            "plugins": [
                {
                    "name": name,
                    "enabled": plugin.enabled,
                    "description": plugin.description
                }
                for name, plugin in self.plugins.items()
            ]
        }
    
    def get_call_history(self, plugin_name: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """获取调用历史"""
        history = self.call_history
        
        if plugin_name:
            history = [h for h in history if h.get("plugin") == plugin_name]
        
        return history[-limit:]
