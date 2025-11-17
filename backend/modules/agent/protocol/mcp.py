"""
MCP (Model Context Protocol) - 模型上下文协议

专为大模型智能体设计的结构化通信协议，实现模块间标准化通信。

MCP协议结构：
{
    "content": str,              # 自然语言内容（用户输入或AI回复）
    "context": {                 # 结构化上下文
        "user_profile": {},      # 用户画像
        "emotion_state": {},     # 情感状态
        "task_goal": {},         # 任务目标
        "memory_summary": {},    # 记忆摘要
        "conversation_history": [] # 对话历史
    },
    "tool_calls": [],            # 工具调用指令
    "tool_responses": []         # 工具执行结果
}
"""

import json
import uuid
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator


class MCPMessageType(str, Enum):
    """MCP消息类型"""
    USER_INPUT = "user_input"           # 用户输入
    AGENT_RESPONSE = "agent_response"   # Agent回复
    PLANNER_OUTPUT = "planner_output"   # Planner输出
    TOOL_REQUEST = "tool_request"       # 工具请求
    TOOL_RESPONSE = "tool_response"     # 工具响应
    REFLECTOR_EVALUATION = "reflector_evaluation"  # Reflector评估
    INTERNAL_COMMUNICATION = "internal_communication"  # 内部通信


class MCPToolCall(BaseModel):
    """工具调用定义"""
    tool_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="工具调用ID")
    tool_name: str = Field(..., description="工具名称")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="工具参数")
    timestamp: datetime = Field(default_factory=datetime.now, description="调用时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MCPToolResponse(BaseModel):
    """工具响应定义"""
    tool_id: str = Field(..., description="对应的工具调用ID")
    tool_name: str = Field(..., description="工具名称")
    success: bool = Field(..., description="是否成功")
    result: Optional[Any] = Field(None, description="执行结果")
    error: Optional[str] = Field(None, description="错误信息")
    execution_time: Optional[float] = Field(None, description="执行时间（秒）")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MCPContext(BaseModel):
    """MCP上下文结构"""
    user_profile: Optional[Dict[str, Any]] = Field(None, description="用户画像")
    emotion_state: Optional[Dict[str, Any]] = Field(None, description="情感状态")
    task_goal: Optional[Dict[str, Any]] = Field(None, description="任务目标")
    memory_summary: Optional[Dict[str, Any]] = Field(None, description="记忆摘要")
    conversation_history: Optional[List[Dict[str, Any]]] = Field(None, description="对话历史")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "user_profile": self.user_profile,
            "emotion_state": self.emotion_state,
            "task_goal": self.task_goal,
            "memory_summary": self.memory_summary,
            "conversation_history": self.conversation_history,
            "metadata": self.metadata
        }


