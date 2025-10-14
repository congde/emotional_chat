# 使用 pysqlite3-binary 替换 sqlite3 以支持 ChromaDB
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import chromadb
from chromadb.config import Settings
import uuid
from typing import List, Dict, Any, Optional
from config import Config

class VectorStore:
    def __init__(self):
        # 禁用遥测以避免 Python 3.8 兼容性问题
        settings = Settings(
            anonymized_telemetry=False,
            allow_reset=True
        )
        self.client = chromadb.PersistentClient(
            path=Config.CHROMA_PERSIST_DIRECTORY,
            settings=settings
        )
        # 不使用自定义嵌入器，使用ChromaDB默认的嵌入函数
        self.embedder = None  # ChromaDB会自动使用默认嵌入
        
        # 使用默认嵌入函数，设置较长的超时时间
        from chromadb.utils import embedding_functions
        # 创建默认嵌入函数，增加超时时间
        default_ef = embedding_functions.DefaultEmbeddingFunction()
        
        # 创建集合，使用自定义嵌入函数
        self.conversation_collection = self.client.get_or_create_collection(
            name="conversations",
            embedding_function=default_ef,
            metadata={"hnsw:space": "cosine"}
        )
        
        self.knowledge_collection = self.client.get_or_create_collection(
            name="knowledge",
            embedding_function=default_ef,
            metadata={"hnsw:space": "cosine"}
        )
        
        self.emotion_collection = self.client.get_or_create_collection(
            name="emotions",
            embedding_function=default_ef,
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_conversation(self, session_id: str, message: str, response: str, emotion: str = None):
        """存储对话记录"""
        conversation_text = f"用户: {message}\n助手: {response}"
        if emotion:
            conversation_text += f"\n情感: {emotion}"
        
        doc_id = f"{session_id}_{uuid.uuid4().hex[:8]}"
        
        self.conversation_collection.add(
            documents=[conversation_text],
            metadatas=[{
                "session_id": session_id,
                "emotion": emotion or "neutral",
                "timestamp": str(uuid.uuid4().time_low)
            }],
            ids=[doc_id]
        )
    
    def search_similar_conversations(self, query: str, session_id: str = None, n_results: int = 5):
        """搜索相似对话"""
        results = self.conversation_collection.query(
            query_texts=[query],
            n_results=n_results,
            where={"session_id": session_id} if session_id else None
        )
        return results
    
    def add_knowledge(self, text: str, category: str = "general", metadata: Dict = None):
        """添加知识库内容"""
        doc_id = uuid.uuid4().hex
        self.knowledge_collection.add(
            documents=[text],
            metadatas=[{
                "category": category,
                **(metadata or {})
            }],
            ids=[doc_id]
        )
    
    def search_knowledge(self, query: str, category: str = None, n_results: int = 3):
        """搜索知识库"""
        where_clause = {"category": category} if category else None
        results = self.knowledge_collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause
        )
        return results
    
    def add_emotion_example(self, text: str, emotion: str, intensity: float):
        """添加情感示例"""
        doc_id = uuid.uuid4().hex
        self.emotion_collection.add(
            documents=[text],
            metadatas=[{
                "emotion": emotion,
                "intensity": intensity
            }],
            ids=[doc_id]
        )
    
    def search_emotion_patterns(self, query: str, emotion: str = None, n_results: int = 3):
        """搜索情感模式"""
        where_clause = {"emotion": emotion} if emotion else None
        results = self.emotion_collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause
        )
        return results
    
    def get_session_history(self, session_id: str, limit: int = 10):
        """获取会话历史"""
        results = self.conversation_collection.get(
            where={"session_id": session_id},
            limit=limit
        )
        return results
