from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import sys
import os
import json
import uuid
import shutil
from datetime import datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import PyPDF2
from PIL import Image
import io
from typing import List
import logging

# 导入日志配置
from backend.logging_config import get_logger

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 如果环境变量中有PROJECT_ROOT，使用它（从run_backend.py设置）
if 'PROJECT_ROOT' in os.environ:
    project_root = os.environ['PROJECT_ROOT']

from backend.simple_langchain_engine import SimpleEmotionalChatEngine as EmotionalChatEngine
from backend.models import ChatRequest, ChatResponse, FeedbackRequest, FeedbackResponse, FeedbackStatistics, FeedbackListResponse
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

# 文件存储配置（使用项目根目录）
UPLOAD_DIR = Path(project_root) / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# 添加静态文件服务
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# 初始化日志记录器
logger = get_logger(__name__)

# 初始化聊天引擎
chat_engine = EmotionalChatEngine()

# 支持的文件类型
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.txt', '.doc', '.docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def is_allowed_file(filename):
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    """从PDF文件中提取文本"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        logger.error(f"PDF文本提取失败: {e}")
        return ""

def extract_text_from_image(file_path):
    """从图片中提取文本（OCR功能，这里简化处理）"""
    try:
        # 这里可以集成OCR库如pytesseract
        # 暂时返回占位符
        return "[图片内容 - 需要OCR处理]"
    except Exception as e:
        logger.error(f"图片文本提取失败: {e}")
        return ""

def parse_url_content(url):
    """解析URL内容"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 提取标题
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "无标题"
        
        # 提取主要内容
        content_selectors = [
            'article', 'main', '.content', '.post-content', 
            '.entry-content', 'p', 'div'
        ]
        
        content_text = ""
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                content_text = " ".join([elem.get_text().strip() for elem in elements[:5]])
                break
        
        return {
            "url": url,
            "title": title_text,
            "content": content_text[:1000],  # 限制长度
            "status": "success"
        }
    except Exception as e:
        logger.error(f"URL解析失败: {e}")
        return {
            "url": url,
            "title": "解析失败",
            "content": f"无法解析URL内容: {str(e)}",
            "status": "error"
        }

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
        logger.error(f"聊天接口错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/with-attachments")
async def chat_with_attachments(
    message: str = Form(...),
    session_id: str = Form(None),
    user_id: str = Form(...),
    url_contents: str = Form(None),
    files: List[UploadFile] = File(default=[])
):
    """带附件的聊天接口"""
    try:
        # 处理文件附件
        file_contents = []
        if files:
            for file in files:
                if not file.filename or not is_allowed_file(file.filename):
                    raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file.filename}")
                
                # 保存文件
                file_id = str(uuid.uuid4())
                file_extension = Path(file.filename).suffix
                file_path = UPLOAD_DIR / f"{file_id}{file_extension}"
                
                # 读取文件内容并检查大小
                file_content = await file.read()
                if len(file_content) > MAX_FILE_SIZE:
                    raise HTTPException(status_code=400, detail=f"文件过大: {file.filename}")
                
                # 写入文件
                with open(file_path, "wb") as buffer:
                    buffer.write(file_content)
                
                # 提取文件内容
                content = ""
                if file_extension.lower() == '.pdf':
                    content = extract_text_from_pdf(file_path)
                elif file_extension.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
                    content = extract_text_from_image(file_path)
                elif file_extension.lower() == '.txt':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                
                file_contents.append({
                    "filename": file.filename,
                    "content": content,
                    "type": file.content_type
                })
        
        # 处理URL内容
        url_contents_list = []
        if url_contents:
            try:
                url_contents_list = json.loads(url_contents)
            except json.JSONDecodeError:
                pass
        
        # 构建增强的消息内容
        enhanced_message = message
        if file_contents:
            enhanced_message += "\n\n[附件内容]:\n"
            for file_content in file_contents:
                enhanced_message += f"\n文件: {file_content['filename']}\n内容: {file_content['content'][:500]}...\n"
        
        if url_contents_list:
            enhanced_message += "\n\n[URL内容]:\n"
            for url_content in url_contents_list:
                enhanced_message += f"\n链接: {url_content['url']}\n标题: {url_content['title']}\n内容: {url_content['content'][:500]}...\n"
        
        # 创建聊天请求
        chat_request = ChatRequest(
            message=enhanced_message,
            session_id=session_id,
            user_id=user_id
        )
        
        # 调用聊天引擎
        response = chat_engine.chat(chat_request)
        
        # 添加附件信息到响应
        response_dict = response.dict()
        response_dict["attachments"] = file_contents
        response_dict["url_contents"] = url_contents_list
        
        return response_dict
        
    except Exception as e:
        logger.error(f"带附件聊天接口错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/parse-url")
