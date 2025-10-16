#!/usr/bin/env python3
"""
RAG系统测试脚本
测试心理健康知识库的各项功能
"""

import sys
import os
import asyncio
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from backend.rag_knowledge_base import KnowledgeBaseManager, PsychologyKnowledgeLoader
from backend.services.rag_service import RAGService, RAGIntegrationService


def print_section(title: str):
    """打印章节标题"""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70 + "\n")


def print_subsection(title: str):
    """打印子标题"""
    print("\n" + "-" * 60)
    print(f" {title}")
    print("-" * 60 + "\n")


def test_knowledge_base_manager():
    """测试知识库管理器"""
    print_section("1. 测试知识库管理器")
    
    try:
        # 初始化知识库管理器
        print("→ 初始化知识库管理器...")
        kb_manager = KnowledgeBaseManager()
        print("✓ 知识库管理器初始化成功")
        
        # 加载示例知识
        print("\n→ 加载示例心理健康知识...")
        loader = PsychologyKnowledgeLoader(kb_manager)
        loader.load_sample_knowledge()
        print("✓ 示例知识加载成功")
        
        # 获取统计信息
        print("\n→ 获取知识库统计信息...")
        stats = kb_manager.get_stats()
        print("✓ 统计信息:")
        for key, value in stats.items():
            print(f"  • {key}: {value}")
        
        return kb_manager, True
        
    except Exception as e:
        print(f"✗ 知识库管理器测试失败: {e}")
        return None, False


def test_similarity_search(kb_manager: KnowledgeBaseManager):
    """测试相似度搜索"""
    print_section("2. 测试相似度搜索")
    
    test_queries = [
        "我最近总是失眠，怎么办？",
        "感到焦虑不安，有什么缓解方法？",
        "如何进行正念冥想？",
        "情绪低落时怎么办？"
    ]
    
    try:
        for i, query in enumerate(test_queries, 1):
            print_subsection(f"查询 {i}: {query}")
            
            # 执行搜索
            results = kb_manager.search_with_score(query, k=2)
            
            print(f"找到 {len(results)} 个相关文档:\n")
            
            for j, (doc, score) in enumerate(results, 1):
                print(f"【结果 {j}】相似度: {score:.4f}")
                print(f"主题: {doc.metadata.get('topic', '未知')}")
                print(f"来源: {doc.metadata.get('source', '未知')}")
                print(f"内容预览: {doc.page_content[:150]}...")
                print()
        
        print("✓ 相似度搜索测试成功")
        return True
        
    except Exception as e:
        print(f"✗ 相似度搜索测试失败: {e}")
        return False


