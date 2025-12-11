"""
RAG模块
检索增强生成(Retrieval-Augmented Generation)相关功能
"""

from .core.knowledge_base import KnowledgeBaseManager, PsychologyKnowledgeLoader
from .core.chunking_strategies import (
    CharacterTextSplitter,
    SentenceTextSplitter,
    MarkdownStructureSplitter,
    DialogueSplitter,
    SmallBigChunking,
    ParentChildChunking
)
from .core.chunking_selector import ChunkingStrategySelector
from .services.rag_service import RAGService, RAGIntegrationService
from .models.rag_models import RAGRequest, RAGResponse, KnowledgeSearchRequest
from .routers.rag_router import router as rag_router

__all__ = [
    "KnowledgeBaseManager",
    "PsychologyKnowledgeLoader",
    "CharacterTextSplitter",
    "SentenceTextSplitter",
    "MarkdownStructureSplitter",
    "DialogueSplitter",
    "SmallBigChunking",
    "ParentChildChunking",
    "ChunkingStrategySelector",
    "RAGService",
    "RAGIntegrationService",
    "RAGRequest",
    "RAGResponse", 
    "KnowledgeSearchRequest",
    "rag_router"
]
