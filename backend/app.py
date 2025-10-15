#!/usr/bin/env python3
"""
应用工厂
创建和配置FastAPI应用实例
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pathlib import Path
import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 导入路由
from backend.routers import (
    chat_router,
    memory_router,
    feedback_router,
    evaluation_router
)

# 导入日志配置
from backend.logging_config import get_logger

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """
    创建FastAPI应用实例
    
    Returns:
        配置好的FastAPI应用
    """
    # 创建应用
    app = FastAPI(
        title="心语情感陪伴机器人 API",
        description="基于LangChain和记忆系统的情感支持聊天机器人",
        version="3.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境中应该设置具体的域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 配置静态文件
    upload_dir = Path(project_root) / "uploads"
    upload_dir.mkdir(exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")
    
    # 注册路由
    app.include_router(chat_router)
    app.include_router(memory_router)
    app.include_router(feedback_router)
    app.include_router(evaluation_router)
    
    # 根路由
    @app.get("/")
    async def root():
        """API根路径"""
        return {
            "name": "心语情感陪伴机器人",
            "version": "3.0.0",
            "status": "running",
            "features": [
                "情感分析",
                "记忆系统",
                "上下文管理",
                "向量数据库",
                "LangChain集成",
                "自动评估"
            ],
            "architecture": "分层服务架构",
            "timestamp": datetime.now().isoformat()
        }
    
    # 健康检查
    @app.get("/health")
    async def health_check():
        """健康检查"""
        try:
            from backend.database import DatabaseManager
            
            # 测试数据库连接
            db_manager = DatabaseManager()
            db_manager.log_system_event("INFO", "Health check")
            
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "3.0.0",
                "database": "connected",
                "vector_db": "ready",
                "memory_system": "enabled"
            }
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "timestamp": datetime.now().isoformat(),
                    "error": str(e)
                }
            )
    
    # 系统信息
    @app.get("/system/info")
    async def system_info():
        """系统信息"""
        return {
            "architecture": {
                "pattern": "分层服务架构",
                "layers": ["路由层", "服务层", "数据层"],
                "services": ["ChatService", "MemoryService", "ContextService"],
                "routers": ["chat", "memory", "feedback", "evaluation"]
            },
            "memory_system": {
                "enabled": True,
                "components": ["记忆提取器", "记忆管理器", "上下文组装器"],
                "storage": ["向量数据库 (ChromaDB)", "关系数据库 (MySQL)"]
            },
            "features": {
                "emotion_analysis": "情绪分析与追踪",
                "memory_extraction": "自动记忆提取",
                "context_assembly": "上下文组装",
                "user_profiling": "用户画像",
                "evaluation": "自动评估系统"
            }
        }
    
    logger.info("应用初始化完成")
    
    return app


# 创建应用实例
app = create_app()

