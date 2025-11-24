#!/usr/bin/env python3
"""
聊天相关路由
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
from backend.models import ChatRequest, ChatResponse
from backend.services.chat_service import ChatService
from backend.logging_config import get_logger
import json
from pathlib import Path
import uuid
import os
import sys
import PyPDF2
import requests
from bs4 import BeautifulSoup

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

router = APIRouter(prefix="/chat", tags=["聊天"])
logger = get_logger(__name__)

# 初始化服务
chat_service = ChatService()

# 文件存储配置
UPLOAD_DIR = Path(project_root) / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

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


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    聊天接口（启用记忆系统）
    """
    try:
        response = await chat_service.chat(request, use_memory_system=True)
        return response
    except Exception as e:
        logger.error(f"聊天接口错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simple", response_model=ChatResponse)
async def chat_simple(request: ChatRequest):
    """
    简单聊天接口（不使用记忆系统，用于对比）
    """
    try:
        response = await chat_service.chat(request, use_memory_system=False)
        return response
    except Exception as e:
        logger.error(f"简单聊天接口错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/summary")
async def get_session_summary(session_id: str):
    """获取会话摘要"""
    try:
        summary = await chat_service.get_session_summary(session_id)
        if "error" in summary:
            raise HTTPException(status_code=404, detail=summary["error"])
        return summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取会话摘要错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/history")
async def get_session_history(session_id: str, limit: int = 20):
    """获取会话历史"""
    try:
        history = await chat_service.get_session_history(session_id, limit)
        # 如果没有消息，返回空列表而不是404
        # 这样前端可以正常处理空会话的情况
        if not history.get("messages"):
            return {
                "session_id": session_id,
                "messages": []
            }
        return history
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取会话历史错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/sessions")
async def get_user_sessions(user_id: str, limit: int = 50):
    """获取用户的所有会话列表"""
    try:
        sessions = await chat_service.get_user_sessions(user_id, limit)
        return sessions
    except Exception as e:
        logger.error(f"获取用户会话列表错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/sessions/search")
async def search_user_sessions(user_id: str, keyword: str = "", limit: int = 50):
    """搜索用户会话"""
    try:
        result = await chat_service.search_user_sessions(user_id, keyword, limit)
        return result
    except Exception as e:
        logger.error(f"搜索用户会话错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/batch-delete")
async def delete_sessions_batch(session_ids: List[str]):
    """批量删除会话"""
    try:
        if not session_ids:
            raise HTTPException(status_code=400, detail="会话ID列表不能为空")
        
        result = await chat_service.delete_sessions_batch(session_ids)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量删除会话错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    try:
        success = await chat_service.delete_session(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        return {
            "message": "会话删除成功",
            "session_id": session_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除会话错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/emotion-trends")
async def get_user_emotion_trends(user_id: str):
    """获取用户情感趋势"""
    try:
        trends = await chat_service.get_user_emotion_trends(user_id)
        if "error" in trends:
            raise HTTPException(status_code=404, detail=trends["error"])
        return trends
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取情感趋势错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/with-attachments", response_model=ChatResponse)
async def chat_with_attachments(
    message: str = Form(...),
    session_id: str = Form(None),
    user_id: str = Form(...),
    url_contents: str = Form(None),
    files: List[UploadFile] = File(default=[])
):
    """带附件的聊天接口（支持文件上传）"""
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
                content_preview = file_content['content'][:500] if file_content['content'] else "[空内容]"
                enhanced_message += f"\n文件: {file_content['filename']}\n内容: {content_preview}...\n"
        
        if url_contents_list:
            enhanced_message += "\n\n[URL内容]:\n"
            for url_content in url_contents_list:
                content_preview = url_content.get('content', '')[:500]
                enhanced_message += f"\n链接: {url_content['url']}\n标题: {url_content['title']}\n内容: {content_preview}...\n"
        
        # 创建聊天请求
        chat_request = ChatRequest(
            message=enhanced_message,
            session_id=session_id,
            user_id=user_id
        )
        
        # 调用聊天服务
        response = await chat_service.chat(chat_request, use_memory_system=True)
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"带附件聊天接口错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/parse-url")
async def parse_url(data: dict):
    """URL解析接口"""
    try:
        url = data.get("url")
        if not url:
            raise HTTPException(status_code=400, detail="URL参数缺失")
        
        result = parse_url_content(url)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"URL解析接口错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

