#!/usr/bin/env python3
"""
RAG效果对比演示
展示有无RAG知识库的回复差异
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from backend.services.rag_service import RAGService


def print_header():
    """打印标题"""
    print("\n" + "=" * 80)
    print(" 心语机器人 - RAG增强效果对比演示")
    print("=" * 80 + "\n")


def print_comparison(question: str, without_rag: str, with_rag: str):
    """打印对比结果"""
    print("┌" + "─" * 78 + "┐")
    print(f"│ 用户问题: {question:<65} │")
    print("├" + "─" * 78 + "┤")
    print("│" + " " * 78 + "│")
    print("│ ❌ 无RAG版本（通用回复）" + " " * 50 + "│")
    print("│" + " " * 78 + "│")
    
    # 分割并打印无RAG版本
    lines = without_rag.split('\n')
    for line in lines:
        if len(line) > 72:
            # 长行分割
            while len(line) > 72:
                print(f"│   {line[:72]:<72}   │")
                line = line[72:]
            if line:
                print(f"│   {line:<72}   │")
        else:
            print(f"│   {line:<72}   │")
    
    print("│" + " " * 78 + "│")
    print("├" + "─" * 78 + "┤")
    print("│" + " " * 78 + "│")
    print("│ ✅ RAG增强版本（专业建议 + 知识引用）" + " " * 41 + "│")
    print("│" + " " * 78 + "│")
    
    # 分割并打印RAG版本
    lines = with_rag.split('\n')
    for line in lines:
        if len(line) > 72:
            # 长行分割
            while len(line) > 72:
                print(f"│   {line[:72]:<72}   │")
                line = line[72:]
            if line:
                print(f"│   {line:<72}   │")
        else:
            print(f"│   {line:<72}   │")
    
    print("│" + " " * 78 + "│")
    print("└" + "─" * 78 + "┘")
    print()


def demo_case_1():
    """演示案例1：失眠问题"""
    question = "我最近总是失眠，怎么办？"
    
    without_rag = """你可以试试听听轻音乐、喝杯热牛奶，或者睡前不要玩手机。
保持规律作息也很重要。"""
    
    # 使用RAG获取专业回复
    try:
        rag_service = RAGService()
        result = rag_service.ask(question, search_k=2)
        with_rag = result['answer']
        
        # 如果回复太长，截取主要部分
        if len(with_rag) > 500:
            with_rag = with_rag[:500] + "\n\n[内容较长，已省略部分...]"
        
        with_rag += f"\n\n💡 [此回复基于 {result['knowledge_count']} 个专业知识源]"
        
    except Exception as e:
        with_rag = f"[RAG服务不可用: {e}]\n建议先运行: python init_rag_knowledge.py"
    
    print_comparison(question, without_rag, with_rag)


def demo_case_2():
    """演示案例2：焦虑应对"""
    question = "工作压力太大，很焦虑，怎么缓解？"
    
    without_rag = """我理解你的压力。可以试试深呼吸、运动、或者找朋友聊聊天。
适当休息也很重要，不要太勉强自己。"""
    
    try:
        rag_service = RAGService()
        result = rag_service.ask(question, search_k=2)
        with_rag = result['answer']
        
        if len(with_rag) > 500:
            with_rag = with_rag[:500] + "\n\n[内容较长，已省略部分...]"
        
        with_rag += f"\n\n💡 [此回复基于 {result['knowledge_count']} 个专业知识源]"
        
    except Exception as e:
        with_rag = f"[RAG服务不可用: {e}]"
    
    print_comparison(question, without_rag, with_rag)


def demo_case_3():
    """演示案例3：正念练习"""
    question = "什么是正念冥想？怎么练习？"
    
    without_rag = """正念冥想就是专注当下，观察自己的呼吸和感受。
可以每天花几分钟静坐，慢慢练习就会有效果。"""
    
    try:
        rag_service = RAGService()
        result = rag_service.ask(question, search_k=2)
        with_rag = result['answer']
        
        if len(with_rag) > 500:
            with_rag = with_rag[:500] + "\n\n[内容较长，已省略部分...]"
        
        with_rag += f"\n\n💡 [此回复基于 {result['knowledge_count']} 个专业知识源]"
        
    except Exception as e:
        with_rag = f"[RAG服务不可用: {e}]"
    
    print_comparison(question, without_rag, with_rag)


def print_summary():
    """打印总结"""
    print("\n" + "=" * 80)
    print(" 🎯 RAG增强的优势")
    print("=" * 80 + "\n")
    
    advantages = [
        ("✓ 专业性", "基于权威心理学知识，而非通用建议"),
        ("✓ 可操作性", "提供具体的步骤和方法，而非模糊的建议"),
        ("✓ 可信度", "引用知识来源，增强专业性和可信度"),
        ("✓ 科学性", "包含研究支持的方法和技巧"),
        ("✓ 个性化", "结合用户情绪和对话历史，生成定制化回答")
    ]
    
    for title, desc in advantages:
        print(f"  {title:<15} {desc}")
    
    print("\n" + "=" * 80 + "\n")
    
    print("📊 效果对比总结:\n")
    print("  • 无RAG: 通用的安慰和建议，缺乏专业性和可操作性")
    print("  • 有RAG: 专业的心理学知识 + 具体的实践方法 + 科学依据\n")
    
    print("🎯 结论:\n")
    print("  RAG技术让'心语'机器人从'情感倾听者'升级为'专业心理助手'，")
    print("  不仅能共情用户情绪，还能提供科学、专业、可操作的心理健康建议。\n")


def main():
    """主函数"""
    print_header()
    
    print("💡 提示: 如果看到 '[RAG服务不可用]'，请先运行: python init_rag_knowledge.py\n")
    
    print("\n" + "─" * 80)
    print(" 演示案例 1: 失眠问题")
    print("─" * 80)
    demo_case_1()
    
    print("\n" + "─" * 80)
    print(" 演示案例 2: 焦虑应对")
    print("─" * 80)
    demo_case_2()
    
    print("\n" + "─" * 80)
    print(" 演示案例 3: 正念练习")
    print("─" * 80)
    demo_case_3()
    
    print_summary()
    
    print("📝 后续步骤:\n")
    print("  1. 初始化知识库: python init_rag_knowledge.py")
    print("  2. 运行完整测试: python test_rag_system.py")
    print("  3. 启动API服务: python run_backend.py")
    print("  4. 查看详细文档: cat RAG_README.md")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 演示被用户中断")
    except Exception as e:
        print(f"\n\n✗ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

