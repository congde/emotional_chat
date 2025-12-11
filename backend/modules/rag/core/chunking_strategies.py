#!/usr/bin/env python3
"""
RAG分块策略模块
实现多种文档分块策略，提升RAG系统的检索质量
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from .langchain_compat import Document
from backend.logging_config import get_logger

logger = get_logger(__name__)


# ==================== 中文分句工具 ====================

def split_sentences_zh(text: str) -> List[str]:
    """
    中文分句函数
    基于正则表达式识别中文标点进行分句
    
    Args:
        text: 待分句的文本
        
    Returns:
        句子列表
    """
    # 匹配中文句号、感叹号、问号、分号等作为句子边界
    pattern = re.compile(r'([^。！？；]*[。！？；]+|[^。！？；]+$)')
    sentences = [m.group(0).strip() for m in pattern.finditer(text) if m.group(0).strip()]
    return sentences


# ==================== 基础分块策略 ====================

class CharacterTextSplitter:
    """固定长度分块策略"""
    
    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 90):
        """
        初始化固定长度分块器
        
        Args:
            chunk_size: 块大小（字符数）
            chunk_overlap: 重叠大小（字符数）
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split_text(self, text: str) -> List[str]:
        """按固定长度切分文本"""
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            
            # 重叠处理
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        
        return chunks
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """分割文档列表"""
        all_chunks = []
        for doc in documents:
            text_chunks = self.split_text(doc.page_content)
            for i, chunk_text in enumerate(text_chunks):
                chunk = Document(
                    page_content=chunk_text,
                    metadata={
                        **doc.metadata,
                        'chunk_id': i,
                        'chunking_strategy': 'character',
                        'chunk_size': len(chunk_text)
                    }
                )
                all_chunks.append(chunk)
        return all_chunks


