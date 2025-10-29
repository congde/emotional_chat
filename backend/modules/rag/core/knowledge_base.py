#!/usr/bin/env python3
"""
RAG知识库管理模块
负责心理健康知识文档的加载、处理、向量化和检索
"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from datetime import datetime

try:
    from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader, TextLoader
    from langchain_community.vectorstores import Chroma
except ImportError:
    # 兼容旧版本 langchain
    from langchain.document_loaders import PyPDFLoader, DirectoryLoader, TextLoader
    from langchain.vectorstores import Chroma

try:
    from langchain_openai import OpenAIEmbeddings
except ImportError:
    from langchain.embeddings import OpenAIEmbeddings

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from backend.logging_config import get_logger
from config import Config

logger = get_logger(__name__)


class KnowledgeBaseManager:
    """心理健康知识库管理器"""
    
    def __init__(self, persist_directory: str = "./chroma_db/psychology_kb"):
        """
        初始化知识库管理器
        
        Args:
            persist_directory: 向量数据库持久化目录
        """
        self.persist_directory = persist_directory
        # 暂时禁用嵌入功能，使用简单的文本匹配
        self.embeddings = None
        logger.info("暂时禁用嵌入功能，使用简单文本匹配")
        self.vectorstore: Optional[Chroma] = None
        
        # 确保目录存在
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        
        # 文档分块器配置
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", "；", ".", "!", "?", ";", " ", ""]
        )
        
        logger.info(f"知识库管理器初始化完成，持久化目录: {persist_directory}")
    
    def load_pdf_documents(self, pdf_path: str) -> List[Document]:
        """
        加载单个PDF文档
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            文档列表
        """
        try:
            logger.info(f"开始加载PDF文档: {pdf_path}")
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            logger.info(f"成功加载PDF文档，共 {len(documents)} 页")
            return documents
        except Exception as e:
            logger.error(f"加载PDF文档失败: {e}")
            raise
    
    def load_directory_documents(self, directory_path: str, glob_pattern: str = "**/*.pdf") -> List[Document]:
        """
        批量加载目录下的文档
        
        Args:
            directory_path: 目录路径
            glob_pattern: 文件匹配模式
            
        Returns:
            文档列表
        """
        try:
            logger.info(f"开始加载目录文档: {directory_path}, 模式: {glob_pattern}")
            loader = DirectoryLoader(
                directory_path,
                glob=glob_pattern,
                loader_cls=PyPDFLoader,
                show_progress=True
            )
            documents = loader.load()
            logger.info(f"成功加载目录文档，共 {len(documents)} 页")
            return documents
        except Exception as e:
            logger.error(f"加载目录文档失败: {e}")
            raise
    
    def load_text_documents(self, text_path: str) -> List[Document]:
        """
        加载文本文档
        
        Args:
            text_path: 文本文件路径
            
        Returns:
            文档列表
        """
        try:
            logger.info(f"开始加载文本文档: {text_path}")
            loader = TextLoader(text_path, encoding='utf-8')
            documents = loader.load()
            logger.info(f"成功加载文本文档")
            return documents
        except Exception as e:
            logger.error(f"加载文本文档失败: {e}")
            raise
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        分割文档为小块
        
        Args:
            documents: 原始文档列表
            
        Returns:
            分割后的文档块列表
        """
        try:
            logger.info(f"开始分割文档，共 {len(documents)} 个文档")
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"文档分割完成，共 {len(chunks)} 个文档块")
            return chunks
        except Exception as e:
            logger.error(f"文档分割失败: {e}")
            raise
    
    def create_vectorstore(self, chunks: List[Document]) -> Chroma:
        """
        创建向量存储
        
        Args:
            chunks: 文档块列表
            
        Returns:
            向量存储实例
        """
        try:
            logger.info(f"开始创建向量存储，共 {len(chunks)} 个文档块")
            
            # 为每个文档块添加元数据
            for i, chunk in enumerate(chunks):
                if 'chunk_id' not in chunk.metadata:
                    chunk.metadata['chunk_id'] = i
                if 'timestamp' not in chunk.metadata:
                    chunk.metadata['timestamp'] = datetime.now().isoformat()
            
            # 如果没有嵌入函数，使用简单的文本存储
            if self.embeddings is None:
                logger.info("使用简单文本存储模式")
                # 创建一个简单的文本存储，不使用向量
                self.vectorstore = None
                self.text_storage = chunks  # 直接存储文本块
                logger.info("文本存储创建完成")
                return None
            else:
                vectorstore = Chroma.from_documents(
                    documents=chunks,
                    embedding=self.embeddings,
                    persist_directory=self.persist_directory
                )
                vectorstore.persist()
                
                self.vectorstore = vectorstore
                logger.info("向量存储创建完成并持久化")
                return vectorstore
        except Exception as e:
            logger.error(f"创建向量存储失败: {e}")
            raise
    
    def load_vectorstore(self) -> Chroma:
        """
        加载已存在的向量存储
        
        Returns:
            向量存储实例
        """
        try:
            logger.info(f"从 {self.persist_directory} 加载向量存储")
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            logger.info("向量存储加载成功")
            return self.vectorstore
        except Exception as e:
            logger.error(f"加载向量存储失败: {e}")
            raise
    
    def add_documents(self, documents: List[Document]) -> None:
        """
        向现有向量存储添加文档
        
        Args:
            documents: 新文档列表
        """
        try:
            if self.vectorstore is None:
                logger.warning("向量存储未初始化，尝试加载...")
                try:
                    self.load_vectorstore()
                except:
                    logger.info("向量存储不存在，创建新的向量存储")
                    self.create_vectorstore(documents)
                    return
            
            logger.info(f"向向量存储添加 {len(documents)} 个文档")
            
            # 分割文档
            chunks = self.split_documents(documents)
            
            # 添加元数据
            for i, chunk in enumerate(chunks):
                chunk.metadata['timestamp'] = datetime.now().isoformat()
            
            # 添加到向量存储
            self.vectorstore.add_documents(chunks)
            self.vectorstore.persist()
            
            logger.info("文档添加完成并持久化")
        except Exception as e:
            logger.error(f"添加文档失败: {e}")
            raise
    
    def search_similar(self, query: str, k: int = 3) -> List[Document]:
        """
        相似度搜索
        
        Args:
            query: 查询文本
            k: 返回结果数量
            
        Returns:
            相似文档列表
        """
        try:
            # 如果使用简单文本存储
            if self.embeddings is None and hasattr(self, 'text_storage'):
                logger.info(f"使用简单文本搜索: {query[:50]}...")
                # 简单的关键词匹配
                query_lower = query.lower()
                results = []
                for doc in self.text_storage:
                    if query_lower in doc.page_content.lower():
                        results.append(doc)
                        if len(results) >= k:
                            break
                logger.info(f"简单搜索完成，返回 {len(results)} 个结果")
                return results
            
            # 使用向量搜索
            if self.vectorstore is None:
                logger.info("向量存储未加载，尝试加载...")
                self.load_vectorstore()
            
            logger.info(f"执行相似度搜索: {query[:50]}...")
            results = self.vectorstore.similarity_search(query, k=k)
            logger.info(f"搜索完成，返回 {len(results)} 个结果")
            return results
        except Exception as e:
            logger.error(f"相似度搜索失败: {e}")
            raise
    
    def search_with_score(self, query: str, k: int = 3) -> List[tuple]:
        """
        带评分的相似度搜索
        
        Args:
            query: 查询文本
            k: 返回结果数量
            
        Returns:
            (文档, 相似度分数)元组列表
        """
        try:
            if self.vectorstore is None:
                logger.info("向量存储未加载，尝试加载...")
                self.load_vectorstore()
            
            logger.info(f"执行带评分的相似度搜索: {query[:50]}...")
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            logger.info(f"搜索完成，返回 {len(results)} 个结果")
            return results
        except Exception as e:
            logger.error(f"带评分的相似度搜索失败: {e}")
            raise
    
    def get_retriever(self, search_kwargs: Optional[Dict[str, Any]] = None):
        """
        获取检索器
        
        Args:
            search_kwargs: 搜索参数
            
        Returns:
            检索器实例
        """
        try:
            if self.vectorstore is None:
                logger.info("向量存储未加载，尝试加载...")
                self.load_vectorstore()
            
            if search_kwargs is None:
                search_kwargs = {"k": 3}
            
            retriever = self.vectorstore.as_retriever(search_kwargs=search_kwargs)
            logger.info("检索器获取成功")
            return retriever
        except Exception as e:
            logger.error(f"获取检索器失败: {e}")
            raise
    
    def delete_collection(self) -> None:
        """删除整个向量集合"""
        try:
            if self.vectorstore is not None:
                self.vectorstore.delete_collection()
                self.vectorstore = None
                logger.info("向量集合已删除")
        except Exception as e:
            logger.error(f"删除向量集合失败: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取知识库统计信息
        
        Returns:
            统计信息字典
        """
        try:
            if self.vectorstore is None:
                return {
                    "status": "未初始化",
                    "document_count": 0
                }
            
            # 获取集合信息
            collection = self.vectorstore._collection
            count = collection.count() if collection else 0
            
            return {
                "status": "就绪",
                "document_count": count,
                "persist_directory": self.persist_directory,
                "embedding_model": "OpenAI Ada-002"
            }
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {
                "status": "错误",
                "error": str(e)
            }


class PsychologyKnowledgeLoader:
    """心理健康知识加载器"""
    
    def __init__(self, kb_manager: KnowledgeBaseManager):
        """
        初始化知识加载器
        
        Args:
            kb_manager: 知识库管理器实例
        """
        self.kb_manager = kb_manager
        logger.info("心理健康知识加载器初始化完成")
    
    def load_sample_knowledge(self) -> None:
        """
        加载示例心理健康知识
        （当没有PDF文档时，使用预设的文本知识）
        """
        sample_texts = [
            """
            认知行为疗法（CBT）基础知识
            
            认知行为疗法是一种广泛应用的心理治疗方法，主要帮助人们识别和改变不良的思维模式和行为习惯。
            
            核心原理：
            1. 思维影响情绪：我们的想法会直接影响我们的感受
            2. 行为影响情绪：我们的行为方式也会影响我们的心理状态
            3. 三者互相影响：思维、情绪和行为形成一个循环系统
            
            常见应用场景：
            - 焦虑症：通过识别灾难化思维，学习更现实的思考方式
            - 抑郁症：挑战消极自动思维，培养更积极的认知模式
            - 失眠：建立健康的睡眠习惯和认知
            """,
            
            """
            正念减压技术（MBSR）
            
            正念减压是一种基于冥想的压力管理方法，由Jon Kabat-Zinn博士在1970年代开发。
            
            核心练习：
            
            1. 身体扫描练习
            - 平躺或坐下，保持舒适姿势
            - 将注意力依次集中在身体各个部位
            - 从脚趾开始，逐步向上：脚掌、小腿、大腿、腹部、胸部、手臂、头部
            - 观察每个部位的感觉，不做评判
            - 如果感到紧张，想象呼吸流经该部位，帮助放松
            
            2. 正念呼吸
            - 将注意力集中在呼吸上
            - 观察每一次吸气和呼气
            - 当思绪飘走时，温和地将注意力带回呼吸
            
            3. 正念行走
            - 缓慢行走，注意每一步的感觉
            - 感受脚与地面的接触
            - 观察身体的移动
            
            研究表明，持续8周的正念练习可以显著改善：
            - 失眠问题
            - 焦虑症状
            - 抑郁情绪
            - 慢性疼痛
            - 压力水平
            """,
            
            """
            积极心理学实践技巧
            
            积极心理学关注人类的积极品质和幸福感的提升。
            
            实用技巧：
            
            1. 感恩练习
            - 每天记录3件感恩的事情
            - 可以是小事：一杯热茶、朋友的微笑、阳光明媚
            - 研究显示，持续感恩练习可提升整体幸福感
            
            2. 优势识别
            - 识别自己的性格优势（如创造力、善良、勇气等）
            - 每天找机会运用一项优势
            - 在工作和生活中发挥优势可增强成就感
            
            3. 积极体验品味
            - 有意识地延长积极体验的时间
            - 与他人分享快乐时刻
            - 回忆美好记忆
            
            4. 成长型思维
            - 将挑战视为成长机会
            - 相信能力可以通过努力提升
            - 从失败中学习，而非被失败定义
            """,
            
            """
            应对焦虑的具体策略
            
            焦虑是一种常见的情绪体验，但过度焦虑会影响生活质量。
            
            有效应对方法：
            
            1. 深呼吸技术（4-7-8呼吸法）
            - 吸气4秒
            - 屏住呼吸7秒
            - 呼气8秒
            - 重复4次
            - 可快速激活副交感神经系统，降低焦虑
            
            2. 渐进式肌肉放松
            - 依次收紧和放松各肌肉群
            - 从脚部开始，逐步向上
            - 每个部位收紧5秒，然后放松10秒
            - 帮助识别和释放身体紧张
            
            3. 认知重构
            - 识别焦虑想法："我肯定会搞砸"
            - 挑战这个想法：有什么证据支持或反对？
            - 形成更平衡的想法："我准备充分了，会尽力而为"
            
            4. 问题解决技能
            - 明确问题
            - 列出可能的解决方案
            - 评估每个方案的优劣
            - 选择并实施最佳方案
            - 评估结果并调整
            
            5. 规律运动
            - 每周至少150分钟中等强度运动
            - 运动可以降低压力激素，提升内啡肽
            - 快走、游泳、瑜伽都是好选择
            """,
            
            """
            改善睡眠的科学方法
            
            良好的睡眠对心理健康至关重要。
            
            睡眠卫生建议：
            
            1. 规律作息
            - 每天同一时间起床和睡觉
            - 包括周末也要保持一致
            - 帮助调节生物钟
            
            2. 睡前仪式
            - 睡前1小时开始放松活动
            - 避免电子屏幕（蓝光影响褪黑素分泌）
            - 可以做：阅读、听轻音乐、泡热水澡
            
            3. 卧室环境优化
            - 保持凉爽（18-20°C最佳）
            - 确保黑暗和安静
            - 床只用于睡眠和亲密行为
            
            4. 处理睡前思绪
            - 如果20分钟内睡不着，起床去另一个房间
            - 做些安静的活动，直到感到困倦
            - 将担忧写在纸上，明天再处理
            
            5. 白天习惯
            - 每天暴露于自然光下
            - 限制咖啡因（下午2点后避免）
            - 规律运动但不要太晚（睡前3小时）
            - 午睡不超过20分钟
            
            6. 正念身体扫描
            - 平躺在床上
            - 从脚趾开始，依次关注身体各部位
            - 想象每次呼吸都带来放松
            - 这种方法在临床研究中显著改善失眠
            """,
            
            """
            建立心理韧性的方法
            
            心理韧性是从困难和压力中恢复的能力。
            
            培养韧性的策略：
            
            1. 建立支持网络
            - 培养亲密关系
            - 加入兴趣小组或社区
            - 在需要时寻求帮助
            
            2. 接纳变化
            - 理解变化是生活的常态
            - 关注可控的事情
            - 灵活调整目标和期望
            
            3. 采取行动
            - 将大问题分解为小步骤
            - 每天朝目标前进一点
            - 庆祝小胜利
            
            4. 保持希望
            - 相信困难会过去
            - 想象积极的未来
            - 从过去的困难中汲取力量
            
            5. 自我关怀
            - 像对待朋友一样对待自己
            - 接纳不完美
            - 在困难时给自己温暖和理解
            """
        ]
        
        try:
            logger.info("开始加载示例心理健康知识")
            
            # 创建Document对象
            documents = []
            for i, text in enumerate(sample_texts):
                doc = Document(
                    page_content=text.strip(),
                    metadata={
                        "source": "内置知识库",
                        "topic": self._extract_topic(text),
                        "doc_id": i,
                        "timestamp": datetime.now().isoformat()
                    }
                )
                documents.append(doc)
            
            # 分割文档
            chunks = self.kb_manager.split_documents(documents)
            
            # 创建向量存储
            self.kb_manager.create_vectorstore(chunks)
            
            logger.info(f"成功加载 {len(documents)} 个示例知识文档，共 {len(chunks)} 个文档块")
            
        except Exception as e:
            logger.error(f"加载示例知识失败: {e}")
            raise
    
    def _extract_topic(self, text: str) -> str:
        """从文本中提取主题"""
        lines = text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith(' '):
                return line
        return "未知主题"
    
    def load_from_pdf(self, pdf_path: str) -> None:
        """
        从PDF文件加载知识
        
        Args:
            pdf_path: PDF文件路径
        """
        try:
            logger.info(f"从PDF加载知识: {pdf_path}")
            
            # 加载PDF
            documents = self.kb_manager.load_pdf_documents(pdf_path)
            
            # 添加到知识库
            self.kb_manager.add_documents(documents)
            
            logger.info(f"成功从PDF加载知识: {pdf_path}")
            
        except Exception as e:
            logger.error(f"从PDF加载知识失败: {e}")
            raise
    
    def load_from_directory(self, directory_path: str) -> None:
        """
        从目录批量加载知识
        
        Args:
            directory_path: 目录路径
        """
        try:
            logger.info(f"从目录批量加载知识: {directory_path}")
            
            # 加载目录下的所有PDF
            documents = self.kb_manager.load_directory_documents(directory_path)
            
            # 分割并创建向量存储
            chunks = self.kb_manager.split_documents(documents)
            self.kb_manager.create_vectorstore(chunks)
            
            logger.info(f"成功从目录加载知识: {directory_path}")
            
        except Exception as e:
            logger.error(f"从目录加载知识失败: {e}")
            raise
    
    def load_from_knowledge_base_structure(self, base_path: str = "./knowledge_base") -> None:
        """
        从标准知识库结构加载知识
        
        Args:
            base_path: 知识库根目录路径
        """
        try:
            logger.info(f"从标准知识库结构加载知识: {base_path}")
            
            all_documents = []
            
            # 定义知识库结构
            knowledge_structure = {
                "clinical_guidelines": "临床指南",
                "therapy_methods": "治疗方法", 
                "self_help_tools": "自助工具",
                "organization_policy": "机构政策"
            }
            
            for folder, category in knowledge_structure.items():
                folder_path = os.path.join(base_path, folder)
                if os.path.exists(folder_path):
                    logger.info(f"加载 {category} 知识: {folder_path}")
                    
                    # 加载该目录下的所有文档
                    try:
                        docs = self.kb_manager.load_directory_documents(
                            folder_path, 
                            glob_pattern="**/*"
                        )
                        
                        # 为每个文档添加分类元数据
                        for doc in docs:
                            doc.metadata.update({
                                "category": category,
                                "folder": folder,
                                "source": "知识库文件"
                            })
                        
                        all_documents.extend(docs)
                        logger.info(f"成功加载 {category} 知识，共 {len(docs)} 个文档")
                        
                    except Exception as e:
                        logger.warning(f"加载 {category} 知识失败: {e}")
                        continue
                else:
                    logger.warning(f"知识库目录不存在: {folder_path}")
            
            if all_documents:
                # 分割文档
                chunks = self.kb_manager.split_documents(all_documents)
                
                # 创建向量存储
                self.kb_manager.create_vectorstore(chunks)
                
                logger.info(f"成功从知识库结构加载知识，共 {len(all_documents)} 个文档，{len(chunks)} 个文档块")
            else:
                logger.warning("未找到任何知识库文档")
                
        except Exception as e:
            logger.error(f"从知识库结构加载知识失败: {e}")
            raise


if __name__ == "__main__":
    # 测试代码
    print("初始化知识库管理器...")
    kb_manager = KnowledgeBaseManager()
    
    print("加载示例知识...")
    loader = PsychologyKnowledgeLoader(kb_manager)
    loader.load_sample_knowledge()
    
    print("\n知识库统计信息:")
    stats = kb_manager.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n测试检索功能:")
    query = "我最近总是失眠，怎么办？"
    print(f"查询: {query}")
    results = kb_manager.search_similar(query, k=2)
    print(f"\n找到 {len(results)} 个相关文档:")
    for i, doc in enumerate(results, 1):
        print(f"\n--- 结果 {i} ---")
        print(f"来源: {doc.metadata.get('source', '未知')}")
        print(f"主题: {doc.metadata.get('topic', '未知')}")
        print(f"内容预览: {doc.page_content[:200]}...")