async def parse_url(data: dict):
    """URL解析接口"""
    try:
        url = data.get("url")
        if not url:
            raise HTTPException(status_code=400, detail="URL参数缺失")
        
        result = parse_url_content(url)
        return result
        
    except Exception as e:
        logger.error(f"URL解析接口错误: {e}")
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
        logger.error(f"获取会话摘要错误: {e}")
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
        logger.error(f"获取会话历史错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}/sessions")
async def get_user_sessions(user_id: str, limit: int = 50):
    """获取用户的所有会话列表"""
    try:
        from backend.database import DatabaseManager, ChatMessage
        with DatabaseManager() as db:
            sessions = db.get_user_sessions(user_id, limit)
            
            session_list = []
            for session in sessions:
                # 获取会话的第一条消息作为标题
                first_message = db.db.query(ChatMessage)\
                    .filter(ChatMessage.session_id == session.session_id)\
                    .filter(ChatMessage.role == 'user')\
                    .order_by(ChatMessage.created_at.asc())\
                    .first()
                
                title = first_message.content[:30] + "..." if first_message and len(first_message.content) > 30 else (first_message.content if first_message else "新对话")
                
                session_list.append({
                    "session_id": session.session_id,
                    "title": title,
                    "created_at": session.created_at.isoformat(),
                    "updated_at": session.updated_at.isoformat()
                })
            
            return {
                "user_id": user_id,
                "sessions": session_list
            }
    except Exception as e:
        logger.error(f"获取用户会话列表错误: {e}")
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
        logger.error(f"获取情感趋势错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """提交用户反馈"""
    try:
        from backend.database import DatabaseManager
        with DatabaseManager() as db:
            feedback = db.save_feedback(
                session_id=request.session_id,
                user_id=request.user_id or "anonymous",
                message_id=request.message_id,
                feedback_type=request.feedback_type,
                rating=request.rating,
                comment=request.comment or "",
                user_message=request.user_message or "",
                bot_response=request.bot_response or ""
            )
            
            return FeedbackResponse(
                feedback_id=feedback.id,
                session_id=feedback.session_id,
                feedback_type=feedback.feedback_type,
                rating=feedback.rating,
                created_at=feedback.created_at
            )
    except Exception as e:
        logger.error(f"提交反馈错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/feedback/statistics", response_model=FeedbackStatistics)
async def get_feedback_statistics():
    """获取反馈统计信息"""
    try:
        from backend.database import DatabaseManager
        with DatabaseManager() as db:
            stats = db.get_feedback_statistics()
            return FeedbackStatistics(**stats)
    except Exception as e:
        logger.error(f"获取反馈统计错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/feedback", response_model=FeedbackListResponse)
async def get_feedback_list(feedback_type: str = None, limit: int = 100):
    """获取反馈列表"""
    try:
        from backend.database import DatabaseManager
        with DatabaseManager() as db:
            feedbacks = db.get_all_feedback(feedback_type=feedback_type, limit=limit)
            
            feedback_list = [
                {
                    "id": f.id,
                    "session_id": f.session_id,
                    "user_id": f.user_id,
                    "message_id": f.message_id,
                    "feedback_type": f.feedback_type,
                    "rating": f.rating,
                    "comment": f.comment,
                    "user_message": f.user_message,
                    "bot_response": f.bot_response,
                    "created_at": f.created_at.isoformat(),
                    "is_resolved": f.is_resolved
                }
                for f in feedbacks
            ]
            
            return FeedbackListResponse(
                feedbacks=feedback_list,
                total=len(feedback_list)
            )
    except Exception as e:
        logger.error(f"获取反馈列表错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/feedback/session/{session_id}")
async def get_session_feedback(session_id: str):
    """获取特定会话的反馈"""
    try:
        from backend.database import DatabaseManager
        with DatabaseManager() as db:
            feedbacks = db.get_feedback_by_session(session_id)
            
            return {
                "session_id": session_id,
                "feedbacks": [
                    {
                        "id": f.id,
                        "feedback_type": f.feedback_type,
                        "rating": f.rating,
                        "comment": f.comment,
                        "created_at": f.created_at.isoformat()
                    }
                    for f in feedbacks
                ]
            }
    except Exception as e:
        logger.error(f"获取会话反馈错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/feedback/{feedback_id}/resolve")
async def resolve_feedback(feedback_id: int):
    """标记反馈已解决"""
    try:
        from backend.database import DatabaseManager
        with DatabaseManager() as db:
            feedback = db.mark_feedback_resolved(feedback_id)
            if not feedback:
                raise HTTPException(status_code=404, detail="反馈不存在")
            
            return {
                "message": "反馈已标记为已解决",
                "feedback_id": feedback_id
            }
    except Exception as e:
        logger.error(f"标记反馈已解决错误: {e}")
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
    print("📍 服务地址: http://localhost:8000")
    print("🔗 API文档: http://localhost:8000/docs")
    print("🗄️ 数据库: MySQL")
    print("🧠 向量数据库: Chroma")
    print("🤖 AI引擎: LangChain + OpenAI")
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
