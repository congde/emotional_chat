#!/usr/bin/env python3
"""
聊天服务层
处理所有与聊天相关的业务逻辑
"""

from typing import Dict, Optional, Any, List
# 优先使用带插件支持的引擎
try:
    from backend.modules.llm.core.llm_with_plugins import EmotionalChatEngineWithPlugins
    PLUGIN_ENGINE_AVAILABLE = True
except ImportError:
    PLUGIN_ENGINE_AVAILABLE = False
    EmotionalChatEngineWithPlugins = None

from backend.modules.llm.core.llm_core import SimpleEmotionalChatEngine
from backend.services.memory_service import MemoryService
from backend.services.context_service import ContextService
from backend.models import ChatRequest, ChatResponse
from backend.database import DatabaseManager, ChatSession
import uuid
from datetime import datetime

# 尝试导入RAG服务（可选功能）
try:
    from backend.modules.rag.services.rag_service import RAGIntegrationService
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    RAGIntegrationService = None

# 尝试导入意图识别服务（可选功能）
try:
    from backend.modules.intent.services import IntentService
    INTENT_AVAILABLE = True
except ImportError:
    INTENT_AVAILABLE = False
    IntentService = None

# 导入增强版输入处理器
try:
    from backend.modules.intent.core.enhanced_input_processor import EnhancedInputProcessor
    ENHANCED_PROCESSOR_AVAILABLE = True
except ImportError:
    ENHANCED_PROCESSOR_AVAILABLE = False
    EnhancedInputProcessor = None


