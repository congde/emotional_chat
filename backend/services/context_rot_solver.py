#!/usr/bin/env python3
"""
上下文腐烂（Context Rot）解决方案
基于 Manus 和 LangChain 的最佳实践实现

核心功能：
1. 上下文缩减（Context Reduction）：压缩和摘要
2. 上下文检索（Context Retrieval）：高效获取相关信息
3. 上下文隔离（Context Isolation）：多智能体设计支持
4. 上下文卸载（Context Offloading）：文件系统外部化
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
import os
import hashlib
from pathlib import Path
from enum import Enum


class ContextRotThreshold(Enum):
    """上下文腐烂阈值"""
    SAFE = 128_000  # 安全区域：0-128K tokens
    WARNING = 200_000  # 警告区域：128K-200K tokens
    CRITICAL = 500_000  # 危险区域：>200K tokens


class ContextCompactionStrategy:
    """上下文压缩策略 - 可逆的外部化过程"""
    
    def __init__(self, storage_dir: str = "./context_storage"):
        """
        初始化压缩策略
        
        Args:
            storage_dir: 外部化存储目录
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def compact_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        压缩工具调用 - 将可重建信息外部化
        
        Args:
            tool_call: 完整的工具调用记录
            
        Returns:
            压缩后的工具调用（保留路径引用）
        """
        compacted = tool_call.copy()
        
        # 文件操作：将文件内容外部化，只保留路径
        if tool_call.get("tool_name") in ["write_file", "read_file", "create_file"]:
            file_path = tool_call.get("arguments", {}).get("path") or tool_call.get("arguments", {}).get("file_path")
            if file_path and os.path.exists(file_path):
                # 将完整内容保存到外部存储
                content = tool_call.get("result", {}).get("content", "")
                if content:
                    storage_path = self._save_to_storage(file_path, content, "file_content")
                    compacted["result"] = {
                        "storage_path": str(storage_path),
                        "file_path": file_path,
                        "size": len(content),
                        "compacted": True
                    }
                    # 移除原始内容
                    if "content" in compacted.get("result", {}):
                        del compacted["result"]["content"]
        
        # 搜索结果：将完整搜索结果外部化
        if tool_call.get("tool_name") in ["search", "grep", "find"]:
            results = tool_call.get("result", {}).get("results", [])
            if len(results) > 10:  # 结果过多时压缩
                storage_path = self._save_to_storage(
                    f"search_{tool_call.get('id', 'unknown')}",
                    json.dumps(results, ensure_ascii=False),
                    "search_results"
                )
                compacted["result"] = {
                    "storage_path": str(storage_path),
                    "count": len(results),
                    "summary": results[:3] if results else [],  # 保留前3条作为摘要
                    "compacted": True
                }
        
        return compacted
    
    def expand_tool_call(self, compacted_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        展开压缩的工具调用 - 从外部存储恢复
        
        Args:
            compacted_call: 压缩后的工具调用
            
        Returns:
            恢复后的完整工具调用
        """
        if not compacted_call.get("result", {}).get("compacted"):
            return compacted_call
        
        expanded = compacted_call.copy()
        storage_path = compacted_call.get("result", {}).get("storage_path")
        
        if storage_path and os.path.exists(storage_path):
            with open(storage_path, 'r', encoding='utf-8') as f:
                stored_data = json.load(f)
            
            # 从存储的JSON中提取内容
            stored_content = stored_data.get("content", "")
            
            # 根据类型恢复
            if storage_path.endswith("_file_content.json"):
                expanded["result"]["content"] = stored_content
            elif storage_path.endswith("_search_results.json"):
                expanded["result"]["results"] = json.loads(stored_content) if isinstance(stored_content, str) else stored_content
            
            expanded["result"]["compacted"] = False
            expanded["result"]["expanded_at"] = datetime.now().isoformat()
        
        return expanded
    
    def _save_to_storage(self, identifier: str, content: str, content_type: str) -> Path:
        """
        保存内容到外部存储
        
        Args:
            identifier: 标识符
            content: 内容
            content_type: 内容类型
            
        Returns:
            存储路径
        """
        # 生成唯一文件名
        hash_id = hashlib.md5(f"{identifier}_{content_type}".encode()).hexdigest()[:8]
        filename = f"{content_type}_{hash_id}_{int(datetime.now().timestamp())}.json"
        file_path = self.storage_dir / filename
        
        # 保存内容
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({
                "identifier": identifier,
                "content_type": content_type,
                "content": content,
                "created_at": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        return file_path


class ContextSummarizer:
    """上下文摘要器 - 不可逆的信息浓缩"""
    
    def __init__(self, llm_service=None):
        """
        初始化摘要器
        
        Args:
            llm_service: LLM服务（用于生成摘要）
        """
        self.llm_service = llm_service
    
    def summarize_conversation_turns(
        self,
        turns: List[Dict[str, Any]],
        schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        摘要对话轮次 - 使用结构化模式确保一致性
        
        Args:
            turns: 对话轮次列表
            schema: 结构化摘要模式
            
        Returns:
            摘要结果
        """
        if not turns:
            return {}
        
        # 默认结构化模式（参考 Manus 的做法）
        default_schema = {
            "modified_topics": "用户讨论的主要话题列表",
            "user_goals": "用户表达的目标或需求",
            "key_decisions": "达成的重要决定或共识",
            "unresolved_issues": "未解决的问题",
            "emotional_state": "情绪状态变化",
            "last_stop_point": "上次停止的位置或上下文"
        }
        
        schema = schema or default_schema
        
        # 提取关键信息
        summary = {
            "modified_topics": self._extract_topics(turns),
            "user_goals": self._extract_goals(turns),
            "key_decisions": self._extract_decisions(turns),
            "unresolved_issues": self._extract_unresolved(turns),
            "emotional_state": self._extract_emotion_trend(turns),
            "last_stop_point": turns[-1].get("content", "")[:200] if turns else "",
            "turn_count": len(turns),
            "time_span": self._calculate_time_span(turns),
            "summarized_at": datetime.now().isoformat()
        }
        
        # 如果有LLM服务，可以进一步优化摘要
        if self.llm_service:
            summary = self._llm_enhance_summary(summary, turns, schema)
        
        return summary
    
    def _extract_topics(self, turns: List[Dict[str, Any]]) -> List[str]:
        """提取主要话题"""
        topics = []
        for turn in turns:
            content = turn.get("content", "")
            # 简单提取：实际应该用NLP
            if len(content) > 20:
                topics.append(content[:50])
        return list(set(topics))[:5]  # 去重并限制数量
    
    def _extract_goals(self, turns: List[Dict[str, Any]]) -> List[str]:
        """提取用户目标"""
        goals = []
        keywords = ["想要", "希望", "需要", "目标", "计划"]
        for turn in turns:
            content = turn.get("content", "")
            for keyword in keywords:
                if keyword in content:
                    goals.append(content[:100])
                    break
        return goals[:3]
    
    def _extract_decisions(self, turns: List[Dict[str, Any]]) -> List[str]:
        """提取重要决定"""
        decisions = []
        keywords = ["决定", "选择", "同意", "确定"]
        for turn in turns:
            content = turn.get("content", "")
            for keyword in keywords:
                if keyword in content:
                    decisions.append(content[:100])
                    break
        return decisions[:3]
    
    def _extract_unresolved(self, turns: List[Dict[str, Any]]) -> List[str]:
        """提取未解决问题"""
        unresolved = []
        keywords = ["问题", "困难", "不知道", "怎么办", "困惑"]
        for turn in turns:
            content = turn.get("content", "")
            for keyword in keywords:
                if keyword in content:
                    unresolved.append(content[:100])
                    break
        return unresolved[:3]
    
    def _extract_emotion_trend(self, turns: List[Dict[str, Any]]) -> str:
        """提取情绪趋势"""
        emotions = [turn.get("emotion", "neutral") for turn in turns if turn.get("emotion")]
        if not emotions:
            return "稳定"
        
        # 简单趋势分析
        unique_emotions = list(set(emotions))
        if len(unique_emotions) > 2:
            return "波动"
        elif len(unique_emotions) == 1:
            return f"持续{unique_emotions[0]}"
        else:
            return f"从{unique_emotions[0]}到{unique_emotions[1]}"
    
    def _calculate_time_span(self, turns: List[Dict[str, Any]]) -> str:
        """计算时间跨度"""
        timestamps = [turn.get("timestamp") for turn in turns if turn.get("timestamp")]
        if len(timestamps) < 2:
            return "单次会话"
        
        try:
            first = datetime.fromisoformat(timestamps[0])
            last = datetime.fromisoformat(timestamps[-1])
            delta = last - first
            if delta.days > 0:
                return f"{delta.days}天"
            elif delta.seconds > 3600:
                return f"{delta.seconds // 3600}小时"
            else:
                return f"{delta.seconds // 60}分钟"
        except:
            return "未知"
    
    def _llm_enhance_summary(
        self,
        summary: Dict[str, Any],
        turns: List[Dict[str, Any]],
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """使用LLM增强摘要（可选）"""
        # TODO: 实现LLM增强摘要
        return summary


class ContextRotSolver:
    """上下文腐烂解决方案 - 主控制器"""
    
    def __init__(
        self,
        pre_rot_threshold: int = ContextRotThreshold.SAFE.value,
        compaction_strategy: Optional[ContextCompactionStrategy] = None,
        summarizer: Optional[ContextSummarizer] = None
    ):
        """
        初始化上下文腐烂解决方案
        
        Args:
            pre_rot_threshold: 腐烂前阈值（默认128K tokens）
            compaction_strategy: 压缩策略
            summarizer: 摘要器
        """
        self.pre_rot_threshold = pre_rot_threshold
        self.compaction = compaction_strategy or ContextCompactionStrategy()
        self.summarizer = summarizer or ContextSummarizer()
    
    def estimate_tokens(self, context: Dict[str, Any]) -> int:
        """
        估算上下文的token数量
        
        Args:
            context: 上下文数据
            
        Returns:
            估算的token数
        """
        # 简化估算：每个中文字符约1.5个token，每个英文字符约0.5个token
        total_chars = 0
        
        def count_chars(obj):
            if isinstance(obj, str):
                # 中文字符计数
                chinese_chars = sum(1 for c in obj if '\u4e00' <= c <= '\u9fff')
                other_chars = len(obj) - chinese_chars
                return chinese_chars * 1.5 + other_chars * 0.5
            elif isinstance(obj, dict):
                return sum(count_chars(v) for v in obj.values())
            elif isinstance(obj, list):
                return sum(count_chars(item) for item in obj)
            else:
                return len(str(obj)) * 0.5
        
        return int(count_chars(context))
    
    def should_compact(self, context: Dict[str, Any]) -> bool:
        """
        判断是否需要压缩
        
        Args:
            context: 上下文数据
            
        Returns:
            是否需要压缩
        """
        token_count = self.estimate_tokens(context)
        return token_count > self.pre_rot_threshold * 0.8  # 达到80%阈值时开始压缩
    
    def should_summarize(self, context: Dict[str, Any]) -> bool:
        """
        判断是否需要摘要
        
        Args:
            context: 上下文数据
            
        Returns:
            是否需要摘要
        """
        token_count = self.estimate_tokens(context)
        return token_count > self.pre_rot_threshold  # 超过阈值时进行摘要
    
    def reduce_context(
        self,
        context: Dict[str, Any],
        preserve_recent_turns: int = 5
    ) -> Dict[str, Any]:
        """
        缩减上下文 - 先压缩，再摘要
        
        Args:
            context: 完整上下文
            preserve_recent_turns: 保留最近N轮完整对话
            
        Returns:
            缩减后的上下文
        """
        reduced = context.copy()
        
        # 1. 首先尝试压缩（可逆）
        if self.should_compact(reduced):
            reduced = self._apply_compaction(reduced, preserve_recent_turns)
        
        # 2. 如果压缩后仍然超过阈值，进行摘要（不可逆）
        if self.should_summarize(reduced):
            reduced = self._apply_summarization(reduced, preserve_recent_turns)
        
        return reduced
    
    def _apply_compaction(
        self,
        context: Dict[str, Any],
        preserve_recent: int
    ) -> Dict[str, Any]:
        """
        应用压缩策略
        
        Args:
            context: 上下文数据
            preserve_recent: 保留最近N轮
            
        Returns:
            压缩后的上下文
        """
        compacted = context.copy()
        
        # 压缩工具调用历史
        if "tool_calls" in compacted:
            tool_calls = compacted["tool_calls"]
            # 保留最近的工具调用完整，压缩旧的
            recent_calls = tool_calls[-preserve_recent:] if len(tool_calls) > preserve_recent else tool_calls
            old_calls = tool_calls[:-preserve_recent] if len(tool_calls) > preserve_recent else []
            
            compacted_old = [self.compaction.compact_tool_call(call) for call in old_calls]
            compacted["tool_calls"] = compacted_old + recent_calls
            compacted["compaction_applied"] = True
            compacted["compaction_stats"] = {
                "total_calls": len(tool_calls),
                "compacted_calls": len(old_calls),
                "preserved_calls": len(recent_calls)
            }
        
        return compacted
    
    def _apply_summarization(
        self,
        context: Dict[str, Any],
        preserve_recent: int
    ) -> Dict[str, Any]:
        """
        应用摘要策略
        
        Args:
            context: 上下文数据
            preserve_recent: 保留最近N轮
            
        Returns:
            摘要后的上下文
        """
        summarized = context.copy()
        
        # 摘要对话历史
        if "chat_history" in summarized:
            history = summarized["chat_history"]
            if len(history) > preserve_recent * 2:
                # 分离需要摘要的部分和保留的部分
                to_summarize = history[:-preserve_recent]
                to_preserve = history[-preserve_recent:]
                
                # 生成摘要
                summary = self.summarizer.summarize_conversation_turns(to_summarize)
                
                # 替换为摘要 + 保留的完整对话
                summarized["chat_history"] = [
                    {"role": "system", "content": f"早期对话摘要：{json.dumps(summary, ensure_ascii=False)}"}
                ] + to_preserve
                
                summarized["summarization_applied"] = True
                summarized["summarization_stats"] = {
                    "total_turns": len(history),
                    "summarized_turns": len(to_summarize),
                    "preserved_turns": len(to_preserve)
                }
        
        return summarized
    
    def offload_to_file(
        self,
        context: Dict[str, Any],
        identifier: str
    ) -> Tuple[Dict[str, Any], str]:
        """
        将上下文卸载到文件系统
        
        Args:
            context: 完整上下文
            identifier: 标识符（如session_id）
            
        Returns:
            (精简后的上下文, 文件路径)
        """
        # 保存完整上下文到文件
        storage_dir = Path(self.compaction.storage_dir)
        file_path = storage_dir / f"context_{identifier}_{int(datetime.now().timestamp())}.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({
                "identifier": identifier,
                "context": context,
                "created_at": datetime.now().isoformat(),
                "token_count": self.estimate_tokens(context)
            }, f, ensure_ascii=False, indent=2)
        
        # 返回精简版本（只保留引用）
        offloaded = {
            "identifier": identifier,
            "storage_path": str(file_path),
            "summary": {
                "user_id": context.get("metadata", {}).get("user_id"),
                "session_id": context.get("metadata", {}).get("session_id"),
                "token_count": self.estimate_tokens(context),
                "offloaded_at": datetime.now().isoformat()
            },
            "offloaded": True
        }
        
        return offloaded, str(file_path)
    
    def load_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        从文件系统加载上下文
        
        Args:
            file_path: 文件路径
            
        Returns:
            完整的上下文数据
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("context", {})
    
    def get_context_status(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取上下文状态报告
        
        Args:
            context: 上下文数据
            
        Returns:
            状态报告
        """
        token_count = self.estimate_tokens(context)
        
        status = {
            "token_count": token_count,
            "threshold": self.pre_rot_threshold,
            "usage_percent": (token_count / self.pre_rot_threshold) * 100,
            "status": "safe"
        }
        
        if token_count > ContextRotThreshold.CRITICAL.value:
            status["status"] = "critical"
            status["recommendation"] = "立即进行摘要和卸载"
        elif token_count > ContextRotThreshold.WARNING.value:
            status["status"] = "warning"
            status["recommendation"] = "建议进行压缩或摘要"
        elif token_count > self.pre_rot_threshold:
            status["status"] = "caution"
            status["recommendation"] = "考虑压缩"
        else:
            status["recommendation"] = "状态良好"
        
        return status
