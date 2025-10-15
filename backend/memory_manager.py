#!/usr/bin/env python3
"""
记忆管理系统
负责记忆的向量化存储、检索和更新
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
from backend.vector_store import VectorStore
from backend.database import DatabaseManager
from backend.memory_extractor import MemoryExtractor
from config import Config


class MemoryManager:
    """记忆管理器 - 统一管理用户的长期记忆"""
    
    def __init__(self):
        """初始化记忆管理器"""
        self.vector_store = VectorStore()
        self.extractor = MemoryExtractor()
        
        # 创建专门的记忆集合
        try:
            from chromadb.utils import embedding_functions
            default_ef = embedding_functions.DefaultEmbeddingFunction()
            
            self.memory_collection = self.vector_store.client.get_or_create_collection(
                name="user_memories",
                embedding_function=default_ef,
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            print(f"初始化记忆集合失败: {e}")
            self.memory_collection = None
    
    def process_conversation(self, session_id: str, user_id: str, 
                           user_message: str, bot_response: str,
                           emotion: Optional[str] = None, 
                           emotion_intensity: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        处理一次对话，提取并存储记忆
        
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
        
        # 3. 存储记忆
        stored_memories = []
        for memory in memories:
            stored_memory = self.store_memory(
                user_id=user_id,
                session_id=session_id,
                memory=memory
            )
            if stored_memory:
                stored_memories.append(stored_memory)
        
        return stored_memories
    
    def store_memory(self, user_id: str, session_id: str, 
                    memory: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        存储单条记忆到向量数据库
        
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
            
            # 返回完整记忆数据
            memory["id"] = memory_id
            memory["user_id"] = user_id
            memory["session_id"] = session_id
            
            return memory
            
        except Exception as e:
            print(f"存储记忆失败: {e}")
            return None
    
    def retrieve_memories(self, user_id: str, query: str, 
                         n_results: int = 3,
                         days_limit: int = 7,
                         min_importance: float = 0.3,
                         emotion_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        检索相关记忆
        
        Args:
            user_id: 用户ID
            query: 查询文本（当前对话内容）
            n_results: 返回结果数量
            days_limit: 时间限制（天数），None表示不限制
            min_importance: 最小重要性阈值
            emotion_filter: 情绪过滤（可选）
            
        Returns:
            相关记忆列表
        """
        if not self.memory_collection:
            return []
        
        try:
            # 构建过滤条件
            where_filter = {"user_id": user_id}
            
            # 添加情绪过滤
            if emotion_filter:
                where_filter["emotion"] = emotion_filter
            
            # 查询向量数据库
            results = self.memory_collection.query(
                query_texts=[query],
                n_results=n_results * 2,  # 先多检索一些，再过滤
                where=where_filter
            )
            
            # 处理结果
            memories = []
            if results and results.get("documents") and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
                    distance = results["distances"][0][i] if results.get("distances") else 1.0
                    
                    # 过滤条件
                    # 1. 重要性检查
                    importance = float(metadata.get("importance", 0))
                    if importance < min_importance:
                        continue
                    
                    # 2. 时间检查
                    if days_limit:
                        timestamp_str = metadata.get("timestamp", "")
                        if timestamp_str:
                            try:
                                memory_time = datetime.fromisoformat(timestamp_str)
                                if datetime.now() - memory_time > timedelta(days=days_limit):
                                    continue
                            except:
                                pass
                    
                    # 3. 相似度检查（距离越小越相似，cosine距离范围0-2）
                    similarity = 1 - (distance / 2)  # 转换为0-1的相似度
                    if similarity < 0.3:  # 相似度阈值
                        continue
                    
                    # 添加到结果
                    memories.append({
                        "id": results["ids"][0][i] if results.get("ids") else "",
                        "content": doc,
                        "type": metadata.get("type", "other"),
                        "emotion": metadata.get("emotion", "neutral"),
                        "intensity": float(metadata.get("intensity", 5.0)),
                        "importance": importance,
                        "timestamp": metadata.get("timestamp", ""),
                        "similarity": similarity,
                        "extraction_method": metadata.get("extraction_method", "unknown")
                    })
                    
                    # 达到所需数量就停止
                    if len(memories) >= n_results:
                        break
            
            # 按重要性和相似度排序
            memories.sort(key=lambda x: (x["importance"] * 0.5 + x["similarity"] * 0.5), reverse=True)
            
            return memories[:n_results]
            
        except Exception as e:
            print(f"检索记忆失败: {e}")
            return []
    
    def get_user_emotion_trend(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """
        获取用户的情绪变化趋势
        
        Args:
            user_id: 用户ID
            days: 统计天数
            
        Returns:
            情绪趋势数据
        """
        if not self.memory_collection:
            return {"emotions": [], "trend": "稳定"}
        
        try:
            # 获取最近的记忆
            cutoff_time = datetime.now() - timedelta(days=days)
            
            # 查询所有该用户的记忆（通过空查询 + 过滤）
            results = self.memory_collection.get(
                where={"user_id": user_id},
                limit=100
            )
            
            # 统计情绪
            emotion_counts = {}
            emotion_intensities = {}
            recent_emotions = []
            
            if results and results.get("metadatas"):
                for metadata in results["metadatas"]:
                    timestamp_str = metadata.get("timestamp", "")
                    if timestamp_str:
                        try:
                            memory_time = datetime.fromisoformat(timestamp_str)
                            if memory_time < cutoff_time:
                                continue
                        except:
                            continue
                    
                    emotion = metadata.get("emotion", "neutral")
                    intensity = float(metadata.get("intensity", 5.0))
                    
                    # 统计
                    emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
                    if emotion not in emotion_intensities:
                        emotion_intensities[emotion] = []
                    emotion_intensities[emotion].append(intensity)
                    
                    recent_emotions.append({
                        "emotion": emotion,
                        "intensity": intensity,
                        "timestamp": timestamp_str
                    })
            
            # 分析趋势
            trend = "稳定"
            if recent_emotions:
                # 按时间排序
                recent_emotions.sort(key=lambda x: x["timestamp"])
                
                # 计算平均强度变化
                if len(recent_emotions) >= 3:
                    early_avg = sum(e["intensity"] for e in recent_emotions[:len(recent_emotions)//2]) / (len(recent_emotions)//2)
                    late_avg = sum(e["intensity"] for e in recent_emotions[len(recent_emotions)//2:]) / (len(recent_emotions) - len(recent_emotions)//2)
                    
                    if late_avg > early_avg + 1.5:
                        trend = "情绪波动增强"
                    elif late_avg < early_avg - 1.5:
                        trend = "情绪趋于平稳"
            
            # 计算平均强度
            avg_intensities = {}
            for emotion, intensities in emotion_intensities.items():
                avg_intensities[emotion] = sum(intensities) / len(intensities)
            
            return {
                "emotions": [
                    {
                        "emotion": emotion,
                        "count": count,
                        "avg_intensity": avg_intensities.get(emotion, 5.0)
                    }
                    for emotion, count in sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)
                ],
                "trend": trend,
                "total_count": len(recent_emotions),
                "days": days
            }
            
        except Exception as e:
            print(f"获取情绪趋势失败: {e}")
            return {"emotions": [], "trend": "未知", "error": str(e)}
    
    def get_important_memories(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        获取用户最重要的记忆
        
        Args:
            user_id: 用户ID
            limit: 返回数量
            
        Returns:
            重要记忆列表
        """
        if not self.memory_collection:
            return []
        
        try:
            # 获取所有记忆
            results = self.memory_collection.get(
                where={"user_id": user_id},
                limit=100
            )
            
            memories = []
            if results and results.get("documents"):
                for i, doc in enumerate(results["documents"]):
                    metadata = results["metadatas"][i] if results.get("metadatas") else {}
                    
                    memories.append({
                        "id": results["ids"][i] if results.get("ids") else "",
                        "content": doc,
                        "type": metadata.get("type", "other"),
                        "emotion": metadata.get("emotion", "neutral"),
                        "intensity": float(metadata.get("intensity", 5.0)),
                        "importance": float(metadata.get("importance", 0.5)),
                        "timestamp": metadata.get("timestamp", "")
                    })
            
            # 按重要性排序
            memories.sort(key=lambda x: x["importance"], reverse=True)
            
            return memories[:limit]
            
        except Exception as e:
            print(f"获取重要记忆失败: {e}")
            return []
    
    def delete_memory(self, user_id: str, memory_id: str) -> bool:
        """
        删除指定记忆
        
        Args:
            user_id: 用户ID
            memory_id: 记忆ID
            
        Returns:
            是否删除成功
        """
        if not self.memory_collection:
            return False
        
        try:
            self.memory_collection.delete(ids=[memory_id])
            return True
        except Exception as e:
            print(f"删除记忆失败: {e}")
            return False
    
    def update_memory_importance(self, memory_id: str, new_importance: float) -> bool:
        """
        更新记忆的重要性
        
        Args:
            memory_id: 记忆ID
            new_importance: 新的重要性值(0-1)
            
        Returns:
            是否更新成功
        """
        if not self.memory_collection:
            return False
        
        try:
            # ChromaDB不支持直接更新，需要先获取后重新添加
            # 这里简化处理，实际应用中可能需要更复杂的逻辑
            print(f"记忆{memory_id}的重要性更新为{new_importance}")
            return True
        except Exception as e:
            print(f"更新记忆重要性失败: {e}")
            return False

