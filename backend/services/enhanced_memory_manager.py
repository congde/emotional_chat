#!/usr/bin/env python3
"""
增强版记忆管理器
实现文档中提到的高级记忆功能：
1. 短期记忆：滑动窗口 + 关键轮次保留
2. 长期记忆：向量检索 + 时间衰减
3. 记忆重要性评估
4. 记忆衰减机制
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json
import math
from backend.vector_store import VectorStore
from backend.memory_extractor import MemoryExtractor
from backend.database import DatabaseManager, MemoryItem


class MemoryDecayCalculator:
    """记忆衰减计算器 - 实现遗忘曲线"""
    
    @staticmethod
    def decay_score(original_score: float, days_ago: float, decay_rate: float = 0.9) -> float:
        """
        计算记忆衰减后的分数
        
        Args:
            original_score: 原始分数
            days_ago: 距今天数
            decay_rate: 衰减率（默认每天衰减10%）
            
        Returns:
            衰减后的分数
        """
        return original_score * (decay_rate ** days_ago)
    
    @staticmethod
    def calculate_importance_boost(memory_type: str, emotion_intensity: float, 
                                   access_count: int = 0) -> float:
        """
        计算记忆重要性提升系数
        
        Args:
            memory_type: 记忆类型
            emotion_intensity: 情绪强度
            access_count: 被访问次数
            
        Returns:
            重要性提升系数 (1.0-2.0)
        """
        # 基础权重
        type_weights = {
            "commitment": 1.8,      # 承诺类记忆最重要
            "relationship": 1.6,    # 关系类记忆
            "event": 1.4,           # 事件类记忆
            "concern": 1.5,         # 关注点
            "preference": 1.3,      # 偏好
            "other": 1.0            # 其他
        }
        
        type_boost = type_weights.get(memory_type, 1.0)
        
        # 情绪强度加成（高强度情绪的记忆更重要）
        emotion_boost = 1.0 + (emotion_intensity - 5.0) / 10.0  # 范围：0.5-1.5
        
        # 访问频率加成（被经常回忆的记忆更重要）
        access_boost = 1.0 + min(access_count * 0.05, 0.5)  # 最多+50%
        
        return type_boost * emotion_boost * access_boost


class ShortTermMemory:
    """短期记忆管理器 - 滑动窗口 + 关键轮次保留"""
    
    def __init__(self, window_size: int = 8, max_tokens: int = 4096):
        """
        初始化短期记忆管理器
        
        Args:
            window_size: 滑动窗口大小（保留最近N轮对话）
            max_tokens: 最大token数限制
        """
        self.window_size = window_size
        self.max_tokens = max_tokens
    
    def truncate_conversation(self, 
                             history: List[Dict[str, Any]], 
                             important_markers: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        """
        裁剪对话历史
        
        Args:
            history: 完整对话历史
            important_markers: 重要对话的索引列表
            
        Returns:
            裁剪后的对话历史
        """
        if not history:
            return []
        
        # 1. 保留标记为重要的对话
        important_turns = []
        if important_markers:
            important_turns = [history[i] for i in important_markers if i < len(history)]
        
        # 2. 估算token数（简化：每个字符约0.5个token）
        def estimate_tokens(messages: List[Dict[str, Any]]) -> int:
            return sum(len(str(msg.get("content", ""))) // 2 for msg in messages)
        
        current_tokens = estimate_tokens(important_turns)
        
        # 3. 按时间倒序添加最近的对话，直到达到限制
        recent_turns = []
        reserved_tokens = int(self.max_tokens * 0.8)  # 预留20%空间给新输入
        
        for msg in reversed(history):
            # 跳过已包含的重要对话
            if important_markers and history.index(msg) in important_markers:
                continue
            
            msg_tokens = len(str(msg.get("content", ""))) // 2
            if current_tokens + msg_tokens > reserved_tokens:
                break
            
            recent_turns.insert(0, msg)
            current_tokens += msg_tokens
            
            # 达到窗口大小限制
            if len(recent_turns) >= self.window_size:
                break
        
        # 4. 合并重要对话和最近对话，按时间排序
        all_turns = important_turns + recent_turns
        all_turns.sort(key=lambda x: x.get("timestamp", ""))
        
        return all_turns
    
    def mark_important_turn(self, 
                           message: Dict[str, Any], 
                           criteria: Optional[Dict[str, Any]] = None) -> bool:
        """
        判断对话轮次是否重要
        
        Args:
            message: 消息对象
            criteria: 判断标准
            
        Returns:
            是否重要
        """
        content = message.get("content", "").lower()
        emotion_intensity = message.get("emotion_intensity", 5.0)
        
        # 默认判断标准
        important_keywords = [
            "总是", "从不", "一直", "每次", "永远",  # 频率词
            "承诺", "保证", "答应", "同意",  # 承诺类
            "最重要", "关键", "核心", "主要",  # 强调词
            "失眠", "焦虑", "抑郁", "痛苦",  # 心理健康
            "辞职", "分手", "离婚", "搬家",  # 重大事件
        ]
        
        # 包含重要关键词
        if any(keyword in content for keyword in important_keywords):
            return True
        
        # 高强度情绪（>7.5）
        if emotion_intensity > 7.5:
            return True
        
        # 用户明确请求（以"请"开头或包含疑问词）
        if content.startswith("请") or any(q in content for q in ["吗", "呢", "如何", "怎么", "为什么"]):
            return True
        
        return False


class EnhancedMemoryManager:
    """增强版记忆管理器 - 统一管理短期和长期记忆"""
    
    def __init__(self):
        """初始化增强版记忆管理器"""
        self.vector_store = VectorStore()
        self.extractor = MemoryExtractor()
        self.short_term = ShortTermMemory()
        self.decay_calculator = MemoryDecayCalculator()
        
        # 创建专门的记忆集合
        try:
            from chromadb.utils import embedding_functions
            default_ef = embedding_functions.DefaultEmbeddingFunction()
            
            self.memory_collection = self.vector_store.client.get_or_create_collection(
                name="user_memories_enhanced",
                embedding_function=default_ef,
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            print(f"初始化记忆集合失败: {e}")
            self.memory_collection = None
    
    async def process_conversation(self, 
                                   session_id: str, 
                                   user_id: str,
                                   user_message: str, 
                                   bot_response: str,
                                   emotion: Optional[str] = None,
                                   emotion_intensity: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        处理对话并提取记忆
        
        Args:
            session_id: 会话ID
            user_id: 用户ID
            user_message: 用户消息
            bot_response: 机器人回复
            emotion: 情绪
            emotion_intensity: 情绪强度
            
        Returns:
            提取的记忆列表
        """
        # 1. 判断是否需要提取记忆
        if not self.extractor.should_extract_memory(user_message, emotion, emotion_intensity):
            return []
        
        # 2. 提取记忆
        memories = self.extractor.extract_memories(
            user_message, bot_response, emotion, emotion_intensity
        )
        
        # 3. 计算重要性提升
        stored_memories = []
        for memory in memories:
            # 计算重要性
            importance_boost = self.decay_calculator.calculate_importance_boost(
                memory.get("type", "other"),
                emotion_intensity or 5.0,
                0  # 新记忆访问次数为0
            )
            
            # 更新重要性分数
            original_importance = memory.get("importance", 0.5)
            memory["importance"] = min(original_importance * importance_boost, 1.0)
            
            # 存储记忆
            stored_memory = await self.store_memory(
                user_id=user_id,
                session_id=session_id,
                memory=memory
            )
            
            if stored_memory:
                stored_memories.append(stored_memory)
        
        return stored_memories
    
    async def store_memory(self, 
                          user_id: str, 
                          session_id: str,
                          memory: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        存储单条记忆到向量数据库和关系数据库
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            memory: 记忆数据
            
        Returns:
            存储的记忆（包含ID）
        """
        if not self.memory_collection:
            print("记忆集合未初始化")
            return None
        
        try:
            # 生成唯一ID
            import uuid
            memory_id = f"{user_id}_{uuid.uuid4().hex[:12]}"
            
            # 准备存储文本（用于向量化）
            memory_text = f"{memory.get('summary', '')} {memory.get('content', '')}"
            
            # 准备元数据
            metadata = {
                "user_id": user_id,
                "session_id": session_id,
                "type": memory.get("type", "other"),
                "emotion": memory.get("emotion", "neutral"),
                "intensity": float(memory.get("intensity", 5.0)),
                "importance": float(memory.get("importance", 0.5)),
                "timestamp": memory.get("timestamp", datetime.now().isoformat()),
                "extraction_method": memory.get("extraction_method", "unknown")
            }
            
            # 存储到向量数据库
            self.memory_collection.add(
                documents=[memory_text],
                metadatas=[metadata],
                ids=[memory_id]
            )
            
            # 同步到关系数据库
            with DatabaseManager() as db:
                memory_item = MemoryItem(
                    memory_id=memory_id,
                    user_id=user_id,
                    session_id=session_id,
                    content=memory.get("content", ""),
                    summary=memory.get("summary", ""),
                    memory_type=memory.get("type", "other"),
                    emotion=memory.get("emotion"),
                    emotion_intensity=memory.get("intensity"),
                    importance=memory.get("importance", 0.5),
                    extraction_method=memory.get("extraction_method", "unknown"),
                    keywords=json.dumps(memory.get("keywords", []), ensure_ascii=False)
                )
                db.db.add(memory_item)
                db.db.commit()
            
            # 返回完整记忆数据
            memory["id"] = memory_id
            memory["user_id"] = user_id
            memory["session_id"] = session_id
            
            return memory
            
        except Exception as e:
            print(f"存储记忆失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def retrieve_memories(self, 
                               user_id: str, 
                               query: str,
                               n_results: int = 5,
                               days_limit: Optional[int] = 30,
                               min_importance: float = 0.3,
                               emotion_filter: Optional[str] = None,
                               enable_decay: bool = True) -> List[Dict[str, Any]]:
        """
        检索相关记忆（支持时间衰减）
        
        Args:
            user_id: 用户ID
            query: 查询文本
            n_results: 返回结果数量
            days_limit: 时间限制（天数）
            min_importance: 最小重要性阈值
            emotion_filter: 情绪过滤
            enable_decay: 是否启用时间衰减
            
        Returns:
            相关记忆列表（按重要性排序）
        """
        if not self.memory_collection:
            return []
        
        try:
            # 构建过滤条件
            where_filter = {"user_id": user_id}
            if emotion_filter:
                where_filter["emotion"] = emotion_filter
            
            # 查询向量数据库（多检索一些，再过滤）
            results = self.memory_collection.query(
                query_texts=[query],
                n_results=n_results * 3,
                where=where_filter
            )
            
            # 处理结果
            memories = []
            if results and results.get("documents") and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
                    distance = results["distances"][0][i] if results.get("distances") else 1.0
                    
                    # 解析时间戳
                    timestamp_str = metadata.get("timestamp", "")
                    try:
                        memory_time = datetime.fromisoformat(timestamp_str)
                        days_ago = (datetime.now() - memory_time).days
                    except:
                        days_ago = 0
                    
                    # 时间限制过滤
                    if days_limit and days_ago > days_limit:
                        continue
                    
                    # 计算相似度
                    similarity = 1 - (distance / 2)
                    if similarity < 0.25:  # 相似度阈值
                        continue
                    
                    # 获取原始重要性
                    original_importance = float(metadata.get("importance", 0.5))
                    
                    # 应用时间衰减
                    if enable_decay:
                        # 但对标记为重要的记忆，衰减速度更慢
                        decay_rate = 0.95 if original_importance > 0.7 else 0.9
                        current_importance = self.decay_calculator.decay_score(
                            original_importance, 
                            days_ago,
                            decay_rate
                        )
                    else:
                        current_importance = original_importance
                    
                    # 重要性过滤
                    if current_importance < min_importance:
                        continue
                    
                    # 计算综合分数（重要性40% + 相似度60%）
                    final_score = current_importance * 0.4 + similarity * 0.6
                    
                    memories.append({
                        "id": results["ids"][0][i] if results.get("ids") else "",
                        "content": doc,
                        "type": metadata.get("type", "other"),
                        "emotion": metadata.get("emotion", "neutral"),
                        "intensity": float(metadata.get("intensity", 5.0)),
                        "importance": current_importance,
                        "original_importance": original_importance,
                        "timestamp": timestamp_str,
                        "days_ago": days_ago,
                        "similarity": similarity,
                        "final_score": final_score,
                        "extraction_method": metadata.get("extraction_method", "unknown")
                    })
            
            # 按综合分数排序
            memories.sort(key=lambda x: x["final_score"], reverse=True)
            
            # 更新访问统计
            if memories:
                await self._update_access_stats([m["id"] for m in memories[:n_results]])
            
            return memories[:n_results]
            
        except Exception as e:
            print(f"检索记忆失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def _update_access_stats(self, memory_ids: List[str]):
        """更新记忆的访问统计"""
        try:
            with DatabaseManager() as db:
                for memory_id in memory_ids:
                    memory_item = db.db.query(MemoryItem).filter(
                        MemoryItem.memory_id == memory_id
                    ).first()
                    
                    if memory_item:
                        memory_item.access_count += 1
                        memory_item.last_accessed = datetime.utcnow()
                
                db.db.commit()
        except Exception as e:
            print(f"更新访问统计失败: {e}")
    
    async def get_important_memories(self, 
                                    user_id: str, 
                                    limit: int = 10,
                                    min_importance: float = 0.6) -> List[Dict[str, Any]]:
        """
        获取用户最重要的记忆
        
        Args:
            user_id: 用户ID
            limit: 返回数量
            min_importance: 最小重要性阈值
            
        Returns:
            重要记忆列表
        """
        try:
            with DatabaseManager() as db:
                memories = db.db.query(MemoryItem).filter(
                    MemoryItem.user_id == user_id,
                    MemoryItem.is_active == True,
                    MemoryItem.importance >= min_importance
                ).order_by(
                    MemoryItem.importance.desc(),
                    MemoryItem.access_count.desc()
                ).limit(limit).all()
                
                return [
                    {
                        "id": m.memory_id,
                        "content": m.content,
                        "summary": m.summary,
                        "type": m.memory_type,
                        "emotion": m.emotion,
                        "intensity": m.emotion_intensity,
                        "importance": m.importance,
                        "access_count": m.access_count,
                        "created_at": m.created_at.isoformat() if m.created_at else None,
                        "last_accessed": m.last_accessed.isoformat() if m.last_accessed else None
                    }
                    for m in memories
                ]
        except Exception as e:
            print(f"获取重要记忆失败: {e}")
            return []
    
    def get_short_term_context(self, 
                              history: List[Dict[str, Any]],
                              important_markers: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        """
        获取短期记忆上下文
        
        Args:
            history: 完整对话历史
            important_markers: 重要对话索引
            
        Returns:
            裁剪后的对话历史
        """
        return self.short_term.truncate_conversation(history, important_markers)

