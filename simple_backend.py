#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版后端服务
适用于 Python 3.6 环境，不依赖 ChromaDB
"""

import os
import sys
import logging
from pathlib import Path

# 设置环境变量
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def create_simple_app():
    """创建简化的 FastAPI 应用"""
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.middleware.cors import CORSMiddleware
        from pydantic import BaseModel
        from typing import Optional, Dict, Any
        
        # 创建 FastAPI 应用
        app = FastAPI(
            title="情感聊天机器人API (简化版)",
            description="基于关键词情感分析的聊天机器人",
            version="1.0.0"
        )
        
        # 添加CORS中间件
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # 请求/响应模型
        class ChatRequest(BaseModel):
            message: str
            user_id: Optional[str] = None
            session_id: Optional[str] = None
        
        class ChatResponse(BaseModel):
            response: str
            emotion: Optional[str] = None
            confidence: Optional[float] = None
            intensity: Optional[float] = None
            suggestions: Optional[list] = None
        
        class EmotionAnalysisRequest(BaseModel):
            text: str
            user_id: Optional[str] = None
        
        class EmotionAnalysisResponse(BaseModel):
            emotion: str
            confidence: float
            intensity: float
            polarity: int
            keywords: list
            suggestions: list
            method: str
        
        # 初始化情感分析器
        try:
            from backend.services.advanced_sentiment_analyzer import get_analyzer
            sentiment_analyzer = get_analyzer(use_transformers=False)
            logger.info("✓ 情感分析器初始化成功")
        except Exception as e:
            logger.error(f"情感分析器初始化失败: {e}")
            sentiment_analyzer = None
        
        @app.get("/")
        async def root():
            """根路径"""
            return {
                "message": "情感聊天机器人API (简化版)",
                "version": "1.0.0",
                "status": "running",
                "features": [
                    "情感分析",
                    "聊天对话",
                    "情绪趋势分析"
                ]
            }
        
        @app.get("/health")
        async def health_check():
            """健康检查"""
            return {
                "status": "healthy",
                "sentiment_analyzer": "available" if sentiment_analyzer else "unavailable"
            }
        
        @app.post("/api/chat", response_model=ChatResponse)
        async def chat(request: ChatRequest):
            """聊天接口"""
            try:
                message = request.message.strip()
                if not message:
                    raise HTTPException(status_code=400, detail="消息不能为空")
                
                # 情感分析
                emotion_result = None
                if sentiment_analyzer:
                    try:
                        emotion_result = sentiment_analyzer.analyze(message, request.user_id)
                    except Exception as e:
                        logger.warning(f"情感分析失败: {e}")
                
                # 简单的回复逻辑
                if emotion_result:
                    emotion = emotion_result.get("emotion", "neutral")
                    suggestions = emotion_result.get("suggestions", [])
                    
                    # 根据情绪生成回复
                    if emotion == "happy":
                        response = "很高兴看到你这么开心！有什么特别的事情想要分享吗？"
                    elif emotion == "sad":
                        response = "我理解你现在的心情，每个人都会有难过的时刻。可以告诉我发生了什么吗？"
                    elif emotion == "anxious":
                        response = "焦虑确实让人感到不安，让我们一起面对它。可以告诉我你在担心什么吗？"
                    elif emotion == "angry":
                        response = "我能感受到你的愤怒，让我们先深呼吸一下。是什么事情让你感到愤怒？"
                    elif emotion == "lonely":
                        response = "孤独的感觉确实不好受，但你并不孤单，我在这里。"
                    elif emotion == "grateful":
                        response = "感恩的心很美好，感谢你愿意分享这份美好。"
                    else:
                        response = suggestions[0] if suggestions else "我在这里倾听，无论你想说什么都可以。"
                else:
                    response = "你好！我是你的情感陪伴机器人，有什么想聊的吗？"
                
                return ChatResponse(
                    response=response,
                    emotion=emotion_result.get("emotion") if emotion_result else None,
                    confidence=emotion_result.get("confidence") if emotion_result else None,
                    intensity=emotion_result.get("intensity") if emotion_result else None,
                    suggestions=emotion_result.get("suggestions") if emotion_result else None
                )
                
            except Exception as e:
                logger.error(f"聊天处理失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.post("/api/emotion/analyze", response_model=EmotionAnalysisResponse)
        async def analyze_emotion(request: EmotionAnalysisRequest):
            """情感分析接口"""
            try:
                if not sentiment_analyzer:
                    raise HTTPException(status_code=503, detail="情感分析器不可用")
                
                text = request.text.strip()
                if not text:
                    raise HTTPException(status_code=400, detail="文本不能为空")
                
                result = sentiment_analyzer.analyze(text, request.user_id)
                
                return EmotionAnalysisResponse(
                    emotion=result["emotion"],
                    confidence=result["confidence"],
                    intensity=result["intensity"],
                    polarity=result["polarity"],
                    keywords=result["keywords"],
                    suggestions=result["suggestions"],
                    method=result["method"]
                )
                
            except Exception as e:
                logger.error(f"情感分析失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/api/emotion/trend/{user_id}")
        async def get_emotion_trend(user_id: str):
            """获取情绪趋势"""
            try:
                if not sentiment_analyzer:
                    raise HTTPException(status_code=503, detail="情感分析器不可用")
                
                trend = sentiment_analyzer.get_emotion_trend(user_id)
                return trend
                
            except Exception as e:
                logger.error(f"情绪趋势分析失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        return app
        
    except ImportError as e:
        logger.error(f"导入依赖失败: {e}")
        raise

def main():
    """主函数"""
    try:
        logger.info("🚀 启动简化版情感聊天机器人后端服务...")
        logger.info("📍 服务地址: http://0.0.0.0:8000")
        logger.info("🔗 API文档: http://localhost:8000/docs")
        
        # 创建应用
        app = create_simple_app()
        
        # 启动服务
        import uvicorn
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
