#!/usr/bin/env python3
"""
RAG分块策略选择器
根据文档类型和特征自动选择最佳分块策略
"""

import re
from typing import List, Dict, Any, Optional

from .langchain_compat import Document, RecursiveCharacterTextSplitter
from .chunking_strategies import (
    CharacterTextSplitter,
    SentenceTextSplitter,
    MarkdownStructureSplitter,
    DialogueSplitter,
    SmallBigChunking,
    ParentChildChunking
)
from backend.logging_config import get_logger

logger = get_logger(__name__)


class ChunkingStrategySelector:
    """分块策略选择器"""
    
    def __init__(
        self,
        default_strategy: str = "auto",
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ):
        """
        初始化策略选择器
        
        Args:
            default_strategy: 默认策略（auto/recursive/structure/sentence/small_big/parent_child）
            chunk_size: 默认块大小
            chunk_overlap: 默认重叠大小
        """
        self.default_strategy = default_strategy
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # 初始化各种分块器
        self._initialize_splitters()
    
    def _initialize_splitters(self):
        """初始化各种分块器实例"""
        self.splitters = {
            "character": CharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            ),
            "sentence": SentenceTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            ),
            "recursive": RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                separators=["\n\n", "\n", "。", "！", "？", "；", ".", "!", "?", ";", " ", ""]
            ),
            "structure": MarkdownStructureSplitter(
                chunk_size=int(self.chunk_size * 1.8),  # 结构感知可以稍大
                min_chunk=int(self.chunk_size * 0.5),
                overlap_ratio=self.chunk_overlap / self.chunk_size if self.chunk_size > 0 else 0.1
            ),
            "dialogue": DialogueSplitter(
                max_turns=10,
                max_chars=self.chunk_size * 2,
                overlap_turns=2
            ),
            "small_big": SmallBigChunking(
                small_chunk_size=int(self.chunk_size * 0.4),
                big_chunk_size=int(self.chunk_size * 1.8),
                small_overlap=int(self.chunk_overlap * 0.5),
                big_overlap=self.chunk_overlap
            ),
            "parent_child": ParentChildChunking(
                parent_chunk_size=int(self.chunk_size * 2),
                child_chunk_size=int(self.chunk_size * 0.6),
                parent_overlap=self.chunk_overlap * 2,
                child_overlap=int(self.chunk_overlap * 0.5)
            )
        }
    
    def detect_document_type(self, text: str) -> Dict[str, Any]:
        """
        检测文档类型和特征
        
        Args:
            text: 文档文本
            
        Returns:
            文档特征字典
        """
        features = {
            "is_markdown": False,
            "is_dialogue": False,
            "has_structure": False,
            "avg_sentence_length": 0,
            "paragraph_count": 0,
            "heading_count": 0
        }
        
        # 检测Markdown
        markdown_patterns = [
            r'^#{1,6}\s+',  # 标题
            r'```',  # 代码块
            r'^\s*[-*+]\s+',  # 列表
            r'^\s*\d+\.\s+',  # 有序列表
        ]
        markdown_score = sum(
            1 for pattern in markdown_patterns
            if re.search(pattern, text, re.MULTILINE)
        )
        features["is_markdown"] = markdown_score >= 2
        
        # 检测标题
        heading_pattern = re.compile(r'^#{1,6}\s+', re.MULTILINE)
        headings = heading_pattern.findall(text)
        features["heading_count"] = len(headings)
        features["has_structure"] = len(headings) >= 2
        
        # 检测对话
        dialogue_pattern = re.compile(
            r'^(?:User|用户|Assistant|助手|AI|机器人|问|答)[:：]\s*',
            re.MULTILINE
        )
        dialogue_matches = dialogue_pattern.findall(text)
        features["is_dialogue"] = len(dialogue_matches) >= 3
        
        # 计算平均句子长度
        sentences = re.split(r'[。！？；\n]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        if sentences:
            features["avg_sentence_length"] = sum(len(s) for s in sentences) / len(sentences)
        
        # 段落数
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        features["paragraph_count"] = len(paragraphs)
        
        return features
    
    def select_strategy(
        self,
        documents: Optional[List[Document]] = None,
        text: Optional[str] = None,
        strategy: Optional[str] = None
    ) -> str:
        """
        选择分块策略
        
        Args:
            documents: 文档列表（可选）
            text: 文档文本（可选）
            strategy: 手动指定的策略（可选）
            
        Returns:
            策略名称
        """
        # 如果手动指定了策略，直接返回
        if strategy and strategy != "auto":
            if strategy in self.splitters:
                logger.info(f"使用手动指定的策略: {strategy}")
                return strategy
            else:
                logger.warning(f"未知策略 {strategy}，回退到auto")
        
        # 如果没有文档和文本，使用默认策略
        if not documents and not text:
            logger.info(f"使用默认策略: {self.default_strategy}")
            return self.default_strategy if self.default_strategy != "auto" else "recursive"
        
        # 获取文档文本
        if not text:
            if documents:
                text = "\n\n".join([doc.page_content for doc in documents])
            else:
                text = ""
        
        if not text:
            return "recursive"
        
        # 检测文档特征
        features = self.detect_document_type(text)
        logger.info(f"文档特征: {features}")
        
        # 根据特征选择策略
        if features["is_dialogue"]:
            logger.info("检测到对话格式，使用dialogue策略")
            return "dialogue"
        
        if features["is_markdown"] and features["has_structure"]:
            logger.info("检测到Markdown结构化文档，使用structure策略")
            return "structure"
        
        if features["paragraph_count"] > 10 and features["has_structure"]:
            logger.info("检测到长文档且有结构，使用parent_child策略")
            return "parent_child"
        
        if features["avg_sentence_length"] > 100:
            # 长句子，使用句子分块
            logger.info("检测到长句子，使用sentence策略")
            return "sentence"
        
        # 默认使用递归分块
        logger.info("使用默认recursive策略")
        return "recursive"
    
    def get_splitter(self, strategy: Optional[str] = None) -> Any:
        """
        获取分块器实例
        
        Args:
            strategy: 策略名称，如果为None则自动选择
            
        Returns:
            分块器实例
        """
        if strategy is None:
            strategy = self.select_strategy()
        
        if strategy not in self.splitters:
            logger.warning(f"策略 {strategy} 不存在，使用recursive")
            strategy = "recursive"
        
        return self.splitters[strategy]
    
    def split_documents(
        self,
        documents: List[Document],
        strategy: Optional[str] = None
    ) -> List[Document]:
        """
        分割文档列表
        
        Args:
            documents: 文档列表
            strategy: 策略名称，如果为None则自动选择
            
        Returns:
            分割后的文档块列表
        """
        # 选择策略
        selected_strategy = strategy or self.select_strategy(documents=documents)
        
        # 获取分块器
        splitter = self.get_splitter(selected_strategy)
        
        # 执行分块
        logger.info(f"使用策略 {selected_strategy} 分割 {len(documents)} 个文档")
        chunks = splitter.split_documents(documents)
        logger.info(f"分割完成，共生成 {len(chunks)} 个文档块")
        
        return chunks

