#!/usr/bin/env python3
"""
RAG知识库初始化脚本
快速初始化心理健康知识库
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from backend.rag_knowledge_base import KnowledgeBaseManager, PsychologyKnowledgeLoader


def main():
    """初始化知识库"""
    print("\n" + "=" * 70)
    print(" 心语机器人 - RAG知识库初始化")
    print("=" * 70 + "\n")
    
    try:
        # 1. 创建知识库管理器
        print("→ 步骤 1/3: 初始化知识库管理器...")
        kb_manager = KnowledgeBaseManager()
        print("✓ 知识库管理器初始化成功\n")
        
        # 2. 加载示例知识
        print("→ 步骤 2/3: 加载心理健康知识...")
        print("  这可能需要几分钟，请耐心等待...\n")
        
        loader = PsychologyKnowledgeLoader(kb_manager)
        loader.load_sample_knowledge()
        
        print("✓ 心理健康知识加载成功\n")
        
        # 3. 验证知识库
        print("→ 步骤 3/3: 验证知识库...")
        stats = kb_manager.get_stats()
        
        print("✓ 知识库验证成功\n")
        print("-" * 70)
        print("知识库统计信息:")
        print(f"  状态: {stats.get('status')}")
        print(f"  文档数量: {stats.get('document_count')}")
        print(f"  存储位置: {stats.get('persist_directory')}")
        print(f"  嵌入模型: {stats.get('embedding_model')}")
        print("-" * 70)
        
        # 4. 测试检索
        print("\n→ 测试知识检索功能...")
        test_query = "失眠怎么办"
        results = kb_manager.search_similar(test_query, k=1)
        
        if results:
            print(f"✓ 检索测试成功 (查询: '{test_query}')")
            print(f"  找到 {len(results)} 个相关文档")
            print(f"  示例文档主题: {results[0].metadata.get('topic', '未知')}")
        else:
            print("⚠️ 检索测试返回空结果")
        
        print("\n" + "=" * 70)
        print("🎉 RAG知识库初始化完成！")
        print("=" * 70 + "\n")
        
        print("📝 后续步骤:")
        print("  1. 测试完整系统: python test_rag_system.py")
        print("  2. 启动API服务: python run_backend.py")
        print("  3. 访问API文档: http://localhost:8000/docs")
        print("  4. 测试RAG端点: http://localhost:8000/api/rag/test")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n✗ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n💡 故障排查建议:")
        print("  1. 确保已安装所有依赖: pip install -r requirements.txt")
        print("  2. 检查OpenAI API密钥是否正确配置")
        print("  3. 确保有足够的磁盘空间存储向量数据库")
        print("  4. 查看上方的详细错误信息")
        print()
        
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 初始化被用户中断")
        sys.exit(1)