class SentenceTextSplitter:
    """基于句子的分块策略"""
    
    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 80):
        """
        初始化句子分块器
        
        Args:
            chunk_size: 目标块大小（字符数）
            chunk_overlap: 重叠大小（字符数）
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split_text(self, text: str) -> List[str]:
        """按句子切分文本"""
        sentences = split_sentences_zh(text)
        if not sentences:
            return [text]
        
        chunks = []
        buf = ""
        
        for s in sentences:
            # 如果当前缓冲区加上新句子不超过chunk_size，则添加
            if len(buf) + len(s) <= self.chunk_size:
                buf += s
            else:
                # 保存当前块
                if buf:
                    chunks.append(buf)
                
                # 处理重叠：从上一个块的尾部截取overlap字符
                if self.chunk_overlap > 0 and len(buf) > self.chunk_overlap:
                    buf = buf[-self.chunk_overlap:] + s
                else:
                    buf = s
        
        # 添加最后一个块
        if buf:
            chunks.append(buf)
        
        return chunks
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """分割文档列表"""
        all_chunks = []
        for doc in documents:
            text_chunks = self.split_text(doc.page_content)
            for i, chunk_text in enumerate(text_chunks):
                chunk = Document(
                    page_content=chunk_text,
                    metadata={
                        **doc.metadata,
                        'chunk_id': i,
                        'chunking_strategy': 'sentence',
                        'chunk_size': len(chunk_text)
                    }
                )
                all_chunks.append(chunk)
        return all_chunks


# ==================== 结构感知分块策略 ====================

class MarkdownStructureSplitter:
    """Markdown结构化分块策略"""
    
    def __init__(
        self,
        chunk_size: int = 900,
        min_chunk: int = 250,
        overlap_ratio: float = 0.1
    ):
        """
        初始化Markdown结构分块器
        
        Args:
            chunk_size: 目标块大小（字符数）
            min_chunk: 最小块大小（字符数）
            overlap_ratio: 重叠比例
        """
        self.chunk_size = chunk_size
        self.min_chunk = min_chunk
        self.overlap_ratio = overlap_ratio
        
        # 正则模式
        self.heading_pat = re.compile(r'^(#{1,6})\s+(.*)$')
        self.fence_pat = re.compile(r'^```')
    
    def split_text(self, text: str) -> List[Dict[str, Any]]:
        """
        按Markdown结构切分文本
        
        Returns:
            块列表，每个块包含text和meta信息
        """
        lines = text.splitlines()
        sections = []
        in_code = False
        current = {"level": 0, "title": "", "content": [], "path": []}
        path_stack = []
        
        for ln in lines:
            # 检测代码块
            if self.fence_pat.match(ln):
                in_code = not in_code
            
            # 检测标题（不在代码块中）
            m = self.heading_pat.match(ln) if not in_code else None
            if m:
                # 保存当前章节
                if current["content"]:
                    sections.append(current)
                
                # 创建新章节
                level = len(m.group(1))
                title = m.group(2).strip()
                
                # 更新路径栈
                while path_stack and path_stack[-1][0] >= level:
                    path_stack.pop()
                path_stack.append((level, title))
                breadcrumbs = [t for _, t in path_stack]
                
                current = {
                    "level": level,
                    "title": title,
                    "content": [],
                    "path": breadcrumbs
                }
            else:
                current["content"].append(ln)
        
        # 添加最后一个章节
        if current["content"]:
            sections.append(current)
        
        # 将章节转换为块
        chunks = []
        for sec in sections:
            raw = "\n".join(sec["content"]).strip()
            if not raw:
                continue
            
            if len(raw) <= self.chunk_size:
                chunks.append({
                    "text": raw,
                    "meta": {
                        "section_title": sec["path"][-1] if sec["path"] else "",
                        "breadcrumbs": sec["path"],
                        "section_level": sec["level"]
                    }
                })
            else:
                # 超长章节需要二次切分（按段落）
                paras = [p.strip() for p in raw.split("\n\n") if p.strip()]
                buf = ""
                for p in paras:
                    if len(buf) + len(p) + 2 <= self.chunk_size:
                        buf += (("\n\n" + p) if buf else p)
                    else:
                        if buf:
                            chunks.append({
                                "text": buf,
                                "meta": {
                                    "section_title": sec["path"][-1] if sec["path"] else "",
                                    "breadcrumbs": sec["path"],
                                    "section_level": sec["level"]
                                }
                            })
                        buf = p
                if buf:
                    chunks.append({
                        "text": buf,
                        "meta": {
                            "section_title": sec["path"][-1] if sec["path"] else "",
                            "breadcrumbs": sec["path"],
                            "section_level": sec["level"]
                        }
                    })
        
        # 合并过短的块
        merged = []
        for ch in chunks:
            if not merged:
                merged.append(ch)
                continue
            
            # 如果当前块太短且与前一个块在同一章节，则合并
            if (len(ch["text"]) < self.min_chunk and
                merged[-1]["meta"]["breadcrumbs"] == ch["meta"]["breadcrumbs"]):
                merged[-1]["text"] += "\n\n" + ch["text"]
            else:
                merged.append(ch)
        
        # 添加标题路径前缀和重叠
        overlap = int(self.chunk_size * self.overlap_ratio)
        for ch in merged:
            bc = " > ".join(ch["meta"]["breadcrumbs"][-3:])
            prefix = f"[{bc}]\n" if bc else ""
            if prefix and not ch["text"].startswith(prefix):
                ch["text"] = prefix + ch["text"]
        
        return merged
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """分割文档列表"""
        all_chunks = []
        for doc in documents:
            chunks_data = self.split_text(doc.page_content)
            for i, chunk_data in enumerate(chunks_data):
                chunk = Document(
                    page_content=chunk_data["text"],
                    metadata={
                        **doc.metadata,
                        **chunk_data["meta"],
                        'chunk_id': i,
                        'chunking_strategy': 'markdown_structure',
                        'chunk_size': len(chunk_data["text"])
                    }
                )
                all_chunks.append(chunk)
        return all_chunks


class DialogueSplitter:
    """对话式分块策略"""
    
    def __init__(
        self,
        max_turns: int = 10,
        max_chars: int = 900,
        overlap_turns: int = 2
    ):
        """
        初始化对话分块器
        
        Args:
            max_turns: 每个块最大轮次数
            max_chars: 每个块最大字符数
            overlap_turns: 重叠轮次数
        """
        self.max_turns = max_turns
        self.max_chars = max_chars
        self.overlap_turns = overlap_turns
    
    def parse_dialogue(self, text: str) -> List[Dict[str, Any]]:
        """
        解析对话文本，提取轮次
        
        Args:
            text: 对话文本
            
        Returns:
            轮次列表，每个轮次包含speaker和text
        """
        turns = []
        # 匹配常见的对话格式：User: xxx 或 用户: xxx
        pattern = re.compile(r'^(?:User|用户|Assistant|助手|AI|机器人)[:：]\s*(.+)$', re.MULTILINE)
        
        lines = text.splitlines()
        current_speaker = None
        current_text = []
        
        for line in lines:
            match = pattern.match(line)
            if match:
                # 保存上一个轮次
                if current_speaker and current_text:
                    turns.append({
                        "speaker": current_speaker,
                        "text": "\n".join(current_text).strip()
                    })
                
                # 开始新轮次
                current_speaker = match.group(0).split(':')[0].split('：')[0].strip()
                current_text = [match.group(1)]
            else:
                if current_speaker:
                    current_text.append(line)
                else:
                    # 如果没有识别到说话人，尝试按空行分割
                    if line.strip():
                        if not current_speaker:
                            current_speaker = "Unknown"
                        current_text.append(line)
        
        # 添加最后一个轮次
        if current_speaker and current_text:
            turns.append({
                "speaker": current_speaker,
                "text": "\n".join(current_text).strip()
            })
        
        return turns
    
    def split_text(self, text: str) -> List[Dict[str, Any]]:
        """按对话轮次切分文本"""
        turns = self.parse_dialogue(text)
        if not turns:
            # 如果不是对话格式，返回整个文本
            return [{"text": text, "meta": {}}]
        
        chunks = []
        i = 0
        
        while i < len(turns):
            j = i
            char_count = 0
            speakers = set()
            
            # 收集连续的轮次
            while j < len(turns):
                t = turns[j]
                uttr_len = len(t["text"])
                
                if (j - i + 1) > self.max_turns or (char_count + uttr_len) > self.max_chars:
                    break
                
                char_count += uttr_len
                speakers.add(t["speaker"])
                j += 1
            
            if j > i:
                window = turns[i:j]
            elif i < len(turns):
                window = [turns[i]]
            else:
                break
            
            # 构建块文本
            text_parts = [f'{t["speaker"]}: {t["text"]}' for t in window]
            chunk_text = "\n".join(text_parts)
            
            chunks.append({
                "text": chunk_text,
                "meta": {
                    "speakers": list(speakers),
                    "turns_range": (i, j - 1),
                    "turn_count": len(window)
                }
            })
            
            # 按轮次重叠回退
            if j >= len(turns):
                break
            next_start = i + len(window) - self.overlap_turns
            i = max(next_start, i + 1)
        
        return chunks
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """分割文档列表"""
        all_chunks = []
        for doc in documents:
            chunks_data = self.split_text(doc.page_content)
            for i, chunk_data in enumerate(chunks_data):
                chunk = Document(
                    page_content=chunk_data["text"],
                    metadata={
                        **doc.metadata,
                        **chunk_data.get("meta", {}),
                        'chunk_id': i,
                        'chunking_strategy': 'dialogue',
                        'chunk_size': len(chunk_data["text"])
                    }
                )
                all_chunks.append(chunk)
        return all_chunks


# ==================== 高级分块策略 ====================

class SmallBigChunking:
    """
    小-大分块策略
    用小粒度块（句子）做高精度召回，用大粒度块（段落/小节）做上下文
    """
    
    def __init__(
        self,
        small_chunk_size: int = 200,
        big_chunk_size: int = 900,
        small_overlap: int = 50,
        big_overlap: int = 90
    ):
        """
        初始化小-大分块器
        
        Args:
            small_chunk_size: 小块大小（用于召回）
            big_chunk_size: 大块大小（用于上下文）
            small_overlap: 小块重叠
            big_overlap: 大块重叠
        """
        self.small_chunk_size = small_chunk_size
        self.big_chunk_size = big_chunk_size
        self.small_overlap = small_overlap
        self.big_overlap = big_overlap
        
        # 使用句子分块器创建小块
        self.small_splitter = SentenceTextSplitter(
            chunk_size=small_chunk_size,
            chunk_overlap=small_overlap
        )
        
        # 使用递归分块器创建大块
        from .langchain_compat import RecursiveCharacterTextSplitter
        self.big_splitter = RecursiveCharacterTextSplitter(
            chunk_size=big_chunk_size,
            chunk_overlap=big_overlap,
            separators=["\n\n", "\n", "。", "！", "？", "；", ".", "!", "?", ";", " ", ""]
        )
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        分割文档，同时生成小块和大块
        
        Returns:
            文档块列表，包含小块（用于索引）和大块（用于上下文）
        """
        all_chunks = []
        
        for doc in documents:
            # 先创建大块
            big_chunks = self.big_splitter.split_documents([doc])
            
            # 为每个大块创建小块
            for big_idx, big_chunk in enumerate(big_chunks):
                # 创建小块
                small_chunks = self.small_splitter.split_documents([big_chunk])
                
                for small_idx, small_chunk in enumerate(small_chunks):
                    # 添加父子关系元数据
                    small_chunk.metadata.update({
                        'chunking_strategy': 'small_big',
                        'chunk_type': 'small',
                        'parent_chunk_id': big_idx,
                        'big_chunk_text': big_chunk.page_content[:500],  # 保存大块文本预览
                        'small_chunk_id': small_idx
                    })
                    all_chunks.append(small_chunk)
                
                # 也保存大块（用于上下文）
                big_chunk.metadata.update({
                    'chunking_strategy': 'small_big',
                    'chunk_type': 'big',
                    'big_chunk_id': big_idx,
                    'child_count': len(small_chunks)
                })
                all_chunks.append(big_chunk)
        
        return all_chunks