class MCPMessage(BaseModel):
    """
    MCP消息 - 核心协议结构
    
    每一轮交互都封装为MCP消息，包含：
    - content: 自然语言内容
    - context: 结构化上下文
    - tool_calls: 工具调用指令
    - tool_responses: 工具执行结果
    """
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="消息ID")
    message_type: MCPMessageType = Field(..., description="消息类型")
    content: str = Field(..., description="自然语言内容")
    context: MCPContext = Field(default_factory=MCPContext, description="结构化上下文")
    tool_calls: List[MCPToolCall] = Field(default_factory=list, description="工具调用指令")
    tool_responses: List[MCPToolResponse] = Field(default_factory=list, description="工具执行结果")
    timestamp: datetime = Field(default_factory=datetime.now, description="消息时间戳")
    source_module: Optional[str] = Field(None, description="来源模块")
    target_module: Optional[str] = Field(None, description="目标模块")
    metadata: Optional[Dict[str, Any]] = Field(None, description="额外元数据")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（用于JSON序列化）"""
        return {
            "message_id": self.message_id,
            "message_type": self.message_type.value,
            "content": self.content,
            "context": self.context.to_dict(),
            "tool_calls": [tc.dict() for tc in self.tool_calls],
            "tool_responses": [tr.dict() for tr in self.tool_responses],
            "timestamp": self.timestamp.isoformat(),
            "source_module": self.source_module,
            "target_module": self.target_module,
            "metadata": self.metadata or {}
        }
    
    def to_json(self, indent: int = 2) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPMessage':
        """从字典创建MCP消息"""
        # 处理tool_calls
        tool_calls = []
        if "tool_calls" in data:
            for tc_data in data["tool_calls"]:
                if isinstance(tc_data, dict):
                    tool_calls.append(MCPToolCall(**tc_data))
        
        # 处理tool_responses
        tool_responses = []
        if "tool_responses" in data:
            for tr_data in data["tool_responses"]:
                if isinstance(tr_data, dict):
                    tool_responses.append(MCPToolResponse(**tr_data))
        
        # 处理context
        context_data = data.get("context", {})
        context = MCPContext(**context_data) if context_data else MCPContext()
        
        # 处理timestamp
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        elif timestamp is None:
            timestamp = datetime.now()
        
        return cls(
            message_id=data.get("message_id", str(uuid.uuid4())),
            message_type=MCPMessageType(data.get("message_type", "internal_communication")),
            content=data.get("content", ""),
            context=context,
            tool_calls=tool_calls,
            tool_responses=tool_responses,
            timestamp=timestamp,
            source_module=data.get("source_module"),
            target_module=data.get("target_module"),
            metadata=data.get("metadata")
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'MCPMessage':
        """从JSON字符串创建MCP消息"""
        data = json.loads(json_str)
        return cls.from_dict(data)


class MCPProtocol:
    """
    MCP协议处理器
    
    提供MCP消息的创建、验证、转换等功能
    """
    
    @staticmethod
    def create_user_input(
        content: str,
        user_profile: Optional[Dict[str, Any]] = None,
        emotion_state: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> MCPMessage:
        """
        创建用户输入MCP消息
        
        Args:
            content: 用户输入内容
            user_profile: 用户画像
            emotion_state: 情感状态
            conversation_history: 对话历史
            
        Returns:
            MCP消息
        """
        context = MCPContext(
            user_profile=user_profile,
            emotion_state=emotion_state,
            conversation_history=conversation_history
        )
        
        return MCPMessage(
            message_type=MCPMessageType.USER_INPUT,
            content=content,
            context=context,
            source_module="user",
            target_module="agent_core"
        )
    
    @staticmethod
    def create_planner_output(
        content: str,
        task_goal: Dict[str, Any],
        tool_calls: List[MCPToolCall],
        context: Optional[MCPContext] = None
    ) -> MCPMessage:
        """
        创建Planner输出MCP消息
        
        Args:
            content: 规划说明
            task_goal: 任务目标
            tool_calls: 工具调用列表
            context: 上下文（可选）
            
        Returns:
            MCP消息
        """
        if context is None:
            context = MCPContext()
        
        context.task_goal = task_goal
        
        return MCPMessage(
            message_type=MCPMessageType.PLANNER_OUTPUT,
            content=content,
            context=context,
            tool_calls=tool_calls,
            source_module="planner",
            target_module="tool_caller"
        )
    
    @staticmethod
    def create_tool_request(
        tool_calls: List[MCPToolCall],
        context: Optional[MCPContext] = None
    ) -> MCPMessage:
        """
        创建工具请求MCP消息
        
        Args:
            tool_calls: 工具调用列表
            context: 上下文（可选）
            
        Returns:
            MCP消息
        """
        if context is None:
            context = MCPContext()
        
        return MCPMessage(
            message_type=MCPMessageType.TOOL_REQUEST,
            content=f"执行 {len(tool_calls)} 个工具调用",
            context=context,
            tool_calls=tool_calls,
            source_module="planner",
            target_module="tool_caller"
        )
    
    @staticmethod
    def create_tool_response(
        tool_responses: List[MCPToolResponse],
        context: Optional[MCPContext] = None
    ) -> MCPMessage:
        """
        创建工具响应MCP消息
        
        Args:
            tool_responses: 工具响应列表
            context: 上下文（可选）
            
        Returns:
            MCP消息
        """
        if context is None:
            context = MCPContext()
        
        success_count = sum(1 for tr in tool_responses if tr.success)
        content = f"工具执行完成：{success_count}/{len(tool_responses)} 成功"
        
        return MCPMessage(
            message_type=MCPMessageType.TOOL_RESPONSE,
            content=content,
            context=context,
            tool_responses=tool_responses,
            source_module="tool_caller",
            target_module="agent_core"
        )
    
    @staticmethod
    def create_agent_response(
        content: str,
        context: Optional[MCPContext] = None,
        tool_responses: Optional[List[MCPToolResponse]] = None
    ) -> MCPMessage:
        """
        创建Agent回复MCP消息
        
        Args:
            content: Agent回复内容
            context: 上下文（可选）
            tool_responses: 工具响应列表（可选）
            
        Returns:
            MCP消息
        """
        if context is None:
            context = MCPContext()
        
        return MCPMessage(
            message_type=MCPMessageType.AGENT_RESPONSE,
            content=content,
            context=context,
            tool_responses=tool_responses or [],
            source_module="agent_core",
            target_module="user"
        )
    
    @staticmethod
    def create_reflector_evaluation(
        content: str,
        evaluation_result: Dict[str, Any],
        context: Optional[MCPContext] = None
    ) -> MCPMessage:
        """
        创建Reflector评估MCP消息
        
        Args:
            content: 评估说明
            evaluation_result: 评估结果
            context: 上下文（可选）
            
        Returns:
            MCP消息
        """
        if context is None:
            context = MCPContext()
        
        return MCPMessage(
            message_type=MCPMessageType.REFLECTOR_EVALUATION,
            content=content,
            context=context,
            metadata={"evaluation": evaluation_result},
            source_module="reflector",
            target_module="agent_core"
        )
    
    @staticmethod
    def validate_message(message: MCPMessage) -> Tuple[bool, Optional[str]]:
        """
        验证MCP消息
        
        Args:
            message: MCP消息
            
        Returns:
            (是否有效, 错误信息)
        """
        # 检查必需字段
        if not message.content:
            return False, "content字段不能为空"
        
        # 检查tool_calls和tool_responses的关联
        if message.tool_responses:
            tool_ids = {tc.tool_id for tc in message.tool_calls}
            response_ids = {tr.tool_id for tr in message.tool_responses}
            
            # 检查是否有未对应的响应
            unmatched = response_ids - tool_ids
            if unmatched:
                return False, f"存在未对应的工具响应ID: {unmatched}"
        
        return True, None
    
    @staticmethod
    def merge_context(
        base_context: MCPContext,
        additional_context: MCPContext
    ) -> MCPContext:
        """
        合并上下文
        
        Args:
            base_context: 基础上下文
            additional_context: 附加上下文
            
        Returns:
            合并后的上下文
        """
        merged = MCPContext()
        
        # 合并各个字段（附加上下文优先）
        merged.user_profile = additional_context.user_profile or base_context.user_profile
        merged.emotion_state = additional_context.emotion_state or base_context.emotion_state
        merged.task_goal = additional_context.task_goal or base_context.task_goal
        merged.memory_summary = additional_context.memory_summary or base_context.memory_summary
        
        # 合并对话历史
        base_history = base_context.conversation_history or []
        additional_history = additional_context.conversation_history or []
        merged.conversation_history = base_history + additional_history
        
        # 合并元数据
        base_metadata = base_context.metadata or {}
        additional_metadata = additional_context.metadata or {}
        merged.metadata = {**base_metadata, **additional_metadata}
        
        return merged


class MCPLogger:
    """
    MCP日志记录器
    
    记录所有MCP消息，支持可追溯性和可重放性
    """
    
    def __init__(self, log_file: Optional[str] = None):
        """
        初始化日志记录器
        
        Args:
            log_file: 日志文件路径（可选，如果为None则只记录到内存）
        """
        self.log_file = log_file
        self.message_log: List[MCPMessage] = []
        self.max_memory_logs = 1000  # 内存中最多保存的日志数量
    
    def log(self, message: MCPMessage):
        """
        记录MCP消息
        
        Args:
            message: MCP消息
        """
        # 验证消息
        is_valid, error = MCPProtocol.validate_message(message)
        if not is_valid:
            print(f"[MCP Logger] 警告：消息验证失败: {error}")
        
        # 添加到内存日志
        self.message_log.append(message)
        
        # 限制内存日志大小
        if len(self.message_log) > self.max_memory_logs:
            self.message_log = self.message_log[-self.max_memory_logs:]
        
        # 写入文件（如果指定）
        if self.log_file:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(message.to_json() + '\n')
            except Exception as e:
                print(f"[MCP Logger] 写入日志文件失败: {str(e)}")
    
    def get_logs(
        self,
        message_type: Optional[MCPMessageType] = None,
        source_module: Optional[str] = None,
        limit: int = 100
    ) -> List[MCPMessage]:
        """
        获取日志
        
        Args:
            message_type: 消息类型过滤（可选）
            source_module: 来源模块过滤（可选）
            limit: 返回数量限制
            
        Returns:
            MCP消息列表
        """
        logs = self.message_log
        
        if message_type:
            logs = [msg for msg in logs if msg.message_type == message_type]
        
        if source_module:
            logs = [msg for msg in logs if msg.source_module == source_module]
        
        return logs[-limit:]
    
    def get_interaction_trace(self, interaction_id: str) -> List[MCPMessage]:
        """
        获取完整交互链
        
        Args:
            interaction_id: 交互ID（通过metadata中的interaction_id查找）
            
        Returns:
            MCP消息列表（按时间排序）
        """
        trace = []
        for msg in self.message_log:
            if msg.metadata and msg.metadata.get("interaction_id") == interaction_id:
                trace.append(msg)
        
        # 按时间排序
        trace.sort(key=lambda x: x.timestamp)
        return trace
    
    def export_logs(self, output_file: str):
        """
        导出日志到文件
        
        Args:
            output_file: 输出文件路径
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for msg in self.message_log:
                    f.write(msg.to_json() + '\n')
        except Exception as e:
            print(f"[MCP Logger] 导出日志失败: {str(e)}")


