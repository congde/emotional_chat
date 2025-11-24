"""
MCP (Model Context Protocol) 协议模块

提供标准化的Agent模块间通信协议
"""

from .mcp import (
    MCPMessage,
    MCPMessageType,
    MCPToolCall,
    MCPToolResponse,
    MCPContext,
    MCPProtocol,
    MCPLogger,
    get_mcp_logger,
    create_mcp_protocol_with_context
)

__all__ = [
    "MCPMessage",
    "MCPMessageType",
    "MCPToolCall",
    "MCPToolResponse",
    "MCPContext",
    "MCPProtocol",
    "MCPLogger",
    "get_mcp_logger",
    "create_mcp_protocol_with_context"
]

