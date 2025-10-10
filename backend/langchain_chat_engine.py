#!/usr/bin/env python3
"""
基于LangChain的完整聊天引擎
参考: https://github.com/congde/emotional_chat.git
"""
import os
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferMemory
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

# 数据库和模型
from backend.database import DatabaseManager, create_tables
from backend.models import ChatRequest, ChatResponse

class EmotionalChatEngine:
    def __init__(self):
        # 检查 OpenAI API Key 是否设置
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        # 初始化OpenAI模型
        self.llm = ChatOpenAI(
            model="gpt-5-chat",
            temperature=0.7,
            api_key=api_key
        )
        
        # 创建数据库表
        create_tables()
        
        # 初始化向量数据库（长期记忆）
        self.vectorstore = Chroma(
            persist_directory="./memory_db",
            embedding_function=OpenAIEmbeddings(api_key=api_key)
        )
        
        # 会话级别的短期记忆管理器（字典：session_id -> ConversationBufferMemory）
        self.session_memories: Dict[str, ConversationBufferMemory] = {}
        
        # 定义AI人格与行为准则
        self.template = """
你是一位温暖、耐心的心理健康陪伴助手，名叫"心语"。
你的任务是倾听用户的情绪，给予共情和支持，避免说教或直接给建议。
请用中文回复，语气柔和，适当使用表情符号（如😊）。

===== 长期记忆（过往重要对话片段）=====
{long_term_memory}

===== 当前会话对话历史 =====
{history}

用户：{input}
助手：
"""
        
        # 创建提示模板和链
        self.prompt = ChatPromptTemplate.from_template(self.template)
        self.output_parser = StrOutputParser()
        self.chain = self.prompt | self.llm | self.output_parser
        
        # 情感关键词映射
        self.emotion_keywords = {
            "happy": ["开心", "高兴", "快乐", "兴奋", "满意", "幸福", "😊", "😄", "🎉"],
            "sad": ["难过", "伤心", "沮丧", "失落", "痛苦", "抑郁", "😢", "😭", "💔"],
            "angry": ["愤怒", "生气", "恼火", "愤怒", "暴躁", "😠", "😡", "🔥"],
            "anxious": ["焦虑", "担心", "紧张", "不安", "恐惧", "😰", "😨", "😟"],
            "excited": ["兴奋", "激动", "期待", "迫不及待", "兴奋", "🎊", "✨", "🚀"],
            "confused": ["困惑", "迷茫", "不明白", "不懂", "疑惑", "😕", "🤔", "❓"],
            "frustrated": ["沮丧", "挫败", "失望", "无奈", "😤", "😩", "😒"],
            "lonely": ["孤独", "寂寞", "孤单", "😔", "😞", "💭"],
            "grateful": ["感谢", "感激", "谢谢", "🙏", "💝", "❤️"]
        }
        
        # 安全过滤词汇
        self.blocked_words = ["自杀", "自残", "杀人", "爆炸", "暴力", "伤害"]
    
    def analyze_emotion(self, message: str) -> Dict[str, Any]:
        """分析用户消息的情感"""
        message_lower = message.lower()
        
        emotion_scores = {}
        for emotion, keywords in self.emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > 0:
                emotion_scores[emotion] = score
        
        if emotion_scores:
            dominant_emotion = max(emotion_scores, key=emotion_scores.get)
            intensity = min(emotion_scores[dominant_emotion] * 2, 10)
        else:
            dominant_emotion = "neutral"
            intensity = 5
        
        suggestions = self._get_emotion_suggestions(dominant_emotion)
        
        return {
            "emotion": dominant_emotion,
            "intensity": intensity,
            "keywords": self.emotion_keywords.get(dominant_emotion, []),
            "suggestions": suggestions
        }
    
    def _get_emotion_suggestions(self, emotion: str) -> List[str]:
        """根据情感类型获取建议"""
        suggestions_map = {
            "happy": [
                "很高兴看到你这么开心！有什么特别的事情想要分享吗？",
                "你的快乐感染了我！让我们一起保持这种积极的状态吧！",
                "太棒了！有什么秘诀让心情保持这么好的吗？"
            ],
            "sad": [
                "我理解你现在的心情，每个人都会有难过的时刻。",
                "可以告诉我发生了什么吗？我愿意倾听。",
                "虽然现在很难过，但这些感受都是正常的，你并不孤单。"
            ],
            "angry": [
                "我能感受到你的愤怒，让我们先深呼吸一下。",
                "是什么事情让你感到愤怒？我们可以一起分析一下。",
                "愤怒是正常的情绪，重要的是如何表达和处理它。"
            ],
            "anxious": [
                "焦虑确实让人感到不安，让我们一起面对它。",
                "可以告诉我你在担心什么吗？有时候说出来会好很多。",
                "深呼吸，我们可以一步一步来解决你担心的问题。"
            ],
            "excited": [
                "你的兴奋很有感染力！有什么好事要发生了吗？",
                "兴奋的感觉真棒！让我们一起期待美好的事情！",
                "看到你这么兴奋，我也跟着开心起来了！"
            ],
            "confused": [
                "困惑是学习过程中的正常现象，我们一起理清思路。",
                "可以具体告诉我哪里让你感到困惑吗？",
                "慢慢来，我们可以一步步分析，直到你完全理解。"
            ],
            "frustrated": [
                "挫败感确实让人沮丧，但这也是成长的一部分。",
                "让我们换个角度思考这个问题，也许能找到新的解决方案。",
                "你已经很努力了，偶尔的挫折不代表失败。"
            ],
            "lonely": [
                "孤独的感觉确实不好受，但你并不孤单，我在这里。",
                "孤独时，我们往往会想到很多，想聊聊你的想法吗？",
                "有时候我们需要独处，但如果你需要陪伴，我随时在这里。"
            ],
            "grateful": [
                "感恩的心很美好，感谢你愿意分享这份美好。",
                "感恩能让我们更加珍惜身边的一切。",
                "你的感恩之心让我也很感动，谢谢你的分享。"
            ],
            "neutral": [
                "今天感觉怎么样？有什么想聊的吗？",
                "我在这里倾听，无论你想说什么都可以。",
                "有时候平淡的日子也很珍贵，不是吗？"
            ]
        }
        return suggestions_map.get(emotion, suggestions_map["neutral"])
    
    def is_safe_input(self, text: str) -> tuple[bool, str]:
        """安全检查"""
        for word in self.blocked_words:
            if word in text:
                return False, f"检测到高风险词汇，请联系专业心理咨询师。紧急求助电话：400-161-9995（希望24热线）"
        return True, ""
    
    def save_memory(self, user_id: str, content: str, metadata: Dict = None):
        """存储记忆片段到向量数据库"""
        doc = Document(
            page_content=content,
            metadata=metadata or {"user_id": user_id, "timestamp": datetime.now().isoformat()}
        )
        self.vectorstore.add_documents([doc])
    
    def retrieve_memories(self, query: str, user_id: str, k: int = 3) -> List[str]:
        """检索相关长期记忆"""
        try:
            results = self.vectorstore.similarity_search(
                query, 
                k=k, 
                filter={"user_id": user_id}
            )
            return [r.page_content for r in results]
        except Exception as e:
            print(f"检索记忆失败: {e}")
            return []
    
    def get_or_create_session_memory(self, session_id: str) -> ConversationBufferMemory:
        """获取或创建会话级别的对话记忆"""
        if session_id not in self.session_memories:
            # 创建新的会话记忆
            memory = ConversationBufferMemory(
                memory_key="history",
                return_messages=False,
                ai_prefix="心语",
                human_prefix="用户"
            )
            
            # 从数据库加载历史消息
            with DatabaseManager() as db:
                recent_messages = db.get_session_messages(session_id, limit=10)
                for msg in reversed(recent_messages):
                    if msg.role == "user":
                        memory.chat_memory.add_user_message(msg.content)
                    elif msg.role == "assistant":
                        memory.chat_memory.add_ai_message(msg.content)
            
            self.session_memories[session_id] = memory
        
        return self.session_memories[session_id]
    
    def clear_session_memory(self, session_id: str):
        """清除会话记忆（可用于重置对话）"""
        if session_id in self.session_memories:
            del self.session_memories[session_id]
    
    def summarize_long_memory(self, session_id: str) -> Optional[str]:
        """对过长的会话记忆进行总结压缩"""
        memory = self.session_memories.get(session_id)
        if not memory:
            return None
        
        messages = memory.chat_memory.messages
        if len(messages) > 20:  # 超过20条消息时进行总结
            # 构建总结提示
            conversation_text = "\n".join([
                f"{'用户' if i % 2 == 0 else '心语'}: {msg.content}"
                for i, msg in enumerate(messages[:10])
            ])
            
            summary_prompt = f"""
请简要总结以下对话的核心要点和用户的主要情绪状态（不超过150字）：

{conversation_text}

总结：
"""
            try:
                summary = self.llm.predict(summary_prompt)
                return summary
            except Exception as e:
                print(f"总结记忆失败: {e}")
                return None
        return None
    
    def get_response(self, user_input: str, user_id: str, session_id: str) -> str:
        """生成回应（增强版上下文记忆）"""
        # 安全检查
        is_safe, warning = self.is_safe_input(user_input)
        if not is_safe:
            return warning
        
        # 1. 获取会话短期记忆
        session_memory = self.get_or_create_session_memory(session_id)
        
        # 2. 检索长期记忆（向量数据库）
        long_term_memories = self.retrieve_memories(user_input, user_id, k=3)
        long_term_context = "\n".join([f"- {mem}" for mem in long_term_memories]) if long_term_memories else "暂无相关历史记忆"
        
        # 3. 获取会话历史
        history_text = session_memory.load_memory_variables({}).get("history", "")
        
        # 4. 检查是否需要总结（记忆管理）
        summary = self.summarize_long_memory(session_id)
        if summary:
            # 如果有总结，可以在上下文中添加总结信息
            history_text = f"[对话总结]: {summary}\n\n{history_text}"
        
        # 5. 生成回应
        try:
            response = self.chain.invoke({
                "long_term_memory": long_term_context,
                "history": history_text,
                "input": user_input
            })
            
            # 6. 将新的对话添加到会话记忆
            session_memory.save_context(
                {"input": user_input},
                {"output": response}
            )
            
            return response
        except Exception as e:
            print(f"生成回应失败: {e}")
            return "抱歉，我现在无法回应。请稍后再试。"
    
    def chat(self, request: ChatRequest) -> ChatResponse:
        """处理聊天请求"""
        session_id = request.session_id or str(uuid.uuid4())
        user_id = request.user_id or "anonymous"
        
        # 分析情感
        emotion_data = self.analyze_emotion(request.message)
        
        # 保存用户消息到数据库
        with DatabaseManager() as db:
            user_message = db.save_message(
                session_id=session_id,
                user_id=user_id,
                role="user",
                content=request.message,
                emotion=emotion_data["emotion"],
                emotion_intensity=emotion_data["intensity"]
            )
            
            # 保存情感分析结果
            db.save_emotion_analysis(
                session_id=session_id,
                user_id=user_id,
                message_id=user_message.id,
                emotion=emotion_data["emotion"],
                intensity=emotion_data["intensity"],
                keywords=emotion_data["keywords"],
                suggestions=emotion_data["suggestions"]
            )
        
        # 生成回应
        response_text = self.get_response(request.message, user_id, session_id)
        
        # 保存助手消息到数据库
        with DatabaseManager() as db:
            assistant_message = db.save_message(
                session_id=session_id,
                user_id=user_id,
                role="assistant",
                content=response_text,
                emotion="empathetic"
            )
        
        # 保存对话到长期记忆
        conversation_text = f"用户: {request.message}\n心语: {response_text}"
        self.save_memory(user_id, conversation_text, {
            "session_id": session_id,
            "emotion": emotion_data["emotion"]
        })
        
        return ChatResponse(
            response=response_text,
            session_id=session_id,
            emotion=emotion_data["emotion"],
            suggestions=emotion_data["suggestions"][:3]
        )
    
    def get_session_summary(self, session_id: str) -> Dict:
        """获取会话摘要"""
        with DatabaseManager() as db:
            messages = db.get_session_messages(session_id)
            
            if not messages:
                return {"error": "会话不存在"}
            
            # 统计情感分布
            emotion_counts = {}
            for msg in messages:
                if msg.emotion:
                    emotion_counts[msg.emotion] = emotion_counts.get(msg.emotion, 0) + 1
            
            return {
                "session_id": session_id,
                "message_count": len(messages),
                "emotion_distribution": emotion_counts,
                "created_at": messages[-1].created_at.isoformat() if messages else None,
                "updated_at": messages[0].created_at.isoformat() if messages else None
            }
    
    def get_user_emotion_trends(self, user_id: str) -> Dict:
        """获取用户情感趋势"""
        with DatabaseManager() as db:
            emotion_history = db.get_user_emotion_history(user_id, limit=100)
            
            if not emotion_history:
                return {"error": "没有情感数据"}
            
            # 分析情感趋势
            emotions = [e.emotion for e in emotion_history]
            intensities = [e.intensity for e in emotion_history]
            
            return {
                "user_id": user_id,
                "total_records": len(emotion_history),
                "recent_emotions": emotions[:10],
                "average_intensity": sum(intensities) / len(intensities) if intensities else 0,
                "emotion_counts": {emotion: emotions.count(emotion) for emotion in set(emotions)}
            }
    
    def get_memory_stats(self, session_id: str) -> Dict:
        """获取会话记忆统计信息"""
        memory = self.session_memories.get(session_id)
        if not memory:
            return {
                "session_id": session_id,
                "status": "no_active_memory",
                "message_count": 0
            }
        
        messages = memory.chat_memory.messages
        return {
            "session_id": session_id,
            "status": "active",
            "message_count": len(messages),
            "memory_size": len(memory.load_memory_variables({}).get("history", "")),
            "needs_summary": len(messages) > 20
        }
    
    def export_conversation_history(self, session_id: str) -> Dict:
        """导出完整的对话历史（包括短期和长期记忆）"""
        result = {
            "session_id": session_id,
            "exported_at": datetime.now().isoformat()
        }
        
        # 1. 获取短期记忆（当前会话）
        memory = self.session_memories.get(session_id)
        if memory:
            result["current_session"] = memory.load_memory_variables({}).get("history", "")
        
        # 2. 从数据库获取完整历史
        with DatabaseManager() as db:
            messages = db.get_session_messages(session_id)
            result["total_messages"] = len(messages)
            result["messages"] = [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "emotion": msg.emotion,
                    "timestamp": msg.created_at.isoformat()
                }
                for msg in messages
            ]
        
        return result
