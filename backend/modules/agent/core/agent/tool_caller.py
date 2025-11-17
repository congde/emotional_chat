"""
Tool Caller - 工具调用模块

负责：
- 工具注册与管理
- 工具调用执行
- 参数验证
- 结果解析

支持MCP协议：接收MCP工具请求，返回标准化的MCP工具响应
"""

import json
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import inspect

# 导入MCP协议
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, project_root)

from backend.modules.agent.protocol.mcp import (
    MCPMessage, MCPProtocol, MCPToolCall, MCPToolResponse, MCPContext,
    MCPMessageType, get_mcp_logger
)


class Tool:
    """工具定义"""
    
    def __init__(
        self,
        name: str,
        description: str,
        function: Callable,
        parameters: Dict[str, Any],
        category: str = "general"
    ):
        self.name = name
        self.description = description
        self.function = function
        self.parameters = parameters
        self.category = category
        self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "category": self.category
        }


class ToolRegistry:
    """工具注册表"""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
    
    def register(
        self,
        name: str,
        description: str,
        function: Callable,
        parameters: Dict[str, Any],
        category: str = "general"
    ):
        """注册工具"""
        tool = Tool(name, description, function, parameters, category)
        self.tools[name] = tool
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """获取工具"""
        return self.tools.get(name)
    
    def list_tools(self, category: Optional[str] = None) -> List[Tool]:
        """列出所有工具"""
        if category:
            return [t for t in self.tools.values() if t.category == category]
        return list(self.tools.values())
    
    def get_available_tools(self) -> List[str]:
        """获取可用工具名称列表"""
        return list(self.tools.keys())


