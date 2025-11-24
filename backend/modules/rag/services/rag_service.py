#!/usr/bin/env python3
"""
RAG服务层
负责检索增强生成的业务逻辑
"""

from typing import List, Dict, Any, Optional
import logging

# 使用兼容层处理 langchain 导入
from ..core.langchain_compat import Document

# 导入 LangChain (Python 3.10+, langchain 0.2.x+)
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from ..core.knowledge_base import KnowledgeBaseManager
from backend.logging_config import get_logger
from config import Config

logger = get_logger(__name__)


class RAGService:
    """RAG检索增强生成服务"""
    
    def __init__(self, kb_manager: Optional[KnowledgeBaseManager] = None):
        """
        初始化RAG服务
        
        Args:
            kb_manager: 知识库管理器实例
        """
        if kb_manager is None:
            kb_manager = KnowledgeBaseManager()
            # 尝试加载已存在的向量存储
            try:
                kb_manager.load_vectorstore()
            except Exception as e:
                logger.warning(f"加载向量存储失败，可能需要先初始化知识库: {e}")
        
        self.kb_manager = kb_manager
        self.llm = ChatOpenAI(
            api_key=Config.OPENAI_API_KEY,
            base_url=Config.API_BASE_URL,
            model=Config.DEFAULT_MODEL,
            temperature=0.7
        )
        
        # 心理健康专用prompt模板
        self.prompt_template = PromptTemplate(
            template="""你是"心语"，一个专业的心理健康陪伴机器人。你正在使用专业的心理学知识库来回答用户的问题。

参考知识：
{context}

用户问题：{question}

请基于上述专业知识，用温暖、共情和专业的语气回答用户。注意：
1. 优先使用知识库中的科学方法和技巧
2. 用通俗易懂的语言解释专业概念
3. 提供具体可操作的建议
4. 表达共情和支持
5. 如果知识库中有相关练习或技巧，详细说明步骤
6. 询问用户是否需要进一步的指导或陪伴

回答：""",
            input_variables=["context", "question"]
        )
        
        logger.info("RAG服务初始化完成")
    
    def create_qa_chain(self, search_k: int = 3) -> RetrievalQA:
        """
        创建QA链
        
        Args:
            search_k: 检索文档数量
            
        Returns:
            QA链实例
        """
        try:
            retriever = self.kb_manager.get_retriever(search_kwargs={"k": search_k})
            
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True,
                chain_type_kwargs={
                    "prompt": self.prompt_template
                }
            )
            
            logger.info(f"QA链创建成功，检索数量: {search_k}")
            return qa_chain
            
        except Exception as e:
            logger.error(f"创建QA链失败: {e}")
            raise
    
    def ask(self, question: str, search_k: int = 3) -> Dict[str, Any]:
        """
        向知识库提问
        
        Args:
            question: 用户问题
            search_k: 检索文档数量
            
        Returns:
            包含答案和来源的字典
        """
        try:
            logger.info(f"收到问题: {question[:50]}...")
            
            # 创建QA链
            qa_chain = self.create_qa_chain(search_k)
            
            # 执行查询
            result = qa_chain({"query": question})
            
            # 提取答案和来源
            answer = result["result"]
            source_documents = result.get("source_documents", [])
            
            # 整理来源信息
            sources = []
            for doc in source_documents:
                source_info = {
                    "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "metadata": doc.metadata
                }
                sources.append(source_info)
            
            logger.info(f"回答生成成功，使用了 {len(sources)} 个知识源")
            
            return {
                "answer": answer,
                "sources": sources,
                "question": question,
                "knowledge_count": len(sources)
            }
            
        except Exception as e:
            logger.error(f"回答问题失败: {e}")
            raise
    
    def search_knowledge(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        仅搜索知识库，不生成回答
        
        Args:
            query: 查询文本
            k: 返回结果数量
            
        Returns:
            搜索结果列表
        """
        try:
            logger.info(f"搜索知识库: {query[:50]}...")
            
            # 带评分的搜索
            results = self.kb_manager.search_with_score(query, k=k)
            
            # 整理结果
            formatted_results = []
            for doc, score in results:
                result = {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": float(score)
                }
                formatted_results.append(result)
            
            logger.info(f"搜索完成，返回 {len(formatted_results)} 个结果")
            return formatted_results
            
        except Exception as e:
            logger.error(f"搜索知识库失败: {e}")
            raise
    
    def ask_with_context(
        self,
        question: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        user_emotion: Optional[str] = None,
        search_k: int = 3
    ) -> Dict[str, Any]:
        """
        结合对话上下文和用户情绪的知识问答
        
        Args:
            question: 用户问题
            conversation_history: 对话历史
            user_emotion: 用户当前情绪
            search_k: 检索文档数量
            
        Returns:
            包含答案和来源的字典
        """
        try:
            logger.info(f"结合上下文回答问题: {question[:50]}...")
            
            # 先检索相关知识
            knowledge_docs = self.kb_manager.search_similar(question, k=search_k)
            
            # 构建增强的上下文
            knowledge_context = "\n\n".join([
                f"【知识{i+1}】{doc.page_content}"
                for i, doc in enumerate(knowledge_docs)
            ])
            
            # 构建对话历史上下文
            history_context = ""
            if conversation_history:
                recent_history = conversation_history[-3:]  # 只使用最近3轮对话
                history_lines = []
                for msg in recent_history:
                    role = "用户" if msg.get("role") == "user" else "心语"
                    content = msg.get("content", "")
                    history_lines.append(f"{role}: {content}")
                history_context = "\n".join(history_lines)
            
            # 构建情绪上下文
            emotion_context = f"用户当前情绪: {user_emotion}" if user_emotion else ""
            
            # 构建完整的prompt
            enhanced_prompt = f"""你是"心语"，一个专业的心理健康陪伴机器人。

{emotion_context}

最近对话：
{history_context}

参考的专业知识：
{knowledge_context}

用户当前问题：{question}

请基于上述专业知识和对话上下文，用温暖、共情和专业的语气回答用户。注意：
1. 考虑用户的情绪状态，给予适当的情感支持
2. 结合对话历史，提供连贯的回应
3. 优先使用知识库中的科学方法和技巧
4. 用通俗易懂的语言解释专业概念
5. 提供具体可操作的建议
6. 询问用户是否需要进一步的指导或陪伴

回答："""
            
            # 使用LLM生成回答
            response = self.llm.predict(enhanced_prompt)
            
            # 整理来源信息
            sources = []
            for doc in knowledge_docs:
                source_info = {
                    "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "metadata": doc.metadata
                }
                sources.append(source_info)
            
            logger.info(f"结合上下文的回答生成成功")
            
            return {
                "answer": response,
                "sources": sources,
                "question": question,
                "knowledge_count": len(sources),
                "used_emotion_context": user_emotion is not None,
                "used_history_context": conversation_history is not None
            }
            
        except Exception as e:
            logger.error(f"结合上下文回答失败: {e}")
            raise
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """
        获取知识库统计信息
        
        Returns:
            统计信息字典
        """
        try:
            return self.kb_manager.get_stats()
        except Exception as e:
            logger.error(f"获取知识库统计信息失败: {e}")
            return {"error": str(e)}
    
    def is_knowledge_available(self) -> bool:
        """
        检查知识库是否可用，如果不可用则尝试自动初始化
        
        Returns:
            是否可用
        """
        try:
            stats = self.kb_manager.get_stats()
            if stats.get("status") == "就绪" and stats.get("document_count", 0) > 0:
                return True
            
            # 如果知识库未初始化，尝试自动初始化
            logger.info("知识库未初始化，尝试自动加载示例知识...")
            try:
                from ..core.knowledge_base import PsychologyKnowledgeLoader
                loader = PsychologyKnowledgeLoader(self.kb_manager)
                loader.load_sample_knowledge()
                
                # 再次检查
                stats = self.kb_manager.get_stats()
                if stats.get("status") == "就绪" and stats.get("document_count", 0) > 0:
                    logger.info(f"知识库自动初始化成功，文档数: {stats.get('document_count', 0)}")
                    return True
                else:
                    logger.warning("知识库自动初始化后仍不可用")
                    return False
            except Exception as e:
                logger.warning(f"知识库自动初始化失败: {e}")
                return False
        except Exception as e:
            logger.error(f"检查知识库可用性时出错: {e}")
            return False


class RAGIntegrationService:
    """RAG集成服务 - 将RAG功能集成到心语机器人"""
    
    def __init__(self, rag_service: Optional[RAGService] = None):
        """
        初始化RAG集成服务
        
        Args:
            rag_service: RAG服务实例
        """
        self.rag_service = rag_service or RAGService()
        logger.info("RAG集成服务初始化完成")
    
    def should_use_rag(self, message: str, emotion: Optional[str] = None) -> bool:
        """
        判断是否应该使用RAG
        
        Args:
            message: 用户消息
            emotion: 用户情绪
            
        Returns:
            是否使用RAG
        """
        # 定义触发RAG的关键词
        rag_triggers = [
            "怎么办", "如何", "方法", "建议", "技巧", "练习",
            "失眠", "焦虑", "抑郁", "压力", "紧张", "担心", "害怕",
            "孤独", "悲伤", "愤怒", "烦躁", "疲惫", "无助",
            "正念", "冥想", "放松", "呼吸", "认知", "行为",
            "睡眠", "运动", "饮食", "关系", "工作", "学习"
        ]
        
        # 需要专业建议的情绪
        professional_emotions = [
            "焦虑", "抑郁", "压力大", "紧张", "恐惧", "悲伤", "愤怒"
        ]
        
        # 检查消息中是否包含触发词
        message_lower = message.lower()
        has_trigger = any(trigger in message_lower for trigger in rag_triggers)
        
        # 检查情绪是否需要专业建议
        needs_professional = emotion and any(prof in emotion for prof in professional_emotions)
        
        # 检查知识库是否可用
        rag_available = self.rag_service.is_knowledge_available()
        
        should_use = (has_trigger or needs_professional) and rag_available
        
        if should_use:
            logger.info(f"触发RAG: trigger={has_trigger}, emotion={needs_professional}")
        
        return should_use
    
    def enhance_response(
        self,
        message: str,
        emotion: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        增强回复 - 结合知识库生成更专业的回答
        
        Args:
            message: 用户消息
            emotion: 用户情绪
            conversation_history: 对话历史
            
        Returns:
            增强的回复字典
        """
        try:
            # 判断是否应该使用RAG
            if not self.should_use_rag(message, emotion):
                return {
                    "use_rag": False,
                    "reason": "当前对话不需要专业知识库支持"
                }
            
            # 使用RAG生成回答
            result = self.rag_service.ask_with_context(
                question=message,
                conversation_history=conversation_history,
                user_emotion=emotion,
                search_k=3
            )
            
            result["use_rag"] = True
            return result
            
        except Exception as e:
            logger.error(f"增强回复失败: {e}")
            return {
                "use_rag": False,
                "error": str(e)
            }


if __name__ == "__main__":
    # 测试代码
    print("初始化RAG服务...")
    rag_service = RAGService()
    
    print("\n知识库状态:")
    stats = rag_service.get_knowledge_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n测试问答:")
    question = "我最近总是失眠，怎么办？"
    print(f"问题: {question}")
    
    try:
        result = rag_service.ask(question)
        print(f"\n回答:\n{result['answer']}")
        print(f"\n使用了 {result['knowledge_count']} 个知识源")
        print("\n知识来源:")
        for i, source in enumerate(result['sources'], 1):
            print(f"\n来源{i}:")
            print(f"  主题: {source['metadata'].get('topic', '未知')}")
            print(f"  内容: {source['content']}")
    except Exception as e:
        print(f"错误: {e}")
        print("提示: 可能需要先初始化知识库")

