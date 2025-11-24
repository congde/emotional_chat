#!/usr/bin/env python3
"""
LLM模块数据模型
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator

from backend.schemas.common_schemas import BaseResponse


class LLMProvider(str, Enum):
    """LLM提供商枚举"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE_OPENAI = "azure_openai"
    GOOGLE = "google"
    LOCAL = "local"


class MessageRole(str, Enum):
    """消息角色枚举"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


class LLMRequest(BaseModel):
    """LLM请求模型"""
    messages: List['ChatMessage'] = Field(..., description="消息列表")
    model: str = Field(..., description="模型名称")
    temperature: float = Field(0.7, ge=0, le=2, description="温度参数")
    max_tokens: Optional[int] = Field(None, ge=1, le=32000, description="最大令牌数")
    top_p: float = Field(1.0, ge=0, le=1, description="Top-p参数")
    frequency_penalty: float = Field(0.0, ge=-2, le=2, description="频率惩罚")
    presence_penalty: float = Field(0.0, ge=-2, le=2, description="存在惩罚")
    stop: Optional[Union[str, List[str]]] = Field(None, description="停止词")
    stream: bool = Field(False, description="是否流式输出")
    provider: LLMProvider = Field(LLMProvider.OPENAI, description="LLM提供商")
    
    @validator('messages')
    def validate_messages(cls, v):
        if not v:
            raise ValueError('消息列表不能为空')
        return v


class LLMResponse(BaseModel):
    """LLM响应模型"""
    content: str = Field(..., description="回复内容")
    model: str = Field(..., description="使用的模型")
    provider: LLMProvider = Field(..., description="LLM提供商")
    usage: 'LLMUsage' = Field(..., description="使用统计")
    finish_reason: str = Field(..., description="完成原因")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    response_time: float = Field(..., description="响应时间")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ChatMessage(BaseModel):
    """聊天消息模型"""
    role: MessageRole = Field(..., description="消息角色")
    content: str = Field(..., description="消息内容")
    name: Optional[str] = Field(None, description="消息发送者名称")
    function_call: Optional[Dict[str, Any]] = Field(None, description="函数调用")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(None, description="工具调用")
    timestamp: Optional[datetime] = Field(None, description="消息时间戳")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @validator('content')
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError('消息内容不能为空')
        return v.strip()


class LLMUsage(BaseModel):
    """LLM使用统计"""
    prompt_tokens: int = Field(0, ge=0, description="提示令牌数")
    completion_tokens: int = Field(0, ge=0, description="完成令牌数")
    total_tokens: int = Field(0, ge=0, description="总令牌数")
    prompt_cost: float = Field(0.0, ge=0, description="提示成本")
    completion_cost: float = Field(0.0, ge=0, description="完成成本")
    total_cost: float = Field(0.0, ge=0, description="总成本")


class LLMError(BaseModel):
    """LLM错误模型"""
    error_type: str = Field(..., description="错误类型")
    error_code: str = Field(..., description="错误代码")
    message: str = Field(..., description="错误消息")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详情")
    timestamp: datetime = Field(default_factory=datetime.now, description="错误时间")
    request_id: Optional[str] = Field(None, description="请求ID")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CompletionRequest(BaseModel):
    """补全请求模型"""
    prompt: str = Field(..., min_length=1, description="提示文本")
    model: str = Field(..., description="模型名称")
    temperature: float = Field(0.7, ge=0, le=2, description="温度参数")
    max_tokens: int = Field(1000, ge=1, le=32000, description="最大令牌数")
    top_p: float = Field(1.0, ge=0, le=1, description="Top-p参数")
    frequency_penalty: float = Field(0.0, ge=-2, le=2, description="频率惩罚")
    presence_penalty: float = Field(0.0, ge=-2, le=2, description="存在惩罚")
    stop: Optional[Union[str, List[str]]] = Field(None, description="停止词")
    stream: bool = Field(False, description="是否流式输出")
    provider: LLMProvider = Field(LLMProvider.OPENAI, description="LLM提供商")
    
    @validator('prompt')
    def validate_prompt(cls, v):
        if not v.strip():
            raise ValueError('提示文本不能为空')
        return v.strip()


class CompletionResponse(BaseModel):
    """补全响应模型"""
    text: str = Field(..., description="生成的文本")
    model: str = Field(..., description="使用的模型")
    provider: LLMProvider = Field(..., description="LLM提供商")
    usage: LLMUsage = Field(..., description="使用统计")
    finish_reason: str = Field(..., description="完成原因")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    response_time: float = Field(..., description="响应时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class LLMConfig(BaseModel):
    """LLM配置模型"""
    provider: LLMProvider = Field(LLMProvider.OPENAI, description="默认提供商")
    api_key: str = Field(..., description="API密钥")
    base_url: Optional[str] = Field(None, description="API基础URL")
    default_model: str = Field("gpt-4", description="默认模型")
    max_tokens: int = Field(4000, ge=1, le=32000, description="默认最大令牌数")
    temperature: float = Field(0.7, ge=0, le=2, description="默认温度")
    timeout: int = Field(30, ge=1, le=300, description="请求超时时间")
    max_retries: int = Field(3, ge=0, le=10, description="最大重试次数")
    rate_limit: Optional[int] = Field(None, description="速率限制")
    enable_streaming: bool = Field(True, description="是否启用流式输出")
    enable_function_calling: bool = Field(False, description="是否启用函数调用")
    
    class Config:
        json_schema_extra = {
            "example": {
                "provider": "openai",
                "api_key": "sk-...",
                "base_url": "https://api.openai.com/v1",
                "default_model": "gpt-4",
                "max_tokens": 4000,
                "temperature": 0.7,
                "timeout": 30,
                "max_retries": 3,
                "rate_limit": 60,
                "enable_streaming": True,
                "enable_function_calling": False
            }
        }


class ModelInfo(BaseModel):
    """模型信息"""
    model_name: str = Field(..., description="模型名称")
    provider: LLMProvider = Field(..., description="提供商")
    max_tokens: int = Field(..., description="最大令牌数")
    context_length: int = Field(..., description="上下文长度")
    supports_streaming: bool = Field(True, description="是否支持流式输出")
    supports_function_calling: bool = Field(False, description="是否支持函数调用")
    cost_per_token: Optional[float] = Field(None, description="每令牌成本")
    description: Optional[str] = Field(None, description="模型描述")
    created_at: Optional[datetime] = Field(None, description="创建时间")


class LLMStats(BaseModel):
    """LLM统计信息"""
    total_requests: int = Field(0, description="总请求数")
    successful_requests: int = Field(0, description="成功请求数")
    failed_requests: int = Field(0, description="失败请求数")
    total_tokens: int = Field(0, description="总令牌数")
    total_cost: float = Field(0.0, description="总成本")
    average_response_time: float = Field(0.0, description="平均响应时间")
    requests_by_provider: Dict[str, int] = Field(default_factory=dict, description="按提供商统计")
    requests_by_model: Dict[str, int] = Field(default_factory=dict, description="按模型统计")
    last_updated: datetime = Field(default_factory=datetime.now, description="最后更新时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# 更新前向引用（Pydantic v1 自动处理前向引用，不需要 model_rebuild）
# 注意: model_rebuild() 是 Pydantic v2 的方法，v1 不需要
# LLMRequest.model_rebuild()  # Pydantic v1 不需要此调用
# LLMResponse.model_rebuild()  # Pydantic v1 不需要此调用
