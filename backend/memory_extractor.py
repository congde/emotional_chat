#!/usr/bin/env python3
"""
记忆提取模块
从对话中提取关键信息，包括情绪、事件、承诺等
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import re
from openai import OpenAI
from config import Config


class MemoryExtractor:
    """记忆提取器 - 从对话中提取重要信息"""
    
    def __init__(self):
        """初始化记忆提取器"""
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        
        # 定义需要提取的记忆类型
        self.memory_types = {
            "emotion": "情绪表达",
            "event": "生活事件",
            "commitment": "承诺/计划",
            "relationship": "人际关系",
            "preference": "偏好/兴趣",
            "concern": "担忧/焦虑"
        }
        
    def extract_memories(self, user_message: str, bot_response: str, 
                        emotion: Optional[str] = None, 
                        emotion_intensity: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        从对话中提取记忆条目
        
        Args:
            user_message: 用户消息
            bot_response: 机器人回复
            emotion: 检测到的情绪
            emotion_intensity: 情绪强度(1-10)
            
        Returns:
            记忆条目列表
        """
        memories = []
        
        # 1. 使用规则提取明显的记忆点
        rule_based_memories = self._extract_by_rules(user_message, emotion, emotion_intensity)
        memories.extend(rule_based_memories)
        
        # 2. 使用LLM提取更复杂的记忆点
        llm_based_memories = self._extract_by_llm(user_message, bot_response, emotion, emotion_intensity)
        memories.extend(llm_based_memories)
        
        # 3. 去重和优先级排序
        memories = self._deduplicate_and_rank(memories)
        
        return memories
    
    def _extract_by_rules(self, message: str, emotion: Optional[str] = None, 
                         intensity: Optional[float] = None) -> List[Dict[str, Any]]:
        """基于规则提取记忆"""
        memories = []
        
        # 规则1: 检测即将发生的事件
        event_patterns = [
            r"明天|后天|下周|下个月|即将|马上|快要",
            r"考试|面试|约会|会议|出差|旅行",
            r"要去|打算|准备|计划"
        ]
        
        for pattern in event_patterns:
            if re.search(pattern, message):
                memories.append({
                    "type": "event",
                    "content": message,
                    "summary": self._summarize_event(message),
                    "emotion": emotion,
                    "intensity": intensity or 5.0,
                    "timestamp": datetime.now().isoformat(),
                    "importance": self._calculate_importance(message, emotion, intensity),
                    "extraction_method": "rule_based"
                })
                break
        
        # 规则2: 检测人际关系
        relationship_keywords = ["男朋友", "女朋友", "父母", "妈妈", "爸爸", "朋友", 
                                "同事", "老板", "分手", "吵架", "和好"]
        if any(keyword in message for keyword in relationship_keywords):
            memories.append({
                "type": "relationship",
                "content": message,
                "summary": self._summarize_relationship(message),
                "emotion": emotion,
                "intensity": intensity or 5.0,
                "timestamp": datetime.now().isoformat(),
                "importance": self._calculate_importance(message, emotion, intensity),
                "extraction_method": "rule_based"
            })
        
        # 规则3: 检测强烈情绪表达
        if intensity and intensity >= 7.0:
            memories.append({
                "type": "emotion",
                "content": message,
                "summary": f"用户表达了强烈的{emotion}情绪",
                "emotion": emotion,
                "intensity": intensity,
                "timestamp": datetime.now().isoformat(),
                "importance": intensity / 10.0,  # 基于强度计算重要性
                "extraction_method": "rule_based"
            })
        
        # 规则4: 检测承诺和计划
        commitment_patterns = [
            r"我会|我要|我打算|我决定|我承诺",
            r"不再|以后|从今天开始"
        ]
        for pattern in commitment_patterns:
            if re.search(pattern, message):
                memories.append({
                    "type": "commitment",
                    "content": message,
                    "summary": self._summarize_commitment(message),
                    "emotion": emotion,
                    "intensity": intensity or 5.0,
                    "timestamp": datetime.now().isoformat(),
                    "importance": 0.8,  # 承诺通常较重要
                    "extraction_method": "rule_based"
                })
                break
        
        # 规则5: 检测担忧和焦虑
        concern_keywords = ["担心", "害怕", "焦虑", "紧张", "不安", "恐惧", "压力"]
        if any(keyword in message for keyword in concern_keywords):
            memories.append({
                "type": "concern",
                "content": message,
                "summary": self._summarize_concern(message),
                "emotion": emotion,
                "intensity": intensity or 6.0,
                "timestamp": datetime.now().isoformat(),
                "importance": 0.7,
                "extraction_method": "rule_based"
            })
        
        return memories
    
    def _extract_by_llm(self, user_message: str, bot_response: str, 
                       emotion: Optional[str] = None, 
                       intensity: Optional[float] = None) -> List[Dict[str, Any]]:
        """使用LLM提取记忆（用于复杂场景）"""
        try:
            prompt = f"""分析以下对话，提取值得记忆的关键信息。

用户消息：{user_message}
机器人回复：{bot_response}
检测到的情绪：{emotion or '未知'}
情绪强度(1-10)：{intensity or 5.0}

请提取以下类型的记忆：
1. 重要的生活事件（考试、面试、分手等）
2. 人际关系变化
3. 用户的承诺或计划
4. 用户的偏好和兴趣
5. 持续性的担忧或焦虑

对于每个记忆，请判断：
- 类型（event/relationship/commitment/preference/concern）
- 简短摘要（一句话）
- 重要性评分（0-1）

以JSON格式返回，格式：
{{
  "memories": [
    {{
      "type": "event",
      "summary": "用户明天有重要考试",
      "importance": 0.9
    }}
  ]
}}

如果没有值得记忆的信息，返回空数组。"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "你是一个专业的记忆提取助手，善于识别对话中的关键信息。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            
            # 尝试解析JSON
            # 移除markdown代码块标记
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            result = json.loads(content)
            
            # 转换为标准格式
            memories = []
            for mem in result.get("memories", []):
                memories.append({
                    "type": mem.get("type", "other"),
                    "content": user_message,
                    "summary": mem.get("summary", ""),
                    "emotion": emotion,
                    "intensity": intensity or 5.0,
                    "timestamp": datetime.now().isoformat(),
                    "importance": mem.get("importance", 0.5),
                    "extraction_method": "llm_based"
                })
            
            return memories
            
        except Exception as e:
            print(f"LLM记忆提取失败: {e}")
            return []
    
    def _summarize_event(self, message: str) -> str:
        """生成事件摘要"""
        # 简单提取关键信息
        words = message[:50]  # 取前50个字符
        return f"即将发生的事件: {words}..."
    
    def _summarize_relationship(self, message: str) -> str:
        """生成人际关系摘要"""
        words = message[:50]
        return f"人际关系: {words}..."
    
    def _summarize_commitment(self, message: str) -> str:
        """生成承诺摘要"""
        words = message[:50]
        return f"用户计划: {words}..."
    
    def _summarize_concern(self, message: str) -> str:
        """生成担忧摘要"""
        words = message[:50]
        return f"用户担忧: {words}..."
    
    def _calculate_importance(self, message: str, emotion: Optional[str], 
                            intensity: Optional[float]) -> float:
        """计算记忆重要性（0-1）"""
        importance = 0.5  # 基础重要性
        
        # 根据情绪强度调整
        if intensity:
            importance += (intensity / 10.0) * 0.3
        
        # 根据消息长度调整
        if len(message) > 50:
            importance += 0.1
        
        # 限制在0-1范围
        return min(max(importance, 0.0), 1.0)
    
    def _deduplicate_and_rank(self, memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重并按重要性排序"""
        if not memories:
            return []
        
        # 简单去重：相同类型的只保留重要性最高的
        unique_memories = {}
        for mem in memories:
            mem_type = mem["type"]
            if mem_type not in unique_memories or mem["importance"] > unique_memories[mem_type]["importance"]:
                unique_memories[mem_type] = mem
        
        # 按重要性排序
        sorted_memories = sorted(unique_memories.values(), 
                               key=lambda x: x["importance"], 
                               reverse=True)
        
        return sorted_memories
    
    def should_extract_memory(self, user_message: str, emotion: Optional[str] = None, 
                            intensity: Optional[float] = None) -> bool:
        """
        判断是否应该从这次对话中提取记忆
        
        Args:
            user_message: 用户消息
            emotion: 情绪
            intensity: 情绪强度
            
        Returns:
            是否应该提取记忆
        """
        # 1. 消息太短，可能不值得记忆
        if len(user_message) < 10:
            return False
        
        # 2. 强烈情绪必须记忆
        if intensity and intensity >= 7.0:
            return True
        
        # 3. 包含关键词
        important_keywords = [
            "考试", "面试", "分手", "吵架", "生病", "住院",
            "明天", "下周", "计划", "打算", "决定",
            "担心", "害怕", "焦虑", "压力"
        ]
        if any(keyword in user_message for keyword in important_keywords):
            return True
        
        # 4. 消息较长且有一定情绪强度
        if len(user_message) > 30 and intensity and intensity >= 5.0:
            return True
        
        return False

