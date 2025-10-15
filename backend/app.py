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

# 尝试导入Agent路由
try:
    from backend.routers.agent import router as agent_router
    AGENT_ENABLED = True
except ImportError:
    AGENT_ENABLED = False
    agent_router = None

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
    
    # 注册Agent路由（如果可用）
    if AGENT_ENABLED and agent_router:
        app.include_router(agent_router)
        logger.info("Agent模块已启用")
    
    # 根路由
    @app.get("/")
    async def root():
        """API根路径"""
        features = [
            "情感分析",
            "记忆系统",
            "上下文管理",
            "向量数据库",
            "LangChain集成",
            "自动评估"
        ]
        
        # 如果Agent模块启用，添加到功能列表
        if AGENT_ENABLED:
            features.append("Agent智能核心")
        
        return {
            "name": "心语情感陪伴机器人",
            "version": "3.0.0",
            "status": "running",
            "features": features,
            "architecture": "分层服务架构 + Agent核心" if AGENT_ENABLED else "分层服务架构",
            "agent_enabled": AGENT_ENABLED,
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
        routers_list = ["chat", "memory", "feedback", "evaluation"]
        services_list = ["ChatService", "MemoryService", "ContextService"]
        
        # 如果Agent模块启用，添加Agent相关信息
        if AGENT_ENABLED:
            routers_list.append("agent")
            services_list.append("AgentService")
        
        info = {
            "architecture": {
                "pattern": "分层服务架构 + Agent核心" if AGENT_ENABLED else "分层服务架构",
                "layers": ["路由层", "服务层", "核心层", "数据层"] if AGENT_ENABLED else ["路由层", "服务层", "数据层"],
                "services": services_list,
                "routers": routers_list
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
        
        # 添加Agent信息
        if AGENT_ENABLED:
            info["agent_system"] = {
                "enabled": True,
                "components": [
                    "Agent Core - 核心控制器",
                    "Memory Hub - 记忆中枢",
                    "Planner - 任务规划器",
                    "Tool Caller - 工具调用器",
                    "Reflector - 反思优化器"
                ],
                "capabilities": [
                    "智能任务规划",
                    "工具自动调用",
                    "主动回访",
                    "策略优化"
                ],
                "external_tools": [
                    "日历API",
                    "音频播放服务",
                    "心理资源数据库",
                    "定时提醒服务"
                ]
            }
        
        return info
    
    logger.info("应用初始化完成")
    
    return app


# 创建应用实例
app = create_app()

