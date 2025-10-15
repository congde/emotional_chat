#!/usr/bin/env python3
"""
启动后端服务的脚本
"""
import uvicorn
import sys
import os

# 获取项目根目录和backend目录
project_root = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(project_root, "backend")

# 添加项目根目录到Python路径
sys.path.insert(0, project_root)

from config import Config

if __name__ == "__main__":
    print("🚀 启动情感聊天机器人后端服务...")
    print(f"📍 服务地址: http://{Config.HOST}:{Config.PORT}")
    print("🔗 API文档: http://localhost:8000/docs")
    print(f"📂 工作目录: {project_root}")
    
    # 设置项目根目录的环境变量，供后续代码使用
    os.environ['PROJECT_ROOT'] = project_root
    
    # 保持在项目根目录，使用backend.main模块路径
    print(f"✓ 从项目根目录启动，监视backend目录的变化")
    
    uvicorn.run(
        "backend.app:app",  # 使用新的app.py模块
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG,
        reload_dirs=[backend_dir],  # 只监视backend目录的变化
        log_level="info"
    )
