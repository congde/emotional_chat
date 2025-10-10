from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.simple_langchain_engine import SimpleEmotionalChatEngine as EmotionalChatEngine
from backend.models import ChatRequest, ChatResponse
from backend.database import get_db

# 创建FastAPI应用
app = FastAPI(
    title="情感聊天机器人API",
    description="基于LangChain和MySQL的情感支持聊天机器人",
    version="2.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化聊天引擎
chat_engine = EmotionalChatEngine()

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "情感聊天机器人API",
        "version": "2.0.0",
        "status": "running",
        "features": ["LangChain", "MySQL", "VectorDB", "Emotion Analysis"]
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """聊天接口"""
    try:
        response = chat_engine.chat(request)
        return response
    except Exception as e:
        print(f"聊天接口错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{session_id}/summary")
async def get_session_summary(session_id: str):
    """获取会话摘要"""
    try:
        summary = chat_engine.get_session_summary(session_id)
        if "error" in summary:
            raise HTTPException(status_code=404, detail=summary["error"])
        return summary
    except Exception as e:
        print(f"获取会话摘要错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{session_id}/history")
async def get_session_history(session_id: str, limit: int = 20):
    """获取会话历史"""
    try:
        from backend.database import DatabaseManager
        with DatabaseManager() as db:
            messages = db.get_session_messages(session_id, limit)
            
            if not messages:
                raise HTTPException(status_code=404, detail="会话不存在")
            
            return {
                "session_id": session_id,
                "messages": [
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "emotion": msg.emotion,
                        "emotion_intensity": msg.emotion_intensity,
                        "timestamp": msg.created_at.isoformat()
                    }
                    for msg in messages
                ]
            }
    except Exception as e:
        print(f"获取会话历史错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}/emotion-trends")
async def get_user_emotion_trends(user_id: str):
    """获取用户情感趋势"""
    try:
        trends = chat_engine.get_user_emotion_trends(user_id)
        if "error" in trends:
            raise HTTPException(status_code=404, detail=trends["error"])
        return trends
    except Exception as e:
        print(f"获取情感趋势错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        from backend.database import DatabaseManager
        # 测试数据库连接
        from backend.database import DatabaseManager
        db_manager = DatabaseManager()
        db_manager.log_system_event("INFO", "Health check")
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0",
            "database": "connected",
            "vector_db": "ready"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    print("🚀 启动情感聊天机器人后端服务...")
    print("📍 服务地址: http://localhost:8008")
    print("🔗 API文档: http://localhost:8008/docs")
    print("🗄️ 数据库: MySQL")
    print("🧠 向量数据库: Chroma")
    print("🤖 AI引擎: LangChain + OpenAI")
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8008,
        reload=True,
        log_level="info"
    )
