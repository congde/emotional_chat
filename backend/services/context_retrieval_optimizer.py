#!/usr/bin/env python3
"""
上下文检索优化器
基于 Manus 的实践：优先使用文件系统工具（glob、grep）而非向量索引
适用于瞬时会话场景
"""

from typing import Dict, List, Optional, Any
import os
import re
from pathlib import Path
import subprocess


class FileSystemRetriever:
    """基于文件系统的上下文检索器"""
    
    def __init__(self, base_dir: str = "./context_storage"):
        """
        初始化文件系统检索器
        
        Args:
            base_dir: 基础目录
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def glob_search(self, pattern: str, directory: Optional[str] = None) -> List[str]:
        """
        使用glob模式搜索文件
        
        Args:
            pattern: glob模式（如 "*.json", "context_*.txt"）
            directory: 搜索目录（默认base_dir）
            
        Returns:
            匹配的文件路径列表
        """
        search_dir = Path(directory) if directory else self.base_dir
        
        try:
            matches = list(search_dir.glob(pattern))
            return [str(m) for m in matches]
        except Exception as e:
            print(f"Glob搜索失败: {e}")
            return []
    
    def grep_search(
        self,
        pattern: str,
        file_pattern: str = "*.json",
        directory: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        使用grep搜索文件内容
        
        Args:
            pattern: 搜索模式（正则表达式）
            file_pattern: 文件模式
            directory: 搜索目录
            
        Returns:
            匹配结果列表
        """
        search_dir = Path(directory) if directory else self.base_dir
        results = []
        
        # 查找匹配的文件
        files = list(search_dir.glob(file_pattern))
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        if re.search(pattern, line, re.IGNORECASE):
                            results.append({
                                "file": str(file_path),
                                "line": line_num,
                                "content": line.strip(),
                                "match": re.search(pattern, line, re.IGNORECASE).group()
                            })
            except Exception as e:
                print(f"读取文件 {file_path} 失败: {e}")
        
        return results
    
    def read_file_lines(
        self,
        file_path: str,
        start_line: int = 1,
        end_line: Optional[int] = None
    ) -> List[str]:
        """
        按行范围读取文件（适用于大文件）
        
        Args:
            file_path: 文件路径
            start_line: 起始行号（从1开始）
            end_line: 结束行号（None表示到文件末尾）
            
        Returns:
            行内容列表
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if end_line is None:
                    return lines[start_line - 1:]
                else:
                    return lines[start_line - 1:end_line]
        except Exception as e:
            print(f"读取文件行失败: {e}")
            return []
    
    def search_context_by_keywords(
        self,
        keywords: List[str],
        context_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        根据关键词搜索上下文
        
        Args:
            keywords: 关键词列表
            context_type: 上下文类型（如 "conversation", "memory"）
            
        Returns:
            匹配的上下文片段
        """
        results = []
        
        # 构建搜索模式
        pattern = "|".join(keywords)
        
        # 确定文件模式
        if context_type:
            file_pattern = f"*{context_type}*.json"
        else:
            file_pattern = "*.json"
        
        # 执行grep搜索
        grep_results = self.grep_search(pattern, file_pattern)
        
        # 整理结果
        for result in grep_results:
            results.append({
                "file": result["file"],
                "line": result["line"],
                "snippet": result["content"][:200],  # 限制长度
                "matched_keywords": [kw for kw in keywords if kw.lower() in result["content"].lower()]
            })
        
        return results


class ContextRetrievalOptimizer:
    """上下文检索优化器 - 主控制器"""
    
    def __init__(
        self,
        file_retriever: Optional[FileSystemRetriever] = None,
        use_vector_search: bool = False
    ):
        """
        初始化检索优化器
        
        Args:
            file_retriever: 文件系统检索器
            use_vector_search: 是否使用向量搜索（用于长期记忆）
        """
        self.file_retriever = file_retriever or FileSystemRetriever()
        self.use_vector_search = use_vector_search
    
    def retrieve_relevant_context(
        self,
        query: str,
        context_type: Optional[str] = None,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        检索相关上下文
        
        Args:
            query: 查询文本
            context_type: 上下文类型
            max_results: 最大结果数
            
        Returns:
            相关上下文列表
        """
        # 提取关键词
        keywords = self._extract_keywords(query)
        
        # 使用文件系统搜索
        results = self.file_retriever.search_context_by_keywords(
            keywords,
            context_type
        )
        
        # 限制结果数量
        return results[:max_results]
    
    def retrieve_by_file_path(
        self,
        file_path: str,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None
    ) -> str:
        """
        根据文件路径检索内容
        
        Args:
            file_path: 文件路径
            start_line: 起始行
            end_line: 结束行
            
        Returns:
            文件内容
        """
        if start_line or end_line:
            lines = self.file_retriever.read_file_lines(file_path, start_line or 1, end_line)
            return "\n".join(lines)
        else:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"读取文件失败: {e}")
                return ""
    
    def _extract_keywords(self, text: str, max_keywords: int = 5) -> List[str]:
        """
        从文本中提取关键词
        
        Args:
            text: 文本
            max_keywords: 最大关键词数
            
        Returns:
            关键词列表
        """
        # 简单实现：提取长度>2的词
        # 实际应该使用NLP工具（如jieba）
        words = re.findall(r'\b\w{2,}\b', text)
        
        # 过滤停用词（简化版）
        stopwords = {"的", "是", "在", "有", "和", "了", "我", "你", "他", "她", "它"}
        keywords = [w for w in words if w not in stopwords]
        
        # 去重并限制数量
        return list(set(keywords))[:max_keywords]
