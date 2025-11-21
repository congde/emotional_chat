#!/usr/bin/env python3
"""
快速启动脚本
自动完成数据库初始化、RAG知识库初始化，并启动服务
"""

# 使用pysqlite3替代系统sqlite3以支持ChromaDB
import pysqlite3 as sqlite3
import sys
sys.modules['sqlite3'] = sqlite3

import os
import subprocess
import time
from pathlib import Path

# 获取项目根目录
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from config import Config


def print_header(title):
    """打印标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def check_dependencies():
    """检查依赖"""
    print_header("检查依赖")
    
    missing = []
    required_packages = [
        "fastapi", "uvicorn", "sqlalchemy", "alembic",
        "langchain", "chromadb", "openai"
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - 缺失")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  缺少依赖: {', '.join(missing)}")
        print("💡 运行: pip install -r requirements.txt")
        response = input("是否现在安装依赖? (y/n): ")
        if response.lower() == 'y':
            subprocess.run(["pip", "install", "-r", "requirements.txt"])
        else:
            print("⚠️  继续启动，但可能遇到错误")
    
    return len(missing) == 0


def init_database():
    """初始化数据库"""
    print_header("初始化数据库")
    
    try:
        print("→ 检查数据库连接...")
        result = subprocess.run(
            ["python", "db_manager.py", "check"],
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        if result.returncode != 0:
            print("⚠️  数据库连接失败，请检查配置")
            print("💡 确保MySQL服务运行，并检查config.env配置")
            return False
        
        print("→ 升级数据库到最新版本...")
        result = subprocess.run(
            ["python", "db_manager.py", "upgrade"],
            cwd=project_root
        )
        
        if result.returncode == 0:
            print("✓ 数据库初始化完成")
            return True
        else:
            print("⚠️  数据库初始化失败，但继续启动")
            return False
            
    except Exception as e:
        print(f"⚠️  数据库初始化出错: {e}")
        return False


def init_rag_knowledge():
    """初始化RAG知识库"""
    print_header("初始化RAG知识库")
    
    try:
        print("→ 检查知识库状态...")
        
        # 导入RAG模块
        from backend.modules.rag.core.knowledge_base import KnowledgeBaseManager, PsychologyKnowledgeLoader
        
        kb_manager = KnowledgeBaseManager()
        stats = kb_manager.get_stats()
        
        if stats.get('status') == '就绪' and stats.get('document_count', 0) > 0:
            print("✓ 知识库已存在，跳过初始化")
            print(f"  文档数量: {stats.get('document_count', 0)}")
            return True
        
        print("→ 加载心理健康知识...")
        print("  这可能需要几分钟，请耐心等待...")
        
        loader = PsychologyKnowledgeLoader(kb_manager)
        loader.load_sample_knowledge()
        
        # 尝试从知识库结构加载
        try:
            loader.load_from_knowledge_base_structure()
            print("✓ 知识库结构加载成功")
        except Exception as e:
            print(f"⚠️ 知识库结构加载失败: {e}")
            print("继续使用内置示例知识")
        
        # 验证
        final_stats = kb_manager.get_stats()
        print(f"✓ RAG知识库初始化完成")
        print(f"  文档数量: {final_stats.get('document_count', 0)}")
        print(f"  存储位置: {final_stats.get('persist_directory')}")
        
        return True
        
    except Exception as e:
        print(f"⚠️  RAG知识库初始化失败: {e}")
        print("服务将启动，但RAG功能可能不可用")
        return False


def start_backend():
    """启动后端服务"""
    print_header("启动后端服务")
    
    print(f"📍 服务地址: http://{Config.HOST}:{Config.PORT}")
    print("🔗 API文档: http://localhost:{}/docs".format(Config.PORT))
    print("\n💡 提示: 按 Ctrl+C 停止服务")
    print("=" * 70 + "\n")
    
    # 设置环境变量
    os.environ['PROJECT_ROOT'] = project_root
    os.environ['LANGCHAIN_TRACING_V2'] = 'false'
    os.environ['LANGCHAIN_ENDPOINT'] = ''
    
    # 导入并启动
    import uvicorn
    uvicorn.run(
        "backend.app:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=False,
        log_level="info"
    )


def main():
    """主函数"""
    print_header("心语情感陪伴机器人 - 快速启动")
    
    print("本脚本将自动完成以下步骤:")
    print("  1. 检查依赖")
    print("  2. 初始化数据库")
    print("  3. 初始化RAG知识库")
    print("  4. 启动后端服务")
    print()
    
    # 询问是否跳过某些步骤
    skip_db = input("是否跳过数据库初始化? (y/n, 默认n): ").lower() == 'y'
    skip_rag = input("是否跳过RAG知识库初始化? (y/n, 默认n): ").lower() == 'y'
    
    # 1. 检查依赖
    check_dependencies()
    time.sleep(1)
    
    # 2. 初始化数据库
    if not skip_db:
        init_database()
        time.sleep(1)
    else:
        print("\n⏭️  跳过数据库初始化")
    
    # 3. 初始化RAG知识库
    if not skip_rag:
        init_rag_knowledge()
        time.sleep(1)
    else:
        print("\n⏭️  跳过RAG知识库初始化")
    
    # 4. 启动服务
    print_header("准备启动服务")
    print("✅ 所有初始化步骤完成")
    time.sleep(2)
    
    try:
        start_backend()
    except KeyboardInterrupt:
        print("\n\n⚠️  服务已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