class ChatService:
    """聊天服务 - 统一的聊天接口"""
    
    def __init__(
        self,
        memory_service: Optional[MemoryService] = None,
        context_service: Optional[ContextService] = None,
        use_rag: bool = True,
        use_intent: bool = True,
        use_enhanced_processor: bool = True
    ):
        """
        初始化聊天服务
        
        Args:
            memory_service: 记忆服务
            context_service: 上下文服务
            use_rag: 是否启用RAG知识库功能
            use_intent: 是否启用意图识别功能
            use_enhanced_processor: 是否启用增强版输入处理器
        """
        # 优先使用带插件支持的引擎（支持天气查询等功能）
        if PLUGIN_ENGINE_AVAILABLE:
            try:
                self.chat_engine = EmotionalChatEngineWithPlugins()
                print("✓ 使用带插件支持的聊天引擎（支持天气查询等功能）")
            except Exception as e:
                print(f"⚠ 插件引擎初始化失败，使用常规引擎: {e}")
                self.chat_engine = SimpleEmotionalChatEngine()
        else:
            self.chat_engine = SimpleEmotionalChatEngine()
            print("⚠ 插件引擎不可用，使用常规引擎")
        self.memory_service = memory_service or MemoryService()
        self.context_service = context_service or ContextService(memory_service=self.memory_service)
        
        # 初始化增强版输入处理器（如果可用且启用）
        self.enhanced_processor_enabled = False
        self.enhanced_processor = None
        if use_enhanced_processor and ENHANCED_PROCESSOR_AVAILABLE:
            try:
                self.enhanced_processor = EnhancedInputProcessor(
                    enable_jieba=True,  # 启用分词
                    enable_duplicate_check=True  # 启用重复检测
                )
                self.enhanced_processor_enabled = True
                print("✓ 增强版输入处理器已启用")
            except Exception as e:
                print(f"⚠ 增强版输入处理器初始化失败: {e}")
        else:
            if not ENHANCED_PROCESSOR_AVAILABLE:
                print("⚠ 增强版输入处理器不可用")
        
        # 初始化RAG服务（如果可用且启用）
        self.rag_enabled = False
        self.rag_service = None
        if use_rag and RAG_AVAILABLE:
            try:
                self.rag_service = RAGIntegrationService()
                # 检查知识库是否可用
                if self.rag_service.rag_service.is_knowledge_available():
                    self.rag_enabled = True
                    print("✓ RAG知识库已启用")
                else:
                    print("⚠ RAG服务已加载，但知识库未初始化")
            except Exception as e:
                print(f"⚠ RAG服务初始化失败: {e}")
        else:
            if not RAG_AVAILABLE:
                print("⚠ RAG模块不可用（需要安装相关依赖）")
        
        # 初始化意图识别服务（如果可用且启用）
        self.intent_enabled = False
        self.intent_service = None
        if use_intent and INTENT_AVAILABLE:
            try:
                self.intent_service = IntentService()
                self.intent_enabled = True
                print("✓ 意图识别系统已启用")
            except Exception as e:
                print(f"⚠ 意图识别服务初始化失败: {e}")
        else:
            if not INTENT_AVAILABLE:
                print("⚠ 意图识别模块不可用")
    
    async def chat(
        self,
        request: ChatRequest,
        use_memory_system: bool = True
    ) -> ChatResponse:
        """
        处理聊天请求（支持记忆系统）
        
        Args:
            request: 聊天请求
            use_memory_system: 是否启用记忆系统
            
        Returns:
            聊天响应
        """
        # 生成会话ID（如果没有）
        if not request.session_id:
            request.session_id = str(uuid.uuid4())
        
        # 如果启用记忆系统
        if use_memory_system:
            return await self._chat_with_memory(request)
        else:
            # 使用原有引擎（无记忆）
            return self.chat_engine.chat(request)
    
    async def _chat_with_memory(self, request: ChatRequest) -> ChatResponse:
        """使用记忆系统的聊天"""
        user_id = request.user_id or "anonymous"
        session_id = request.session_id
        message = request.message
        
        # 0. 增强版输入预处理（第一步）
        preprocessed = None
        if self.enhanced_processor_enabled and self.enhanced_processor:
            try:
                preprocessed = self.enhanced_processor.preprocess(message, user_id)
                
                # 检查是否被阻止
                if preprocessed["blocked"]:
                    return ChatResponse(
                        response=preprocessed.get("friendly_message", "输入无效，请重新输入"),
                        emotion="neutral",
                        session_id=session_id,
                        timestamp=datetime.now(),
                        context={
                            "blocked": True,
                            "reason": preprocessed["warnings"],
                            "input_validation": "failed"
                        }
                    )
                
                # 使用清洗后的文本
                message = preprocessed["cleaned"]
                
                # 如果检测到重复且频率过高，可以提供特殊提示
                if preprocessed["metadata"].get("high_frequency_repeat"):
                    print(f"⚠️ 用户 {user_id} 高频重复输入: {message[:30]}...")
                
            except Exception as e:
                print(f"输入预处理失败，使用原始消息: {e}")
                preprocessed = None
        
        # 1. 分析情绪（使用清洗后的消息）
        emotion_result = self.chat_engine.analyze_emotion(message)
        emotion = emotion_result.get("emotion", "neutral")
        emotion_intensity = emotion_result.get("intensity", 5.0)
        
        # 2. 意图识别（如果启用）
        intent_result = None
        if self.intent_enabled and self.intent_service:
            try:
                intent_analysis = self.intent_service.analyze(message, user_id)
                intent_result = intent_analysis.get('intent', {})
                
                # 检查是否需要特殊处理（危机情况）
                if intent_analysis.get('action_required', False):
                    print(f"⚠️ 检测到用户 {user_id} 的危机情况，意图: {intent_result.get('intent')}")
                    # 这里可以触发特殊的危机响应流程
                    
            except Exception as e:
                print(f"意图识别失败: {e}")
                intent_result = None
        
        # 3. 构建上下文（包含记忆）
        context = await self.context_service.build_context(
            user_id=user_id,
            session_id=session_id,
            current_message=message,
            emotion=emotion,
            emotion_intensity=emotion_intensity
        )
        
        # 将意图信息添加到上下文中
        if intent_result:
            context['intent'] = intent_result
        
        # 4. 尝试使用RAG增强回复
        rag_result = None
        print(f"ChatService RAG检查: rag_enabled={self.rag_enabled}, rag_service={self.rag_service is not None}")
        if self.rag_enabled and self.rag_service:
            try:
                print("ChatService尝试使用RAG增强")
                # 获取对话历史
                conversation_history = await self._get_conversation_history(session_id)
                
                # 尝试RAG增强
                rag_result = self.rag_service.enhance_response(
                    message=message,
                    emotion=emotion,
                    conversation_history=conversation_history
                )
                print(f"ChatService RAG结果: {rag_result}")
                
            except Exception as e:
                print(f"RAG增强失败，使用常规回复: {e}")
        else:
            print("ChatService RAG未启用，使用常规引擎")
        
        # 5. 生成回复
        if rag_result and rag_result.get("use_rag"):
            # 使用RAG增强的回复
            response = ChatResponse(
                response=rag_result["answer"],
                emotion=emotion,
                emotion_intensity=emotion_intensity,
                session_id=session_id,
                timestamp=datetime.now()
            )
            # 添加RAG来源信息和预处理信息
            response.context = {
                "memories_count": len(context.get("memories", {}).get("all", [])),
                "emotion_trend": context.get("emotion_context", {}).get("trend", {}).get("trend"),
                "has_profile": bool(context.get("user_profile", {}).get("summary")),
                "used_rag": True,
                "knowledge_sources": len(rag_result.get("sources", [])),
                "intent": intent_result.get('intent') if intent_result else None,
                "intent_confidence": intent_result.get('confidence') if intent_result else None,
                "input_preprocessed": preprocessed is not None,
                "input_metadata": preprocessed.get("metadata") if preprocessed else None
            }
        else:
            # 使用常规引擎回复
            print(f"ChatService使用常规引擎: session_id={session_id}, user_id={user_id}")
            try:
                response = self.chat_engine.chat(request)
                print(f"ChatService常规引擎回复完成: {response.session_id}")
            except Exception as e:
                print(f"ChatService常规引擎调用失败: {e}")
                import traceback
                traceback.print_exc()
                # 创建简单的回复
                response = ChatResponse(
                    response="抱歉，我遇到了一些技术问题，请稍后再试。",
                    session_id=session_id,
                    emotion="neutral",
                    timestamp=datetime.now()
                )
            response.context = {
                "memories_count": len(context.get("memories", {}).get("all", [])),
                "emotion_trend": context.get("emotion_context", {}).get("trend", {}).get("trend"),
                "has_profile": bool(context.get("user_profile", {}).get("summary")),
                "used_rag": False,
                "intent": intent_result.get('intent') if intent_result else None,
                "intent_confidence": intent_result.get('confidence') if intent_result else None,
                "input_preprocessed": preprocessed is not None,
                "input_metadata": preprocessed.get("metadata") if preprocessed else None
            }
        
        # 5.1. 保存会话和消息到数据库（如果RAG分支没有保存）
        # 注意：llm_with_plugins.py 的 chat 方法已经保存了消息，这里不再重复保存
        if rag_result and rag_result.get("use_rag"):
            # RAG分支只需要确保会话存在
            try:
                with DatabaseManager() as db:
                    # 如果是新会话，创建会话记录
                    if not request.session_id:
                        print(f"ChatService创建新会话: {session_id} for user: {user_id}")
                        db.create_session(session_id, user_id)
                        print(f"ChatService会话创建完成")
                    # 消息已经在 llm_with_plugins.py 中保存，这里不再重复保存
                    print(f"ChatService RAG分支：消息已在llm引擎中保存，跳过重复保存")
                    
            except Exception as e:
                print(f"ChatService数据库操作失败: {e}")
                import traceback
                traceback.print_exc()
        
        # 6. 处理并存储记忆
        await self.memory_service.process_and_store_memories(
            session_id=session_id,
            user_id=user_id,
            user_message=message,
            bot_response=response.response,
            emotion=emotion,
            emotion_intensity=emotion_intensity
        )
        
        # 7. 确保会话被保存（如果还没有保存）
        # 注意：消息已经在 llm_with_plugins.py 中保存，这里只确保会话存在
        try:
            with DatabaseManager() as db:
                # 检查会话是否存在
                existing_session = db.db.query(ChatSession).filter(
                    ChatSession.session_id == session_id
                ).first()
                
                if not existing_session:
                    print(f"ChatService手动创建会话: {session_id} for user: {user_id}")
                    db.create_session(session_id, user_id)
                    print(f"ChatService手动会话创建完成")
                    # 消息已经在 llm_with_plugins.py 中保存，这里不再重复保存
                    print(f"ChatService：消息已在llm引擎中保存，跳过重复保存")
                else:
                    print(f"ChatService会话已存在: {session_id}")
                    
        except Exception as e:
            print(f"ChatService手动保存失败: {e}")
            import traceback
            traceback.print_exc()
        
        return response
    
    async def _get_conversation_history(self, session_id: str, limit: int = 5) -> List[Dict[str, str]]:
        """
        获取最近的对话历史（用于RAG上下文）
        
        Args:
            session_id: 会话ID
            limit: 限制数量
            
        Returns:
            对话历史列表
        """
        try:
            with DatabaseManager() as db:
                messages = db.get_session_messages(session_id, limit)
                
                history = []
                for msg in messages:
                    history.append({
                        "role": msg.role,
                        "content": msg.content
                    })
                
                return history
        except Exception as e:
            print(f"获取对话历史失败: {e}")
            return []
    
    async def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """
        获取会话摘要
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话摘要
        """
        return self.chat_engine.get_session_summary(session_id)
    
    async def get_session_history(
        self,
        session_id: str,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        获取会话历史
        
        Args:
            session_id: 会话ID
            limit: 限制数量
            
        Returns:
            会话历史
        """
        try:
            with DatabaseManager() as db:
                messages = db.get_session_messages(session_id, limit)
                
                if not messages:
                    return {
                        "session_id": session_id,
                        "messages": [],
                        "total": 0
                    }
                
                return {
                    "session_id": session_id,
                    "messages": [
                        {
                            "id": msg.id,
                            "role": msg.role,
                            "content": msg.content,
                            "emotion": msg.emotion,
                            "emotion_intensity": msg.emotion_intensity,
                            "timestamp": msg.created_at.isoformat() if msg.created_at else None
                        }
                        for msg in messages
                    ],
                    "total": len(messages)
                }
        except Exception as e:
            print(f"获取会话历史失败: {e}")
            return {
                "session_id": session_id,
                "messages": [],
                "total": 0,
                "error": str(e)
            }
    
    async def get_user_sessions(
        self,
        user_id: str,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        获取用户的所有会话
        
        Args:
            user_id: 用户ID
            limit: 限制数量
            
        Returns:
            会话列表
        """
        try:
            with DatabaseManager() as db:
                from backend.database import ChatMessage
                
                sessions = db.get_user_sessions(user_id, limit)
                
                session_list = []
                for session in sessions:
                    # 检查会话是否有消息
                    message_count = db.db.query(ChatMessage)\
                        .filter(ChatMessage.session_id == session.session_id)\
                        .count()
                    
                    # 如果会话没有消息，跳过（不显示在历史列表中）
                    if message_count == 0:
                        continue
                    
                    # 获取会话的第一条消息作为标题
                    first_message = db.db.query(ChatMessage)\
                        .filter(ChatMessage.session_id == session.session_id)\
                        .filter(ChatMessage.role == 'user')\
                        .order_by(ChatMessage.created_at.asc())\
                        .first()
                    
                    # 获取会话的最后一条消息作为预览
                    last_message = db.db.query(ChatMessage)\
                        .filter(ChatMessage.session_id == session.session_id)\
                        .order_by(ChatMessage.created_at.desc())\
                        .first()
                    
                    title = first_message.content[:30] + "..." if first_message and len(first_message.content) > 30 else (first_message.content if first_message else "新对话")
                    
                    # 生成预览文本（最后一条消息的内容，最多50个字符）
                    preview = ""
                    if last_message:
                        preview = last_message.content[:50] + "..." if len(last_message.content) > 50 else last_message.content
                    
                    session_list.append({
                        "session_id": session.session_id,
                        "title": title,
                        "preview": preview,
                        "message_count": message_count,
                        "created_at": session.created_at.isoformat() if session.created_at else None,
                        "updated_at": session.updated_at.isoformat() if session.updated_at else None
                    })
                
                return {
                    "user_id": user_id,
                    "sessions": session_list,
                    "total": len(session_list)
                }
        except Exception as e:
            print(f"获取用户会话列表失败: {e}")
            return {
                "user_id": user_id,
                "sessions": [],
                "total": 0,
                "error": str(e)
            }
    
    async def delete_session(self, session_id: str) -> bool:
        """
        删除会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            是否成功
        """
        try:
            with DatabaseManager() as db:
                return db.delete_session(session_id)
        except Exception as e:
            print(f"删除会话失败: {e}")
            return False
    
    async def get_user_emotion_trends(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """
        获取用户情绪趋势
        
        Args:
            user_id: 用户ID
            days: 天数
            
        Returns:
            情绪趋势
        """
        return self.chat_engine.get_user_emotion_trends(user_id)

