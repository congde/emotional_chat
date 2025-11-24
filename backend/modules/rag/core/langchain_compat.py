#!/usr/bin/env python3
"""
LangChain 兼容层
统一使用 langchain 0.2.x+ (Python 3.10+)
"""

# 1. Document Loaders
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader, TextLoader
from langchain_community.vectorstores import Chroma

# 2. Embeddings
from langchain_openai import OpenAIEmbeddings

# 3. Text Splitter
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 4. Document
from langchain_core.documents import Document

# 版本信息
try:
    import langchain
    LANGCHAIN_VERSION = langchain.__version__
except (ImportError, AttributeError):
    LANGCHAIN_VERSION = "unknown"

IS_NEW_VERSION = True  # 统一使用新版本

__all__ = [
    'PyPDFLoader',
    'DirectoryLoader', 
    'TextLoader',
    'Chroma',
    'OpenAIEmbeddings',
    'RecursiveCharacterTextSplitter',
    'Document',
    'IS_NEW_VERSION',
    'LANGCHAIN_VERSION'
]