def test_rag_qa(kb_manager: KnowledgeBaseManager):
    """测试RAG问答"""
    print_section("3. 测试RAG问答功能")
    
    try:
        # 初始化RAG服务
        print("→ 初始化RAG服务...")
        rag_service = RAGService(kb_manager)
        print("✓ RAG服务初始化成功")
        
        # 测试问题
        test_questions = [
            {
                "question": "我最近总是失眠，有什么具体的方法可以帮助我入睡？",
                "category": "睡眠问题"
            },
            {
                "question": "工作压力太大，感觉很焦虑，怎么办？",
                "category": "焦虑应对"
            }
        ]
        
        for i, test_case in enumerate(test_questions, 1):
            print_subsection(f"问题 {i} ({test_case['category']})")
            print(f"用户: {test_case['question']}\n")
            
            # 执行问答
            result = rag_service.ask(test_case['question'], search_k=2)
            
            print("心语回答:")
            print(result['answer'])
            
            print(f"\n使用了 {result['knowledge_count']} 个知识源:")
            for j, source in enumerate(result['sources'], 1):
                print(f"\n  【来源 {j}】")
                print(f"  主题: {source['metadata'].get('topic', '未知')}")
                print(f"  内容: {source['content'][:100]}...")
            
            print("\n" + "-" * 60)
        
        print("\n✓ RAG问答测试成功")
        return rag_service, True
        
    except Exception as e:
        print(f"✗ RAG问答测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None, False


def test_rag_with_context(rag_service: RAGService):
    """测试带上下文的RAG问答"""
    print_section("4. 测试带上下文的RAG问答")
    
    try:
        # 模拟对话历史
        conversation_history = [
            {"role": "user", "content": "我最近工作压力很大"},
            {"role": "assistant", "content": "我理解你现在承受着很大的工作压力。这种情况很常见，让我们一起来看看如何应对。"},
            {"role": "user", "content": "晚上经常睡不着，一直在想工作的事情"}
        ]
        
        question = "有什么方法可以让我晚上睡得更好吗？"
        emotion = "焦虑"
        
        print(f"【对话场景】")
        print("对话历史:")
        for msg in conversation_history:
            role = "用户" if msg["role"] == "user" else "心语"
            print(f"  {role}: {msg['content']}")
        
        print(f"\n当前用户情绪: {emotion}")
        print(f"当前问题: {question}\n")
        
        # 执行带上下文的问答
        result = rag_service.ask_with_context(
            question=question,
            conversation_history=conversation_history,
            user_emotion=emotion,
            search_k=3
        )
        
        print("心语回答:")
        print(result['answer'])
        
        print(f"\n使用了 {result['knowledge_count']} 个知识源")
        print(f"使用了情绪上下文: {result['used_emotion_context']}")
        print(f"使用了对话历史: {result['used_history_context']}")
        
        print("\n✓ 带上下文的RAG问答测试成功")
        return True
        
    except Exception as e:
        print(f"✗ 带上下文的RAG问答测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rag_integration():
    """测试RAG集成服务"""
    print_section("5. 测试RAG集成服务")
    
    try:
        # 初始化集成服务
        print("→ 初始化RAG集成服务...")
        integration_service = RAGIntegrationService()
        print("✓ RAG集成服务初始化成功")
        
        # 测试不同类型的消息
        test_cases = [
            {
                "message": "今天天气真好",
                "emotion": "开心",
                "expected_rag": False,
                "reason": "日常对话，不需要专业知识"
            },
            {
                "message": "我最近总是失眠，怎么办？",
                "emotion": "焦虑",
                "expected_rag": True,
                "reason": "睡眠问题，需要专业建议"
            },
            {
                "message": "感觉压力好大，有什么放松的方法吗？",
                "emotion": "压力大",
                "expected_rag": True,
                "reason": "压力管理，需要专业技巧"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print_subsection(f"测试用例 {i}")
            print(f"消息: {test_case['message']}")
            print(f"情绪: {test_case['emotion']}")
            print(f"预期使用RAG: {test_case['expected_rag']}")
            print(f"原因: {test_case['reason']}\n")
            
            # 判断是否应该使用RAG
            should_use = integration_service.should_use_rag(
                test_case['message'],
                test_case['emotion']
            )
            
            result_icon = "✓" if should_use == test_case['expected_rag'] else "✗"
            print(f"{result_icon} 实际使用RAG: {should_use}")
            
            if should_use:
                # 尝试增强回复
                enhanced = integration_service.enhance_response(
                    message=test_case['message'],
                    emotion=test_case['emotion']
                )
                
                if enhanced.get('use_rag'):
                    print(f"✓ 成功生成RAG增强回复")
                    print(f"  回复预览: {enhanced['answer'][:100]}...")
            
            print()
        
        print("✓ RAG集成服务测试成功")
        return True
        
    except Exception as e:
        print(f"✗ RAG集成服务测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_complete_workflow():
    """测试完整工作流程"""
    print_section("6. 完整工作流程演示")
    
    try:
        print("【场景】用户寻求失眠帮助的完整对话\n")
        
        # 初始化服务
        rag_service = RAGService()
        
        # 模拟多轮对话
        conversations = [
            {
                "round": 1,
                "user": "我最近总是失眠，很痛苦",
                "emotion": "焦虑",
                "history": []
            },
            {
                "round": 2,
                "user": "具体应该怎么做呢？能详细说说吗？",
                "emotion": "期待",
                "history": [
                    {"role": "user", "content": "我最近总是失眠，很痛苦"},
                    {"role": "assistant", "content": "我理解你的困扰..."}
                ]
            }
        ]
        
        for conv in conversations:
            print(f"【第 {conv['round']} 轮对话】")
            print(f"用户 ({conv['emotion']}): {conv['user']}\n")
            
            result = rag_service.ask_with_context(
                question=conv['user'],
                conversation_history=conv['history'],
                user_emotion=conv['emotion'],
                search_k=2
            )
            
            print(f"心语: {result['answer']}\n")
            print(f"[使用了 {result['knowledge_count']} 个专业知识源]\n")
            print("-" * 60 + "\n")
        
        print("✓ 完整工作流程测试成功")
        return True
        
    except Exception as e:
        print(f"✗ 完整工作流程测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_summary(results: dict):
    """打印测试摘要"""
    print_section("测试摘要")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    print(f"总测试数: {total}")
    print(f"通过: {passed} ✓")
    print(f"失败: {failed} ✗")
    print(f"成功率: {passed/total*100:.1f}%\n")
    
    print("详细结果:")
    for test_name, result in results.items():
        icon = "✓" if result else "✗"
        status = "通过" if result else "失败"
        print(f"  {icon} {test_name}: {status}")
    
    print("\n" + "=" * 70)
    
    if failed == 0:
        print("\n🎉 所有测试通过！RAG系统运行正常。\n")
    else:
        print(f"\n⚠️ 有 {failed} 个测试失败，请检查日志。\n")


def main():
    """主测试函数"""
    print("\n" + "=" * 70)
    print(" 心语机器人 - RAG知识库系统测试")
    print(" 测试时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 70)
    
    results = {}
    
    # 1. 测试知识库管理器
    kb_manager, success = test_knowledge_base_manager()
    results["知识库管理器"] = success
    
    if not success:
        print("\n⚠️ 知识库管理器初始化失败，后续测试无法继续")
        print_summary(results)
        return
    
    # 2. 测试相似度搜索
    success = test_similarity_search(kb_manager)
    results["相似度搜索"] = success
    
    # 3. 测试RAG问答
    rag_service, success = test_rag_qa(kb_manager)
    results["RAG问答"] = success
    
    # 4. 测试带上下文的RAG问答
    if rag_service:
        success = test_rag_with_context(rag_service)
        results["带上下文RAG问答"] = success
    else:
        results["带上下文RAG问答"] = False
    
    # 5. 测试RAG集成服务
    success = test_rag_integration()
    results["RAG集成服务"] = success
    
    # 6. 测试完整工作流程
    success = test_complete_workflow()
    results["完整工作流程"] = success
    
    # 打印摘要
    print_summary(results)
    
    # 提示后续步骤
    print("\n📝 后续步骤:")
    print("  1. 运行 API 服务器: python run_backend.py")
    print("  2. 访问 API 文档: http://localhost:8000/docs")
    print("  3. 测试 RAG API:")
    print("     - GET  /api/rag/status     # 查看知识库状态")
    print("     - POST /api/rag/init/sample # 初始化示例知识")
    print("     - POST /api/rag/ask        # 向知识库提问")
    print("     - POST /api/rag/ask/context # 带上下文提问")
    print("     - GET  /api/rag/examples   # 查看示例问题")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"\n\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