class ToolCaller:
    """工具调用模块 - Agent的工具接口"""
    
    def __init__(self):
        self.registry = ToolRegistry()
        self._register_builtin_tools()
        
        # 调用历史
        self.call_history: List[Dict[str, Any]] = []
        
        # MCP协议支持
        self.mcp_protocol = MCPProtocol()
        self.mcp_logger = get_mcp_logger()
    
    def _register_builtin_tools(self):
        """注册内置工具"""
        
        # ========== 记忆相关工具 ==========
        
        self.registry.register(
            name="search_memory",
            description="搜索用户历史记忆和对话",
            function=self._search_memory,
            parameters={
                "query": {"type": "string", "required": True, "description": "搜索关键词"},
                "user_id": {"type": "string", "required": True, "description": "用户ID"},
                "time_range": {"type": "int", "required": False, "default": 30, "description": "时间范围（天）"},
                "emotion_filter": {"type": "string", "required": False, "description": "情绪过滤"}
            },
            category="memory"
        )
        
        self.registry.register(
            name="get_emotion_log",
            description="获取用户情绪变化记录",
            function=self._get_emotion_log,
            parameters={
                "user_id": {"type": "string", "required": True, "description": "用户ID"},
                "days": {"type": "int", "required": False, "default": 7, "description": "查询天数"},
                "emotion_type": {"type": "string", "required": False, "description": "情绪类型"}
            },
            category="memory"
        )
        
        # ========== 定时任务工具 ==========
        
        self.registry.register(
            name="set_reminder",
            description="设置定时提醒任务",
            function=self._set_reminder,
            parameters={
                "content": {"type": "string", "required": True, "description": "提醒内容"},
                "user_id": {"type": "string", "required": True, "description": "用户ID"},
                "schedule_time": {"type": "string", "required": True, "description": "提醒时间（ISO格式）"},
                "repeat": {"type": "bool", "required": False, "default": False, "description": "是否重复"}
            },
            category="scheduler"
        )
        
        # ========== 资源推荐工具 ==========
        
        self.registry.register(
            name="recommend_meditation",
            description="推荐冥想音频资源",
            function=self._recommend_meditation,
            parameters={
                "theme": {"type": "string", "required": False, "default": "relaxation", "description": "主题（sleep/anxiety/relaxation）"},
                "duration": {"type": "int", "required": False, "default": 10, "description": "时长（分钟）"},
                "user_id": {"type": "string", "required": False, "description": "用户ID"}
            },
            category="resource"
        )
        
        self.registry.register(
            name="recommend_resource",
            description="推荐心理健康资源",
            function=self._recommend_resource,
            parameters={
                "resource_type": {"type": "string", "required": False, "default": "article", "description": "资源类型（article/video/book）"},
                "theme": {"type": "string", "required": True, "description": "主题"},
                "user_id": {"type": "string", "required": False, "description": "用户ID"}
            },
            category="resource"
        )
        
        # ========== 评估工具 ==========
        
        self.registry.register(
            name="psychological_assessment",
            description="触发心理健康评估",
            function=self._psychological_assessment,
            parameters={
                "assessment_type": {"type": "string", "required": True, "description": "评估类型（depression/anxiety/stress）"},
                "user_id": {"type": "string", "required": True, "description": "用户ID"},
                "urgency": {"type": "string", "required": False, "default": "medium", "description": "紧急程度"}
            },
            category="assessment"
        )
        
        # ========== 日历工具 ==========
        
        self.registry.register(
            name="check_calendar",
            description="查看用户日历事件",
            function=self._check_calendar,
            parameters={
                "user_id": {"type": "string", "required": True, "description": "用户ID"},
                "start_date": {"type": "string", "required": False, "description": "开始日期"},
                "end_date": {"type": "string", "required": False, "description": "结束日期"}
            },
            category="calendar"
        )
    
    async def call(
        self, 
        tool_name: str, 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        调用工具
        
        Args:
            tool_name: 工具名称
            parameters: 调用参数
            
        Returns:
            工具执行结果
        """
        call_record = {
            "tool": tool_name,
            "parameters": parameters,
            "timestamp": datetime.now(),
            "success": False
        }
        
        try:
            # 获取工具
            tool = self.registry.get_tool(tool_name)
            
            if not tool:
                raise ValueError(f"工具不存在: {tool_name}")
            
            # 验证参数
            self._validate_parameters(tool, parameters)
            
            # 执行调用
            if inspect.iscoroutinefunction(tool.function):
                result = await tool.function(**parameters)
            else:
                result = tool.function(**parameters)
            
            call_record["success"] = True
            call_record["result"] = result
            
            # 记录调用历史
            self.call_history.append(call_record)
            
            return {
                "success": True,
                "tool": tool_name,
                "result": result,
                "timestamp": call_record["timestamp"].isoformat()
            }
            
        except Exception as e:
            call_record["error"] = str(e)
            self.call_history.append(call_record)
            
            return {
                "success": False,
                "tool": tool_name,
                "error": str(e),
                "timestamp": call_record["timestamp"].isoformat()
            }
    
    async def call_with_mcp(
        self,
        mcp_message: MCPMessage
    ) -> MCPMessage:
        """
        使用MCP协议执行工具调用（新接口）
        
        Args:
            mcp_message: 输入的MCP消息（包含tool_calls）
            
        Returns:
            输出的MCP消息（包含tool_responses）
        """
        import time
        
        tool_responses = []
        
        # 执行所有工具调用
        for tool_call in mcp_message.tool_calls:
            start_time = time.time()
            
            try:
                # 调用工具
                result = await self.call(tool_call.tool_name, tool_call.parameters)
                execution_time = time.time() - start_time
                
                # 创建工具响应
                tool_response = MCPToolResponse(
                    tool_id=tool_call.tool_id,
                    tool_name=tool_call.tool_name,
                    success=result.get("success", False),
                    result=result.get("result"),
                    error=result.get("error"),
                    execution_time=execution_time
                )
                tool_responses.append(tool_response)
                
            except Exception as e:
                execution_time = time.time() - start_time
                tool_response = MCPToolResponse(
                    tool_id=tool_call.tool_id,
                    tool_name=tool_call.tool_name,
                    success=False,
                    error=str(e),
                    execution_time=execution_time
                )
                tool_responses.append(tool_response)
        
        # 创建MCP响应消息
        output_message = self.mcp_protocol.create_tool_response(
            tool_responses=tool_responses,
            context=mcp_message.context
        )
        
        # 设置元数据
        output_message.metadata = {
            **(output_message.metadata or {}),
            "interaction_id": mcp_message.metadata.get("interaction_id") if mcp_message.metadata else None,
            "source_message_id": mcp_message.message_id
        }
        
        # 记录日志
        self.mcp_logger.log(output_message)
        
        return output_message
    
    def _validate_parameters(self, tool: Tool, parameters: Dict[str, Any]):
        """
        验证工具参数
        
        检查必需参数是否存在，类型是否正确
        """
        for param_name, param_spec in tool.parameters.items():
            # 检查必需参数
            if param_spec.get("required", False):
                if param_name not in parameters:
                    raise ValueError(f"缺少必需参数: {param_name}")
            
            # 如果参数存在，检查类型
            if param_name in parameters:
                expected_type = param_spec.get("type")
                actual_value = parameters[param_name]
                
                # 简单类型检查
                type_map = {
                    "string": str,
                    "int": int,
                    "float": float,
                    "bool": bool,
                    "list": list,
                    "dict": dict
                }
                
                if expected_type in type_map:
                    expected_python_type = type_map[expected_type]
                    if not isinstance(actual_value, expected_python_type):
                        raise TypeError(
                            f"参数 {param_name} 类型错误: "
                            f"期望 {expected_type}, 实际 {type(actual_value).__name__}"
                        )
    
    def get_call_history(
        self, 
        limit: int = 10, 
        tool_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        获取调用历史
        
        Args:
            limit: 返回数量限制
            tool_name: 过滤特定工具（可选）
            
        Returns:
            调用历史列表
        """
        history = self.call_history
        
        if tool_name:
            history = [h for h in history if h["tool"] == tool_name]
        
        return history[-limit:]
    
    # ==================== 工具实现 ====================
    
    async def _search_memory(
        self,
        query: str,
        user_id: str,
        time_range: int = 30,
        emotion_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """搜索记忆工具实现"""
        try:
            from .memory_hub import get_memory_hub
            
            memory_hub = get_memory_hub()
            
            context = {"time_range": time_range}
            if emotion_filter:
                context["emotion"] = emotion_filter
            
            results = memory_hub.retrieve(
                query=query,
                user_id=user_id,
                context=context,
                top_k=5
            )
            
            return {
                "count": len(results),
                "memories": [
                    {
                        "content": m.get("content", ""),
                        "emotion": m.get("emotion", {}),
                        "timestamp": m.get("timestamp", "").isoformat() if hasattr(m.get("timestamp", ""), "isoformat") else str(m.get("timestamp", "")),
                        "importance": m.get("importance", 0)
                    }
                    for m in results
                ]
            }
        
        except Exception as e:
            return {
                "count": 0,
                "memories": [],
                "error": str(e)
            }
    
    async def _get_emotion_log(
        self,
        user_id: str,
        days: int = 7,
        emotion_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取情绪日志工具实现"""
        try:
            from .memory_hub import get_memory_hub
            
            memory_hub = get_memory_hub()
            action_log = memory_hub.get_action_log(user_id, days)
            
            # 过滤情绪相关的日志
            emotion_logs = []
            for log in action_log:
                if log.get("emotion"):
                    if not emotion_type or log["emotion"] == emotion_type:
                        emotion_logs.append(log)
            
            # 分析趋势
            emotions = {}
            for log in emotion_logs:
                emotion = log["emotion"]
                emotions[emotion] = emotions.get(emotion, 0) + 1
            
            dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0] if emotions else "平静"
            
            return {
                "logs": emotion_logs,
                "summary": {
                    "dominant_emotion": dominant_emotion,
                    "emotion_distribution": emotions,
                    "total_count": len(emotion_logs)
                }
            }
        
        except Exception as e:
            return {
                "logs": [],
                "summary": {},
                "error": str(e)
            }
    
    async def _set_reminder(
        self,
        content: str,
        user_id: str,
        schedule_time: str,
        repeat: bool = False
    ) -> Dict[str, Any]:
        """设置提醒工具实现"""
        try:
            # 这里应该集成实际的定时任务系统（APScheduler等）
            # 简化实现：只是返回提醒信息
            
            return {
                "reminder_id": f"reminder_{datetime.now().timestamp()}",
                "user_id": user_id,
                "content": content,
                "scheduled_at": schedule_time,
                "repeat": repeat,
                "status": "scheduled",
                "message": f"已设置提醒：{content}"
            }
        
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def _recommend_meditation(
        self,
        theme: str = "relaxation",
        duration: int = 10,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """推荐冥想音频工具实现"""
        # 冥想资源数据库（实际应该从数据库或API获取）
        meditation_db = {
            "sleep": [
                {
                    "title": "深度睡眠引导冥想",
                    "duration": 15,
                    "url": "https://example.com/meditation/sleep1.mp3",
                    "description": "通过渐进式放松帮助你快速入睡"
                },
                {
                    "title": "助眠白噪音",
                    "duration": 30,
                    "url": "https://example.com/meditation/sleep2.mp3",
                    "description": "舒缓的自然声音帮助改善睡眠质量"
                }
            ],
            "anxiety": [
                {
                    "title": "焦虑缓解冥想",
                    "duration": 10,
                    "url": "https://example.com/meditation/anxiety1.mp3",
                    "description": "通过正念练习缓解焦虑情绪"
                },
                {
                    "title": "4-7-8呼吸练习",
                    "duration": 5,
                    "url": "https://example.com/meditation/anxiety2.mp3",
                    "description": "快速减压的呼吸技巧"
                }
            ],
            "relaxation": [
                {
                    "title": "全身放松扫描",
                    "duration": 12,
                    "url": "https://example.com/meditation/relax1.mp3",
                    "description": "系统性地放松身体各个部位"
                },
                {
                    "title": "正念冥想",
                    "duration": 10,
                    "url": "https://example.com/meditation/relax2.mp3",
                    "description": "培养正念觉察，减轻压力"
                }
            ]
        }
        
        recommendations = meditation_db.get(theme, meditation_db["relaxation"])
        
        # 根据时长过滤
        filtered = [r for r in recommendations if r["duration"] <= duration + 5]
        
        if not filtered:
            filtered = recommendations  # 如果没有符合的，返回所有
        
        return {
            "theme": theme,
            "count": len(filtered),
            "recommendations": filtered,
            "message": f"为你推荐了 {len(filtered)} 个{theme}相关的冥想练习"
        }
    
    async def _recommend_resource(
        self,
        theme: str,
        resource_type: str = "article",
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """推荐心理健康资源"""
        # 资源数据库（简化实现）
        resources = {
            "anxiety": {
                "article": [
                    {"title": "如何应对焦虑情绪", "url": "https://example.com/article/anxiety1"},
                    {"title": "焦虑症的自我调节方法", "url": "https://example.com/article/anxiety2"}
                ],
                "video": [
                    {"title": "焦虑管理技巧", "url": "https://example.com/video/anxiety1"}
                ]
            },
            "depression": {
                "article": [
                    {"title": "走出抑郁的第一步", "url": "https://example.com/article/depression1"}
                ]
            }
        }
        
        theme_resources = resources.get(theme, {})
        type_resources = theme_resources.get(resource_type, [])
        
        return {
            "theme": theme,
            "resource_type": resource_type,
            "count": len(type_resources),
            "resources": type_resources
        }
    
    async def _psychological_assessment(
        self,
        assessment_type: str,
        user_id: str,
        urgency: str = "medium"
    ) -> Dict[str, Any]:
        """心理健康评估工具"""
        # 这里应该返回评估问卷或触发评估流程
        assessments = {
            "depression": {
                "name": "PHQ-9抑郁量表",
                "questions_count": 9,
                "estimated_time": "3分钟"
            },
            "anxiety": {
                "name": "GAD-7焦虑量表",
                "questions_count": 7,
                "estimated_time": "2分钟"
            },
            "stress": {
                "name": "压力感知量表",
                "questions_count": 10,
                "estimated_time": "5分钟"
            }
        }
        
        assessment = assessments.get(assessment_type)
        
        if not assessment:
            return {
                "status": "error",
                "message": f"未知的评估类型: {assessment_type}"
            }
        
        return {
            "status": "ready",
            "assessment_type": assessment_type,
            "assessment_name": assessment["name"],
            "questions_count": assessment["questions_count"],
            "estimated_time": assessment["estimated_time"],
            "urgency": urgency,
            "message": f"已准备{assessment['name']}，共{assessment['questions_count']}题，预计{assessment['estimated_time']}"
        }
    
    async def _check_calendar(
        self,
        user_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """查看日历事件"""
        # 简化实现：返回模拟数据
        # 实际应该对接用户日历API
        
        return {
            "user_id": user_id,
            "events": [
                {
                    "title": "重要会议",
                    "date": "2025-10-16",
                    "time": "14:00",
                    "type": "work"
                },
                {
                    "title": "健身",
                    "date": "2025-10-17",
                    "time": "18:00",
                    "type": "personal"
                }
            ],
            "count": 2,
            "message": "查询到2个即将到来的事件"
        }


# 单例模式
_tool_caller_instance = None

def get_tool_caller() -> ToolCaller:
    """获取全局ToolCaller实例"""
    global _tool_caller_instance
    if _tool_caller_instance is None:
        _tool_caller_instance = ToolCaller()
    return _tool_caller_instance


# 使用示例
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # 创建工具调用器
        tool_caller = ToolCaller()
        
        # 列出所有工具
        print("可用工具：")
        for tool in tool_caller.registry.list_tools():
            print(f"  - {tool.name}: {tool.description}")
        
        print("\n" + "="*50 + "\n")
        
        # 调用工具示例1：搜索记忆
        print("1. 搜索记忆：")
        result = await tool_caller.call(
            "search_memory",
            {
                "query": "睡眠",
                "user_id": "user_123",
                "time_range": 7
            }
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        print("\n" + "="*50 + "\n")
        
        # 调用工具示例2：推荐冥想
        print("2. 推荐冥想：")
        result = await tool_caller.call(
            "recommend_meditation",
            {
                "theme": "sleep",
                "duration": 15
            }
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        print("\n" + "="*50 + "\n")
        
        # 调用工具示例3：设置提醒
        print("3. 设置提醒：")
        result = await tool_caller.call(
            "set_reminder",
            {
                "content": "记得做睡前冥想",
                "user_id": "user_123",
                "schedule_time": "2025-10-15T21:30:00",
                "repeat": True
            }
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    asyncio.run(main())

