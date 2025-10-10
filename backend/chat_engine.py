from typing import List, Dict, Any, Optional
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from datetime import datetime
import uuid
import json

from config import Config
from .models import ChatSession, Message, ChatRequest, ChatResponse
from .vector_store import VectorStore
from .emotion_analyzer import EmotionAnalyzer

class EmotionalChatEngine:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=Config.OPENAI_API_KEY,
            model_name=Config.DEFAULT_MODEL,
            temperature=Config.TEMPERATURE,
            max_tokens=Config.MAX_TOKENS
        )
        
        self.vector_store = VectorStore()
        self.emotion_analyzer = EmotionAnalyzer()
        self.sessions: Dict[str, ChatSession] = {}
        
        # 系统提示词
        self.system_prompt = """
        你是一个专业的情感支持聊天机器人，具有以下特点：
        
        1. **情感智能**: 能够识别和理解用户的情感状态，提供共情回应
        2. **温暖专业**: 语调温暖、专业，像一位贴心的朋友
        3. **非评判性**: 不对用户的情感或想法进行评判
        4. **支持导向**: 重点是情感支持和陪伴，而非解决问题
        5. **个性化**: 根据用户的情感状态调整回应风格
        
        回应原则：
        - 承认用户的情感："我能感受到你的..."
        - 提供情感支持："你并不孤单，我在这里陪伴你"
        - 鼓励表达："愿意多分享一些吗？"
        - 避免直接建议，更多是倾听和理解
        
        请用中文回应，保持温暖、真诚的语调。
        """
        
        # 创建对话链
        self.conversation_chain = self._create_conversation_chain()
    
    def _create_conversation_chain(self):
        """创建对话链"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])
        
        memory = ConversationBufferWindowMemory(
            k=10,  # 保留最近10轮对话
            return_messages=True,
            memory_key="history"
        )
        
        chain = ConversationChain(
            llm=self.llm,
            prompt=prompt,
            memory=memory,
            verbose=True
        )
        
        return chain
    
    def get_or_create_session(self, session_id: str = None, user_id: str = None) -> ChatSession:
        """获取或创建会话"""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        if session_id not in self.sessions:
            self.sessions[session_id] = ChatSession(
                session_id=session_id,
                user_id=user_id
            )
        
        return self.sessions[session_id]
    
    def chat(self, request: ChatRequest) -> ChatResponse:
        """处理聊天请求"""
        # 获取或创建会话
        session = self.get_or_create_session(request.session_id, request.user_id)
        
        # 分析用户消息的情感
        emotion_data = self.emotion_analyzer.analyze_emotion(request.message)
        
        # 添加用户消息到会话
        user_message = Message(
            role="user",
            content=request.message,
            emotion=emotion_data.get("emotion")
        )
        session.messages.append(user_message)
        
        # 获取对话历史用于上下文
        conversation_history = self._get_conversation_history(session)
        
        # 搜索相关知识和情感模式
        relevant_knowledge = self._search_relevant_context(request.message, emotion_data)
        
        # 生成回应
        response_text = self._generate_response(
            request.message, 
            emotion_data, 
            conversation_history,
            relevant_knowledge
        )
        
        # 创建助手消息
        assistant_message = Message(
            role="assistant",
            content=response_text,
            emotion="empathetic"
        )
        session.messages.append(assistant_message)
        
        # 更新会话时间
        session.updated_at = datetime.now()
        session.emotion_state = emotion_data
        
        # 存储到向量数据库
        self.vector_store.add_conversation(
            session.session_id,
            request.message,
            response_text,
            emotion_data.get("emotion")
        )
        
        # 生成建议
        suggestions = emotion_data.get("suggestions", [])
        
        return ChatResponse(
            response=response_text,
            session_id=session.session_id,
            emotion=emotion_data.get("emotion"),
            suggestions=suggestions[:3]  # 返回前3个建议
        )
    
    def _get_conversation_history(self, session: ChatSession) -> List[BaseMessage]:
        """获取对话历史"""
        messages = []
        for msg in session.messages[-10:]:  # 最近10条消息
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                messages.append(AIMessage(content=msg.content))
        return messages
    
    def _search_relevant_context(self, message: str, emotion_data: Dict) -> Dict:
        """搜索相关上下文"""
        context = {}
        
        # 搜索相似对话
        similar_conversations = self.vector_store.search_similar_conversations(message)
        if similar_conversations['documents']:
            context['similar_conversations'] = similar_conversations['documents'][0][:2]
        
        # 搜索知识库
        knowledge_results = self.vector_store.search_knowledge(message)
        if knowledge_results['documents']:
            context['knowledge'] = knowledge_results['documents'][0][:2]
        
        # 搜索情感模式
        emotion = emotion_data.get("emotion")
        emotion_patterns = self.vector_store.search_emotion_patterns(message, emotion)
        if emotion_patterns['documents']:
            context['emotion_patterns'] = emotion_patterns['documents'][0][:2]
        
        return context
    
    def _generate_response(self, user_message: str, emotion_data: Dict, 
                          conversation_history: List[BaseMessage], 
                          context: Dict) -> str:
        """生成回应"""
        try:
            # 构建增强的提示
            enhanced_prompt = self._build_enhanced_prompt(
                user_message, emotion_data, context
            )
            
            # 使用对话链生成回应
            response = self.conversation_chain.predict(
                input=enhanced_prompt
            )
            
            return response.strip()
            
        except Exception as e:
            print(f"生成回应出错: {e}")
            # 备选方案：使用情感分析器生成共情回应
            return self.emotion_analyzer.generate_empathetic_response(
                user_message, emotion_data, conversation_history
            )
    
    def _build_enhanced_prompt(self, user_message: str, emotion_data: Dict, context: Dict) -> str:
        """构建增强的提示"""
        emotion = emotion_data.get("emotion", "neutral")
        intensity = emotion_data.get("intensity", 5)
        
        prompt_parts = [f"用户消息: {user_message}"]
        prompt_parts.append(f"情感分析: {emotion} (强度: {intensity}/10)")
        
        # 添加上下文信息
        if context.get('similar_conversations'):
            prompt_parts.append(f"相关对话历史: {'; '.join(context['similar_conversations'])}")
        
        if context.get('knowledge'):
            prompt_parts.append(f"相关知识: {'; '.join(context['knowledge'])}")
        
        if context.get('emotion_patterns'):
            prompt_parts.append(f"情感模式: {'; '.join(context['emotion_patterns'])}")
        
        # 根据情感强度调整回应策略
        if intensity >= 7:
            prompt_parts.append("注意：用户情感强度很高，需要特别关注和共情")
        elif intensity <= 3:
            prompt_parts.append("注意：用户情感较为平静，可以引导更多交流")
        
        return "\n".join(prompt_parts)
    
    def get_session_summary(self, session_id: str) -> Dict:
        """获取会话摘要"""
        if session_id not in self.sessions:
            return {"error": "会话不存在"}
        
        session = self.sessions[session_id]
        
        # 统计情感分布
        emotion_counts = {}
        for message in session.messages:
            if message.emotion:
                emotion_counts[message.emotion] = emotion_counts.get(message.emotion, 0) + 1
        
        return {
            "session_id": session_id,
            "message_count": len(session.messages),
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "emotion_distribution": emotion_counts,
            "current_emotion": session.emotion_state.get("emotion") if session.emotion_state else None
        }
