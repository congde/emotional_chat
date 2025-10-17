#!/usr/bin/env python3
"""
通用数据模型
定义基础的数据模型和验证器
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class ResponseStatus(str, Enum):
    """响应状态枚举"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool = Field(..., description="请求是否成功")
    message: str = Field(..., description="响应消息")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")
    status_code: int = Field(200, description="HTTP状态码")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ErrorResponse(BaseResponse):
    """错误响应模型"""
    success: bool = Field(False, description="请求失败")
    error: Dict[str, Any] = Field(..., description="错误详情")
    
    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "message": "请求失败",
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "输入验证失败",
                    "details": {
                        "field": "message",
                        "reason": "消息内容不能为空"
                    }
                },
                "timestamp": "2025-10-16T14:30:00Z",
                "status_code": 400
            }
        }


class PaginationRequest(BaseModel):
    """分页请求模型"""
    page: int = Field(1, ge=1, description="页码，从1开始")
    page_size: int = Field(20, ge=1, le=100, description="每页大小，最大100")
    
    @validator('page')
    def validate_page(cls, v):
        if v < 1:
            raise ValueError('页码必须大于0')
        return v
    
    @validator('page_size')
    def validate_page_size(cls, v):
        if v < 1 or v > 100:
            raise ValueError('每页大小必须在1-100之间')
        return v


class PaginationResponse(BaseModel):
    """分页响应模型"""
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
    total: int = Field(..., description="总记录数")
    total_pages: int = Field(..., description="总页数")
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")
    
    @validator('total_pages', always=True)
    def calculate_total_pages(cls, v, values):
        total = values.get('total', 0)
        page_size = values.get('page_size', 1)
        return (total + page_size - 1) // page_size
    
    @validator('has_next', always=True)
    def calculate_has_next(cls, v, values):
        page = values.get('page', 1)
        total_pages = values.get('total_pages', 1)
        return page < total_pages
    
    @validator('has_prev', always=True)
    def calculate_has_prev(cls, v, values):
        page = values.get('page', 1)
        return page > 1


class HealthCheckResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field(..., description="服务状态")
    version: str = Field(..., description="服务版本")
    uptime: Optional[str] = Field(None, description="运行时间")
    services: Dict[str, str] = Field(..., description="各服务状态")
    timestamp: datetime = Field(default_factory=datetime.now, description="检查时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "status": "healthy",
                "version": "3.0.0",
                "uptime": "2 days, 3 hours, 45 minutes",
                "services": {
                    "database": "connected",
                    "redis": "connected",
                    "openai": "available",
                    "vector_db": "ready"
                },
                "timestamp": "2025-10-16T14:30:00Z"
            }
        }


class SystemInfoResponse(BaseModel):
    """系统信息响应模型"""
    name: str = Field(..., description="系统名称")
    version: str = Field(..., description="系统版本")
    environment: str = Field(..., description="运行环境")
    features: List[str] = Field(..., description="功能特性列表")
    architecture: str = Field(..., description="系统架构")
    agent_enabled: bool = Field(..., description="Agent模块是否启用")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class StatisticsResponse(BaseModel):
    """统计信息响应模型"""
    total_users: int = Field(..., description="总用户数")
    total_sessions: int = Field(..., description="总会话数")
    total_messages: int = Field(..., description="总消息数")
    active_sessions: int = Field(..., description="活跃会话数")
    emotion_distribution: Optional[Dict[str, int]] = Field(None, description="情绪分布")
    time_range: Optional[str] = Field(None, description="统计时间范围")
    timestamp: datetime = Field(default_factory=datetime.now, description="统计时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class FileUploadResponse(BaseModel):
    """文件上传响应模型"""
    filename: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小（字节）")
    file_type: str = Field(..., description="文件类型")
    upload_id: str = Field(..., description="上传ID")
    url: Optional[str] = Field(None, description="文件访问URL")
    timestamp: datetime = Field(default_factory=datetime.now, description="上传时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SearchRequest(BaseModel):
    """搜索请求模型"""
    query: str = Field(..., min_length=1, max_length=100, description="搜索关键词")
    filters: Optional[Dict[str, Any]] = Field(None, description="搜索过滤器")
    sort_by: Optional[str] = Field(None, description="排序字段")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="排序顺序")
    pagination: PaginationRequest = Field(default_factory=PaginationRequest, description="分页参数")
    
    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError('搜索关键词不能为空')
        return v.strip()


class SearchResponse(BaseModel):
    """搜索响应模型"""
    query: str = Field(..., description="搜索关键词")
    results: List[Dict[str, Any]] = Field(..., description="搜索结果")
    total: int = Field(..., description="结果总数")
    pagination: PaginationResponse = Field(..., description="分页信息")
    search_time: float = Field(..., description="搜索耗时（秒）")
    suggestions: Optional[List[str]] = Field(None, description="搜索建议")


class BatchRequest(BaseModel):
    """批量请求模型"""
    items: List[Dict[str, Any]] = Field(..., description="批量操作项目")
    operation: str = Field(..., description="操作类型")
    options: Optional[Dict[str, Any]] = Field(None, description="操作选项")
    
    @validator('items')
    def validate_items(cls, v):
        if not v:
            raise ValueError('批量操作项目不能为空')
        if len(v) > 100:
            raise ValueError('批量操作项目不能超过100个')
        return v


class BatchResponse(BaseModel):
    """批量响应模型"""
    total: int = Field(..., description="总项目数")
    successful: int = Field(..., description="成功项目数")
    failed: int = Field(..., description="失败项目数")
    results: List[Dict[str, Any]] = Field(..., description="操作结果")
    errors: Optional[List[Dict[str, Any]]] = Field(None, description="错误信息")


class ValidationErrorDetail(BaseModel):
    """验证错误详情"""
    field: str = Field(..., description="错误字段")
    message: str = Field(..., description="错误消息")
    value: Optional[Any] = Field(None, description="错误值")


class ValidationErrorResponse(BaseResponse):
    """验证错误响应"""
    success: bool = Field(False, description="验证失败")
    errors: List[ValidationErrorDetail] = Field(..., description="验证错误列表")
    
    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "message": "输入验证失败",
                "errors": [
                    {
                        "field": "message",
                        "message": "消息内容不能为空",
                        "value": ""
                    },
                    {
                        "field": "user_id",
                        "message": "用户ID格式不正确",
                        "value": "invalid_id"
                    }
                ],
                "timestamp": "2025-10-16T14:30:00Z",
                "status_code": 422
            }
        }