class ParentChildChunking:
    """
    父子段分块策略
    将文档按结构单元（父块）切分，再在每个父块内切出子块（句子/短段）
    """
    
    def __init__(
        self,
        parent_chunk_size: int = 1000,
        child_chunk_size: int = 300,
        parent_overlap: int = 100,
        child_overlap: int = 50
    ):
        """
        初始化父子段分块器
        
        Args:
            parent_chunk_size: 父块大小
            child_chunk_size: 子块大小
            parent_overlap: 父块重叠
            child_overlap: 子块重叠
        """
        self.parent_chunk_size = parent_chunk_size
        self.child_chunk_size = child_chunk_size
        self.parent_overlap = parent_overlap
        self.child_overlap = child_overlap
        
        # 使用Markdown结构分块器创建父块
        self.parent_splitter = MarkdownStructureSplitter(
            chunk_size=parent_chunk_size,
            min_chunk=200,
            overlap_ratio=parent_overlap / parent_chunk_size if parent_chunk_size > 0 else 0.1
        )
        
        # 使用句子分块器创建子块
        self.child_splitter = SentenceTextSplitter(
            chunk_size=child_chunk_size,
            chunk_overlap=child_overlap
        )
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        分割文档，创建父子块结构
        
        Returns:
            文档块列表，包含父块和子块，通过parent_id关联
        """
        all_chunks = []
        
        for doc in documents:
            # 创建父块
            parent_chunks = self.parent_splitter.split_documents([doc])
            
            for parent_idx, parent_chunk in enumerate(parent_chunks):
                # 保存父块
                parent_chunk.metadata.update({
                    'chunking_strategy': 'parent_child',
                    'chunk_type': 'parent',
                    'parent_id': parent_idx
                })
                all_chunks.append(parent_chunk)
                
                # 为父块创建子块
                child_chunks = self.child_splitter.split_documents([parent_chunk])
                
                for child_idx, child_chunk in enumerate(child_chunks):
                    # 添加父子关系
                    child_chunk.metadata.update({
                        'chunking_strategy': 'parent_child',
                        'chunk_type': 'child',
                        'parent_id': parent_idx,
                        'child_id': child_idx,
                        'parent_title': parent_chunk.metadata.get('section_title', ''),
                        'breadcrumbs': parent_chunk.metadata.get('breadcrumbs', [])
                    })
                    all_chunks.append(child_chunk)
        
        return all_chunks

