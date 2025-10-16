"""
路由模块 - API路由定义
"""

from backend.routers.chat import router as chat_router
from backend.routers.memory import router as memory_router
from backend.routers.feedback import router as feedback_router
from backend.routers.evaluation import router as evaluation_router

# 模块化路由
from backend.modules.rag.routers.rag_router import router as rag_router
from backend.modules.agent.routers.agent_router import router as agent_router

__all__ = [
    "chat_router",
    "memory_router",
    "feedback_router",
    "evaluation_router",
    "rag_router",
    "agent_router",
]

