#!/usr/bin/env python3
"""
测试知识库结构功能
验证从knowledge_base目录加载知识的功能
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from backend.modules.rag.core.knowledge_base import KnowledgeBaseManager, PsychologyKnowledgeLoader


def test_knowledge_base_structure():
    """测试知识库结构加载功能"""
    print("\n" + "=" * 70)
    print(" 心语机器人 - 知识库结构测试")
    print("=" * 70 + "\n")
    
    try:
        # 1. 检查知识库目录结构
        print("→ 步骤 1/4: 检查知识库目录结构...")
        knowledge_base_path = "./knowledge_base"
        
        if not os.path.exists(knowledge_base_path):
            print("❌ 知识库目录不存在，请先创建目录结构")
            return False
        
        # 检查各个子目录
        subdirs = ["clinical_guidelines", "therapy_methods", "self_help_tools", "organization_policy"]
        for subdir in subdirs:
            subdir_path = os.path.join(knowledge_base_path, subdir)
            if os.path.exists(subdir_path):
                files = os.listdir(subdir_path)
                print(f"✓ {subdir}: {len(files)} 个文件")
                for file in files:
                    print(f"  - {file}")
            else:
                print(f"⚠️ {subdir}: 目录不存在")
        
        print("✓ 知识库目录结构检查完成\n")
        
        # 2. 初始化知识库管理器
        print("→ 步骤 2/4: 初始化知识库管理器...")
        kb_manager = KnowledgeBaseManager()
        print("✓ 知识库管理器初始化成功\n")
        
        # 3. 从知识库结构加载知识
        print("→ 步骤 3/4: 从知识库结构加载知识...")
        print("  这可能需要几分钟，请耐心等待...\n")
        
        loader = PsychologyKnowledgeLoader(kb_manager)
        loader.load_from_knowledge_base_structure()
        
        print("✓ 知识库结构加载成功\n")
        
        # 4. 验证知识库
        print("→ 步骤 4/4: 验证知识库...")
        stats = kb_manager.get_stats()
        
        print("✓ 知识库验证成功\n")
        print("-" * 70)
        print("知识库统计信息:")
        print(f"  状态: {stats.get('status')}")
        print(f"  文档数量: {stats.get('document_count')}")
        print(f"  存储位置: {stats.get('persist_directory')}")
        print(f"  嵌入模型: {stats.get('embedding_model')}")
        print("-" * 70)
        
        # 5. 测试检索功能
        print("\n→ 测试知识检索功能...")
        test_queries = [
            "焦虑障碍的诊断标准",
            "CBT工作表的五要素",
            "正念身体扫描练习",
            "危机干预的标准流程"
        ]
        
        for query in test_queries:
            print(f"\n查询: '{query}'")
            results = kb_manager.search_similar(query, k=2)
            
            if results:
                print(f"✓ 找到 {len(results)} 个相关文档:")
                for i, doc in enumerate(results, 1):
                    print(f"\n--- 结果 {i} ---")
                    print(f"来源: {doc.metadata.get('source', '未知')}")
                    print(f"分类: {doc.metadata.get('category', '未知')}")
                    print(f"文件夹: {doc.metadata.get('folder', '未知')}")
                    print(f"内容预览: {doc.page_content[:150]}...")
            else:
                print("⚠️ 未找到相关文档")
        
        print("\n" + "=" * 70)
        print("🎉 知识库结构测试完成！")
        print("=" * 70 + "\n")
        
        print("📝 后续步骤:")
        print("  1. 启动API服务: python run_backend.py")
        print("  2. 测试新API端点: curl -X POST http://localhost:8000/api/rag/init/knowledge-base")
        print("  3. 查看API文档: http://localhost:8000/docs")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n💡 故障排查建议:")
        print("  1. 确保knowledge_base目录存在")
        print("  2. 检查目录下是否有文档文件")
        print("  3. 确保已安装所有依赖")
        print("  4. 查看上方的详细错误信息")
        print()
        
        return False


def check_directory_structure():
    """检查目录结构"""
    print("检查知识库目录结构...")
    
    knowledge_base_path = "./knowledge_base"
    if not os.path.exists(knowledge_base_path):
        print("❌ knowledge_base目录不存在")
        return False
    
    subdirs = ["clinical_guidelines", "therapy_methods", "self_help_tools", "organization_policy"]
    all_exist = True
    
    for subdir in subdirs:
        subdir_path = os.path.join(knowledge_base_path, subdir)
        if os.path.exists(subdir_path):
            files = os.listdir(subdir_path)
            print(f"✓ {subdir}: {len(files)} 个文件")
            if files:
                for file in files:
                    print(f"  - {file}")
            else:
                print(f"  (空目录)")
        else:
            print(f"❌ {subdir}: 目录不存在")
            all_exist = False
    
    return all_exist


if __name__ == "__main__":
    try:
        # 先检查目录结构
        if not check_directory_structure():
            print("\n请先创建知识库目录结构，然后重新运行测试")
            sys.exit(1)
        
        # 运行测试
        success = test_knowledge_base_structure()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
        sys.exit(1)