# 全局MCP日志记录器实例
_mcp_logger_instance: Optional[MCPLogger] = None

def get_mcp_logger(log_file: Optional[str] = None) -> MCPLogger:
    """
    获取全局MCP日志记录器
    
    Args:
        log_file: 日志文件路径（仅在首次调用时生效）
        
    Returns:
        MCP日志记录器实例
    """
    global _mcp_logger_instance
    if _mcp_logger_instance is None:
        _mcp_logger_instance = MCPLogger(log_file)
    return _mcp_logger_instance


# 使用示例
if __name__ == "__main__":
    # 创建MCP协议处理器
    protocol = MCPProtocol()
    
    # 示例1：创建用户输入消息
    user_msg = protocol.create_user_input(
        content="我最近心情很不好，感觉很焦虑",
        emotion_state={"emotion": "焦虑", "intensity": 7.5}
    )
    print("用户输入消息：")
    print(user_msg.to_json())
    print("\n" + "="*60 + "\n")
    
    # 示例2：创建Planner输出消息
    tool_call = MCPToolCall(
        tool_name="search_memory",
        parameters={"query": "焦虑", "user_id": "user_123"}
    )
    planner_msg = protocol.create_planner_output(
        content="识别到情感支持需求，需要检索相关记忆",
        task_goal={"goal_type": "emotional_support", "complexity": "medium"},
        tool_calls=[tool_call]
    )
    print("Planner输出消息：")
    print(planner_msg.to_json())
    print("\n" + "="*60 + "\n")
    
    # 示例3：创建工具响应消息
    tool_response = MCPToolResponse(
        tool_id=tool_call.tool_id,
        tool_name="search_memory",
        success=True,
        result={"count": 3, "memories": []}
    )
    tool_response_msg = protocol.create_tool_response(
        tool_responses=[tool_response]
    )
    print("工具响应消息：")
    print(tool_response_msg.to_json())
    print("\n" + "="*60 + "\n")
    
    # 示例4：使用日志记录器
    logger = get_mcp_logger()
    logger.log(user_msg)
    logger.log(planner_msg)
    logger.log(tool_response_msg)
    
    print("日志记录：")
    print(f"共记录了 {len(logger.get_logs())} 条消息")

