#!/usr/bin/env python3
"""
流式聊天路由
实现流式响应和实时交互功能
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.requests import Request
from typing import Dict, List, Optional, Any
import asyncio
import json
import time
from datetime import datetime

from backend.services.optimized_chat_service import optimized_chat_service
from backend.logging_config import get_logger

logger = get_logger(__name__)

# 创建路由器
router = APIRouter(prefix="/streaming", tags=["流式聊天"])


@router.post("/chat")
async def streaming_chat(request: Dict[str, Any]):
    """
    流式聊天接口
    
    Args:
        request: 聊天请求，包含message、session_id、user_id等
        
    Returns:
        流式响应，使用Server-Sent Events格式
    """
    try:
        # 验证请求参数
        if not request.get("message"):
            raise HTTPException(status_code=400, detail="消息内容不能为空")
        
        # 使用优化的聊天服务进行流式处理
        return await optimized_chat_service.chat_streaming(request)
        
    except Exception as e:
        logger.error(f"流式聊天失败: {e}")
        
        # 返回错误流
        async def error_stream():
            yield f"data: {json.dumps({'error': str(e), 'type': 'error'})}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            error_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )


@router.post("/chat/with-metadata")
async def streaming_chat_with_metadata(request: Dict[str, Any]):
    """
    带元数据的流式聊天
    
    Args:
        request: 聊天请求，包含消息和元数据
        
    Returns:
        包含元数据的流式响应
    """
    try:
        user_input = request.get("message", "")
        session_id = request.get("session_id", "default")
        user_id = request.get("user_id", "anonymous")
        metadata = request.get("metadata", {})
        
        # 添加请求时间戳
        request_time = datetime.now().isoformat()
        
        async def enhanced_stream():
            # 发送开始信号
            yield f"data: {json.dumps({'type': 'start', 'timestamp': request_time})}\n\n"
            
            # 发送处理状态
            yield f"data: {json.dumps({'type': 'processing', 'message': '正在分析您的消息...'})}\n\n"
            
            # 并行处理用户输入
            processing_result = await optimized_chat_service._parallel_process_input(user_input)
            
            # 发送处理结果
            yield f"data: {json.dumps({'type': 'analysis', 'emotion': processing_result.get('emotion'), 'processing_time': processing_result.get('processing_time')})}\n\n"
            
            # 构建优化的Prompt
            prompt = await optimized_chat_service._build_optimized_prompt(user_input, processing_result)
            
            # 发送生成开始信号
            yield f"data: {json.dumps({'type': 'generating', 'message': '正在生成回复...'})}\n\n"
            
            # 流式生成响应
            response_text = ""
            async for chunk in optimized_chat_service.performance_optimizer.stream_response(prompt, optimized_chat_service.llm_client):
                if chunk.startswith("data: "):
                    token = chunk[6:].strip()
                    if token and token != "[DONE]":
                        response_text += token
                        yield f"data: {json.dumps({'type': 'token', 'content': token, 'position': len(response_text)})}\n\n"
            
            # 发送完成信号
            yield f"data: {json.dumps({'type': 'complete', 'full_response': response_text, 'metadata': metadata})}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            enhanced_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
                "X-Content-Type-Options": "nosniff"
            }
        )
        
    except Exception as e:
        logger.error(f"带元数据的流式聊天失败: {e}")
        
        async def error_stream():
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            error_stream(),
            media_type="text/event-stream"
        )


@router.get("/status")
async def get_streaming_status():
    """
    获取流式服务状态
    
    Returns:
        流式服务状态信息
    """
    try:
        from backend.services.performance_optimizer import stream_handler
        
        active_streams = stream_handler.get_active_streams()
        
        return {
            "status": "active",
            "active_streams": len(active_streams),
            "streams": active_streams,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取流式状态失败: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.post("/test")
async def test_streaming():
    """
    测试流式响应
    
    Returns:
        测试流式响应
    """
    async def test_stream():
        messages = [
            "正在连接...",
            "分析您的请求...",
            "检索相关信息...",
            "生成回复中...",
            "完成！"
        ]
        
        for i, message in enumerate(messages):
            yield f"data: {json.dumps({'step': i+1, 'total': len(messages), 'message': message})}\n\n"
            await asyncio.sleep(0.5)  # 模拟处理时间
        
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        test_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )


@router.websocket("/ws")
async def websocket_chat(websocket):
    """
    WebSocket流式聊天
    
    Args:
        websocket: WebSocket连接
    """
    try:
        await websocket.accept()
        
        while True:
            # 接收消息
            data = await websocket.receive_text()
            request = json.loads(data)
            
            user_input = request.get("message", "")
            if not user_input:
                await websocket.send_text(json.dumps({"error": "消息不能为空"}))
                continue
            
            # 发送开始信号
            await websocket.send_text(json.dumps({
                "type": "start",
                "timestamp": datetime.now().isoformat()
            }))
            
            # 处理请求
            try:
                # 并行处理
                processing_result = await optimized_chat_service._parallel_process_input(user_input)
                
                # 发送分析结果
                await websocket.send_text(json.dumps({
                    "type": "analysis",
                    "emotion": processing_result.get("emotion"),
                    "processing_time": processing_result.get("processing_time")
                }))
                
                # 生成响应
                prompt = await optimized_chat_service._build_optimized_prompt(user_input, processing_result)
                response = await optimized_chat_service._generate_response_optimized(prompt)
                
                # 发送完整响应
                await websocket.send_text(json.dumps({
                    "type": "response",
                    "content": response,
                    "timestamp": datetime.now().isoformat()
                }))
                
            except Exception as e:
                logger.error(f"WebSocket聊天处理失败: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": str(e)
                }))
    
    except Exception as e:
        logger.error(f"WebSocket连接失败: {e}")
        try:
            await websocket.close()
        except:
            pass


@router.get("/")
async def streaming_info():
    """
    流式服务信息
    
    Returns:
        流式服务相关信息
    """
    return {
        "service": "流式聊天服务",
        "version": "1.0.0",
        "features": [
            "Server-Sent Events (SSE)",
            "WebSocket支持",
            "实时元数据",
            "性能优化",
            "错误处理"
        ],
        "endpoints": {
            "POST /streaming/chat": "基础流式聊天",
            "POST /streaming/chat/with-metadata": "带元数据的流式聊天",
            "GET /streaming/status": "流式服务状态",
            "POST /streaming/test": "测试流式响应",
            "WS /streaming/ws": "WebSocket聊天"
        },
        "timestamp": datetime.now().isoformat()
    }
