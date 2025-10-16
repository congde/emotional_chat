#!/usr/bin/env python3
"""
接口定义模块
定义系统的核心接口和抽象类
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from ..models import ChatRequest, ChatResponse


@dataclass
class EmotionResult:
    """情绪分析结果"""
    emotion: str
    intensity: float
    confidence: float
    details: Dict[str, Any]


@dataclass
class MemoryInfo:
    """记忆信息"""
    id: str
    content: str
    emotion: str
    importance: float
    timestamp: str
    metadata: Dict[str, Any]


@dataclass
class ContextInfo:
    """上下文信息"""
    user_id: str
    session_id: str
    memories: List[MemoryInfo]
    emotion_history: List[EmotionResult]
    user_profile: Dict[str, Any]
    conversation_summary: str


@dataclass
class RAGResult:
    """RAG检索结果"""
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    knowledge_count: int
    used_context: bool


class IChatEngine(ABC):
    """聊天引擎接口"""
    
    @abstractmethod
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """处理聊天请求"""
        pass
    
    @abstractmethod
    async def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """获取会话摘要"""
        pass
    
    @abstractmethod
    async def get_user_emotion_trends(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """获取用户情绪趋势"""
        pass


class IEmotionAnalyzer(ABC):
    """情绪分析器接口"""
    
    @abstractmethod
    async def analyze_emotion(self, text: str) -> EmotionResult:
        """分析文本情绪"""
        pass
    
    @abstractmethod
    async def analyze_emotion_batch(self, texts: List[str]) -> List[EmotionResult]:
        """批量分析情绪"""
        pass
    
    @abstractmethod
    async def get_emotion_history(self, user_id: str, limit: int = 50) -> List[EmotionResult]:
        """获取用户情绪历史"""
        pass


class IMemoryService(ABC):
    """记忆服务接口"""
    
    @abstractmethod
    async def extract_memories(self, text: str, emotion: str) -> List[Dict[str, Any]]:
        """从文本中提取记忆"""
        pass
    
    @abstractmethod
    async def store_memory(self, memory: Dict[str, Any]) -> str:
        """存储记忆"""
        pass
    
    @abstractmethod
    async def retrieve_memories(
        self,
        user_id: str,
        query: Optional[str] = None,
        limit: int = 10
    ) -> List[MemoryInfo]:
        """检索记忆"""
        pass
    
    @abstractmethod
    async def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """更新记忆"""
        pass
    
    @abstractmethod
    async def delete_memory(self, memory_id: str) -> bool:
        """删除记忆"""
        pass
    
    @abstractmethod
    async def get_memory_stats(self, user_id: str) -> Dict[str, Any]:
        """获取记忆统计信息"""
        pass


class IContextService(ABC):
    """上下文服务接口"""
    
    @abstractmethod
    async def build_context(
        self,
        user_id: str,
        session_id: str,
        current_message: str,
        emotion: str,
        emotion_intensity: float
    ) -> ContextInfo:
        """构建对话上下文"""
        pass
    
    @abstractmethod
    async def update_context(
        self,
        context: ContextInfo,
        new_message: str,
        new_emotion: EmotionResult
    ) -> ContextInfo:
        """更新上下文"""
        pass
    
    @abstractmethod
    async def clear_context(self, user_id: str, session_id: str) -> bool:
        """清空上下文"""
        pass


class IRAGService(ABC):
    """RAG服务接口"""
    
    @abstractmethod
    async def ask(self, question: str, search_k: int = 3) -> RAGResult:
        """向知识库提问"""
        pass
    
    @abstractmethod
    async def ask_with_context(
        self,
        question: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        user_emotion: Optional[str] = None,
        search_k: int = 3
    ) -> RAGResult:
        """带上下文的提问"""
        pass
    
    @abstractmethod
    async def search_knowledge(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """搜索知识库"""
        pass
    
    @abstractmethod
    async def add_document(self, document: Dict[str, Any]) -> bool:
        """添加文档到知识库"""
        pass
    
    @abstractmethod
    async def get_knowledge_stats(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """检查知识库是否可用"""
        pass


class IEvaluationService(ABC):
    """评估服务接口"""
    
    @abstractmethod
    async def evaluate_response(
        self,
        user_message: str,
        bot_response: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """评估回复质量"""
        pass
    
    @abstractmethod
    async def get_evaluation_history(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """获取评估历史"""
        pass
    
    @abstractmethod
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        pass


class IFeedbackService(ABC):
    """反馈服务接口"""
    
    @abstractmethod
    async def submit_feedback(
        self,
        user_id: str,
        session_id: str,
        feedback_type: str,
        content: str,
        rating: Optional[int] = None
    ) -> str:
        """提交反馈"""
        pass
    
    @abstractmethod
    async def get_feedback(
        self,
        user_id: Optional[str] = None,
        feedback_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """获取反馈"""
        pass
    
    @abstractmethod
    async def analyze_feedback(self, feedback_id: str) -> Dict[str, Any]:
        """分析反馈"""
        pass


class IDatabaseService(ABC):
    """数据库服务接口"""
    
    @abstractmethod
    async def connect(self) -> bool:
        """连接数据库"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """断开数据库连接"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        pass
    
    @abstractmethod
    async def execute_query(self, query: str, params: Dict[str, Any]) -> Any:
        """执行查询"""
        pass
    
    @abstractmethod
    async def execute_transaction(self, operations: List[Dict[str, Any]]) -> bool:
        """执行事务"""
        pass


class ICacheService(ABC):
    """缓存服务接口"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        pass
    
    @abstractmethod
    async def clear(self, pattern: Optional[str] = None) -> int:
        """清空缓存"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        pass


class ILogger(ABC):
    """日志服务接口"""
    
    @abstractmethod
    async def debug(self, message: str, **kwargs) -> None:
        """调试日志"""
        pass
    
    @abstractmethod
    async def info(self, message: str, **kwargs) -> None:
        """信息日志"""
        pass
    
    @abstractmethod
    async def warning(self, message: str, **kwargs) -> None:
        """警告日志"""
        pass
    
    @abstractmethod
    async def error(self, message: str, exception: Optional[Exception] = None, **kwargs) -> None:
        """错误日志"""
        pass
    
    @abstractmethod
    async def critical(self, message: str, exception: Optional[Exception] = None, **kwargs) -> None:
        """严重错误日志"""
        pass


class IValidationService(ABC):
    """验证服务接口"""
    
    @abstractmethod
    async def validate_request(self, request: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证请求"""
        pass
    
    @abstractmethod
    async def validate_user_input(self, text: str) -> Tuple[bool, List[str]]:
        """验证用户输入"""
        pass
    
    @abstractmethod
    async def sanitize_input(self, text: str) -> str:
        """清理输入"""
        pass
