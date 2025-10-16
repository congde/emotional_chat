#!/usr/bin/env python3
"""
RAG模块数据模型
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator

from backend.schemas.common_schemas import BaseResponse, PaginationRequest


class KnowledgeSource(BaseModel):
    """知识来源模型"""
    content: str = Field(..., description="知识内容")
    metadata: Dict[str, Any] = Field(..., description="元数据")
    relevance_score: Optional[float] = Field(None, description="相关度分数")


class DocumentInfo(BaseModel):
    """文档信息模型"""
    filename: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小")
    file_type: str = Field(..., description="文件类型")
    upload_time: datetime = Field(default_factory=datetime.now, description="上传时间")
    chunk_count: Optional[int] = Field(None, description="文档块数量")
    metadata: Optional[Dict[str, Any]] = Field(None, description="文档元数据")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class RAGRequest(BaseModel):
    """RAG问答请求"""
    question: str = Field(..., min_length=1, max_length=1000, description="用户问题")
    search_k: int = Field(3, ge=1, le=10, description="检索文档数量")
    use_context: bool = Field(True, description="是否使用上下文")
    conversation_history: Optional[List[Dict[str, str]]] = Field(None, description="对话历史")
    user_emotion: Optional[str] = Field(None, description="用户情绪")
    
    @validator('question')
    def validate_question(cls, v):
        if not v.strip():
            raise ValueError('问题不能为空')
        return v.strip()


class RAGResponse(BaseModel):
    """RAG问答响应"""
    answer: str = Field(..., description="生成的回答")
    sources: List[KnowledgeSource] = Field(..., description="知识来源")
    confidence: float = Field(..., ge=0, le=1, description="回答置信度")
    knowledge_count: int = Field(..., ge=0, description="使用的知识源数量")
    used_context: bool = Field(..., description="是否使用了上下文")
    processing_time: Optional[float] = Field(None, description="处理时间（秒）")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class KnowledgeSearchRequest(BaseModel):
    """知识搜索请求"""
    query: str = Field(..., min_length=1, max_length=200, description="搜索查询")
    k: int = Field(3, ge=1, le=20, description="返回结果数量")
    similarity_threshold: Optional[float] = Field(0.7, ge=0, le=1, description="相似度阈值")
    filters: Optional[Dict[str, Any]] = Field(None, description="搜索过滤器")
    
    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError('搜索查询不能为空')
        return v.strip()


class KnowledgeSearchResponse(BaseModel):
    """知识搜索响应"""
    query: str = Field(..., description="搜索查询")
    results: List[KnowledgeSource] = Field(..., description="搜索结果")
    total: int = Field(..., ge=0, description="结果总数")
    search_time: float = Field(..., description="搜索时间（秒）")
    timestamp: datetime = Field(default_factory=datetime.now, description="搜索时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DocumentUploadRequest(BaseModel):
    """文档上传请求"""
    filename: str = Field(..., description="文件名")
    file_type: str = Field(..., description="文件类型")
    content: bytes = Field(..., description="文件内容")
    metadata: Optional[Dict[str, Any]] = Field(None, description="文档元数据")
    auto_chunk: bool = Field(True, description="是否自动分块")
    chunk_size: int = Field(500, ge=100, le=2000, description="分块大小")
    chunk_overlap: int = Field(50, ge=0, le=200, description="分块重叠")


class KnowledgeBaseStats(BaseModel):
    """知识库统计信息"""
    total_documents: int = Field(..., description="总文档数")
    total_chunks: int = Field(..., description="总文档块数")
    storage_size: int = Field(..., description="存储大小（字节）")
    last_updated: Optional[datetime] = Field(None, description="最后更新时间")
    embedding_model: str = Field(..., description="嵌入模型")
    collection_name: str = Field(..., description="集合名称")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class RAGConfig(BaseModel):
    """RAG配置模型"""
    enabled: bool = Field(True, description="是否启用RAG")
    knowledge_base_path: str = Field("./chroma_db/psychology_kb", description="知识库路径")
    search_k: int = Field(3, ge=1, le=10, description="默认检索数量")
    similarity_threshold: float = Field(0.7, ge=0, le=1, description="相似度阈值")
    max_context_length: int = Field(4000, ge=1000, le=8000, description="最大上下文长度")
    chunk_size: int = Field(500, ge=100, le=2000, description="文档分块大小")
    chunk_overlap: int = Field(50, ge=0, le=200, description="分块重叠大小")
    embedding_model: str = Field("text-embedding-ada-002", description="嵌入模型")


class RAGTriggerConfig(BaseModel):
    """RAG触发配置"""
    emotion_triggers: List[str] = Field(
        default=[
            "焦虑", "抑郁", "压力大", "紧张", "恐惧", 
            "悲伤", "愤怒", "失眠", "孤独"
        ],
        description="情绪触发词"
    )
    keyword_triggers: List[str] = Field(
        default=[
            "怎么办", "如何", "方法", "建议", "技巧", "练习",
            "正念", "冥想", "放松", "呼吸", "认知", "行为",
            "睡眠", "运动", "饮食", "关系", "工作", "学习"
        ],
        description="关键词触发词"
    )
    auto_trigger: bool = Field(True, description="是否自动触发")
    confidence_threshold: float = Field(0.7, ge=0, le=1, description="触发置信度阈值")
