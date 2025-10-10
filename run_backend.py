#!/usr/bin/env python3
"""
启动后端服务的脚本
"""
import uvicorn
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config

if __name__ == "__main__":
    print("🚀 启动情感聊天机器人后端服务...")
    print(f"📍 服务地址: http://{Config.HOST}:{Config.PORT}")
    print("🔗 API文档: http://localhost:8008/docs")
    
    uvicorn.run(
        "backend.main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG,
        log_level="info"
    )
