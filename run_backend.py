#!/usr/bin/env python3
"""
启动后端服务的脚本
自动构建本地知识库并启动服务
"""
# 使用 SQLite3 兼容性模块（处理 Mac Python 3.10 兼容性问题）
import sys
import os
# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# SQLite3 兼容性设置
try:
    from backend.utils.sqlite_compat import setup_sqlite3
    setup_sqlite3()
except ImportError:
    pass  # 使用默认 sqlite3

import uvicorn
import os
import asyncio
from pathlib import Path

# 获取项目根目录和backend目录
project_root = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(project_root, "backend")

# 添加项目根目录到Python路径
sys.path.insert(0, project_root)

from config import Config

def setup_knowledge_base():
    """设置本地知识库"""
    print("📚 正在初始化本地知识库...")
    
    try:
        # 导入RAG相关模块
        from backend.modules.rag.core.knowledge_base import KnowledgeBaseManager, PsychologyKnowledgeLoader
        
        # 初始化知识库管理器
        kb_manager = KnowledgeBaseManager()
        
        # 检查知识库是否已存在
        stats = kb_manager.get_stats()
        if stats.get('status') == '就绪' and stats.get('document_count', 0) > 0:
            print("✓ 知识库已存在，跳过初始化")
            return True
        
        print("→ 加载内置示例知识...")
        loader = PsychologyKnowledgeLoader(kb_manager)
        loader.load_sample_knowledge()
        
        # 尝试从知识库结构加载
        print("→ 尝试从知识库结构加载...")
        try:
            loader.load_from_knowledge_base_structure()
            print("✓ 知识库结构加载成功")
        except Exception as e:
            print(f"⚠️ 知识库结构加载失败: {e}")
            print("继续使用内置示例知识")
        
        # 验证知识库状态
        final_stats = kb_manager.get_stats()
        print(f"✓ 知识库初始化完成")
        print(f"  文档数量: {final_stats.get('document_count', 0)}")
        print(f"  存储位置: {final_stats.get('persist_directory')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 知识库初始化失败: {e}")
        print("⚠️ 服务将启动，但RAG功能可能不可用")
        return False

def check_dependencies():
    """检查必要的依赖"""
    print("🔍 检查依赖...")
    
    missing_deps = []
    
    try:
        import chromadb
    except ImportError:
        missing_deps.append("chromadb")
    
    try:
        import langchain
    except ImportError:
        missing_deps.append("langchain")
    
    try:
        import openai
    except ImportError:
        missing_deps.append("openai")
    
    if missing_deps:
        print(f"⚠️ 缺少依赖: {', '.join(missing_deps)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("✓ 依赖检查通过")
    return True

if __name__ == "__main__":
    print("🚀 启动情感聊天机器人后端服务...")
    print(f"📍 服务地址: http://{Config.HOST}:{Config.PORT}")
    print("🔗 API文档: http://localhost:8000/docs")
    print(f"📂 工作目录: {project_root}")
    
    # 设置项目根目录的环境变量，供后续代码使用
    os.environ['PROJECT_ROOT'] = project_root
    
    # 禁用LangSmith追踪以避免403错误
    os.environ['LANGCHAIN_TRACING_V2'] = 'false'
    os.environ['LANGCHAIN_ENDPOINT'] = ''
    
    # 检查依赖
    if not check_dependencies():
        print("⚠️ 依赖检查失败，但继续启动服务")
    
    # 初始化知识库
    kb_success = setup_knowledge_base()
    
    if kb_success:
        print("✅ 本地知识库构建完成")
    else:
        print("⚠️ 本地知识库构建失败，RAG功能可能不可用")
    
    print("\n" + "="*60)
    print("🎉 服务启动中...")
    print("="*60)
    
    # 保持在项目根目录，使用backend.app应用工厂
    print(f"✓ 从项目根目录启动，使用backend.app应用工厂")
    
    # 为了彻底解决 watchfiles 频繁检测问题，完全禁用热重载
    print("🚀 启动模式：禁用热重载以避免文件监视问题")
    uvicorn.run(
        "backend.app:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=False,  # 完全禁用热重载
        log_level="info"
    )
