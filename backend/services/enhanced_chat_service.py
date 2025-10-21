#!/usr/bin/env python3
"""
增强版聊天服务
集成所有增强功能：
1. 增强版记忆管理（短期+长期+衰减）
2. 用户画像动态构建
3. 智能上下文组装
4. 主动回忆系统
"""

from typing import Dict, Optional, Any, List
from datetime import datetime
import uuid
import json

from backend.models import ChatRequest, ChatResponse
from backend.database import DatabaseManager, ChatSession, ChatMessage
from backend.modules.llm.core.llm_core import SimpleEmotionalChatEngine

# 导入增强版组件
from backend.services.enhanced_memory_manager import EnhancedMemoryManager
from backend.services.user_profile_builder import UserProfileBuilder
from backend.services.enhanced_context_assembler import EnhancedContextAssembler
from backend.services.proactive_recall_system import ProactiveRecallSystem

# 尝试导入可选功能
try:
    from backend.modules.rag.services.rag_service import RAGIntegrationService
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    RAGIntegrationService = None

try:
    from backend.modules.intent.services import IntentService
    INTENT_AVAILABLE = True
except ImportError:
    INTENT_AVAILABLE = False
    IntentService = None

try:
    from backend.modules.intent.core.enhanced_input_processor import EnhancedInputProcessor
    ENHANCED_PROCESSOR_AVAILABLE = True
except ImportError:
    ENHANCED_PROCESSOR_AVAILABLE = False
    EnhancedInputProcessor = None


class EnhancedChatService:
    """增强版聊天服务 - 实现文档中所有的高级功能"""
    
    def __init__(
        self,
        use_rag: bool = True,
        use_intent: bool = True,
        use_enhanced_processor: bool = True,
        enable_proactive_recall: bool = True
    ):
        """
        初始化增强版聊天服务
        
        Args:
            use_rag: 是否启用RAG知识库
            use_intent: 是否启用意图识别
            use_enhanced_processor: 是否启用增强输入处理
            enable_proactive_recall: 是否启用主动回忆
        """
        # 核心引擎
        self.chat_engine = SimpleEmotionalChatEngine()
        
        # 增强版组件
        self.memory_manager = EnhancedMemoryManager()
        self.profile_builder = UserProfileBuilder()
        self.context_assembler = EnhancedContextAssembler()
        self.proactive_recall = ProactiveRecallSystem() if enable_proactive_recall else None
        
        # 可选功能初始化
        self._init_optional_features(use_rag, use_intent, use_enhanced_processor)
        
        print("✓ 增强版聊天服务已启动")
        print(f"  - 记忆管理: 短期滑动窗口 + 长期向量检索 + 时间衰减")
        print(f"  - 用户画像: 动态构建")
        print(f"  - 主动回忆: {'启用' if enable_proactive_recall else '禁用'}")
        print(f"  - RAG: {'启用' if self.rag_enabled else '禁用'}")
        print(f"  - 意图识别: {'启用' if self.intent_enabled else '禁用'}")
    
    def _init_optional_features(self, use_rag: bool, use_intent: bool, use_enhanced_processor: bool):
        """初始化可选功能"""
        # 增强版输入处理器
        self.enhanced_processor_enabled = False
        self.enhanced_processor = None
        if use_enhanced_processor and ENHANCED_PROCESSOR_AVAILABLE:
            try:
                self.enhanced_processor = EnhancedInputProcessor(
                    enable_jieba=True,
                    enable_duplicate_check=True
                )
                self.enhanced_processor_enabled = True
                print("  ✓ 增强版输入处理器已启用")
            except Exception as e:
                print(f"  ⚠ 增强版输入处理器初始化失败: {e}")
        
        # RAG服务
        self.rag_enabled = False
        self.rag_service = None
        if use_rag and RAG_AVAILABLE:
            try:
                self.rag_service = RAGIntegrationService()
                if self.rag_service.rag_service.is_knowledge_available():
                    self.rag_enabled = True
                    print("  ✓ RAG知识库已启用")
                else:
                    print("  ⚠ RAG服务已加载，但知识库未初始化")
            except Exception as e:
                print(f"  ⚠ RAG服务初始化失败: {e}")
        
        # 意图识别服务
        self.intent_enabled = False
        self.intent_service = None
        if use_intent and INTENT_AVAILABLE:
            try:
                self.intent_service = IntentService()
                self.intent_enabled = True
                print("  ✓ 意图识别系统已启用")
            except Exception as e:
                print(f"  ⚠ 意图识别服务初始化失败: {e}")
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """
        处理聊天请求（增强版流程）
        
        Args:
            request: 聊天请求
            
        Returns:
            聊天响应
        """
        # 生成会话ID（如果没有）
        if not request.session_id:
            request.session_id = str(uuid.uuid4())
        
        user_id = request.user_id or "anonymous"
        session_id = request.session_id
        message = request.message
        
        # ============ 第1步：输入预处理 ============
        preprocessed, message = await self._preprocess_input(user_id, message)
        if preprocessed and preprocessed.get("blocked"):
            return self._create_blocked_response(session_id, preprocessed)
        
        # ============ 第2步：情绪分析 ============
        emotion_result = self.chat_engine.analyze_emotion(message)
        emotion = emotion_result.get("emotion", "neutral")
        emotion_intensity = emotion_result.get("intensity", 5.0)
        
        # ============ 第3步：意图识别 ============
        intent_result = await self._analyze_intent(user_id, message)
        
        # ============ 第4步：主动回忆检查 ============
        proactive_prompt = None
        if self.proactive_recall:
            proactive_prompt = await self.proactive_recall.generate_proactive_response(
                user_id, message, emotion
            )
        
        # ============ 第5步：获取对话历史 ============
        chat_history = await self._get_conversation_history(session_id, limit=15)
        
        # ============ 第6步：组装增强上下文 ============
        context = await self.context_assembler.assemble_context(
            user_id=user_id,
            session_id=session_id,
            current_message=message,
            chat_history=chat_history,
            emotion=emotion,
            emotion_intensity=emotion_intensity
        )
        
        # ============ 第7步：构建增强Prompt ============
        system_prompt = self._build_system_prompt(context, proactive_prompt)
        enhanced_prompt = self.context_assembler.build_prompt_context(
            context, system_prompt
        )
        
        # ============ 第8步：尝试RAG增强 ============
        rag_result = None
        if self.rag_enabled and self.rag_service:
            rag_result = await self._try_rag_enhancement(
                message, emotion, chat_history
            )
        
        # ============ 第9步：生成回复 ============
        response = await self._generate_response(
            request, rag_result, session_id, emotion, emotion_intensity
        )
        
        # ============ 第10步：添加上下文信息 ============
        self._enrich_response_context(
            response, context, intent_result, preprocessed, rag_result
        )
        
        # ============ 第11步：保存对话到数据库 ============
        await self._save_conversation(
            session_id, user_id, message, response.response, 
            emotion, emotion_intensity
        )
        
        # ============ 第12步：处理并存储记忆 ============
        await self.memory_manager.process_conversation(
            session_id=session_id,
            user_id=user_id,
            user_message=message,
            bot_response=response.response,
            emotion=emotion,
            emotion_intensity=emotion_intensity
        )
        
        return response
    
    async def _preprocess_input(self, user_id: str, message: str) -> tuple:
        """输入预处理"""
        preprocessed = None
        if self.enhanced_processor_enabled and self.enhanced_processor:
            try:
                preprocessed = self.enhanced_processor.preprocess(message, user_id)
                if preprocessed["blocked"]:
                    return preprocessed, message
                message = preprocessed["cleaned"]
            except Exception as e:
                print(f"输入预处理失败: {e}")
        
        return preprocessed, message
    
    async def _analyze_intent(self, user_id: str, message: str) -> Optional[Dict]:
        """意图识别"""
        intent_result = None
        if self.intent_enabled and self.intent_service:
            try:
                intent_analysis = self.intent_service.analyze(message, user_id)
                intent_result = intent_analysis.get('intent', {})
                
                if intent_analysis.get('action_required', False):
                    print(f"⚠️ 检测到用户 {user_id} 的危机情况")
            except Exception as e:
                print(f"意图识别失败: {e}")
        
        return intent_result
    
    async def _get_conversation_history(self, session_id: str, limit: int = 15) -> List[Dict]:
        """获取对话历史"""
        try:
            with DatabaseManager() as db:
                messages = db.get_session_messages(session_id, limit)
                return [
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "emotion": msg.emotion,
                        "emotion_intensity": msg.emotion_intensity,
                        "timestamp": msg.created_at.isoformat() if msg.created_at else None
                    }
                    for msg in messages
                ]
        except Exception as e:
            print(f"获取对话历史失败: {e}")
            return []
    
    def _build_system_prompt(self, context: Dict[str, Any], proactive_prompt: Optional[str]) -> str:
        """构建系统Prompt"""
        system_prompt = """你是"心语"，一位温暖、耐心的心理陪伴者。"""
        
        # 如果有主动回忆提示，添加到系统Prompt
        if proactive_prompt:
            system_prompt += f"\n\n【主动关怀】\n在适当的时候，你可以主动提及：{proactive_prompt}"
        
        return system_prompt
    
    async def _try_rag_enhancement(self, message: str, emotion: str, 
                                  chat_history: List[Dict]) -> Optional[Dict]:
        """尝试RAG增强"""
        try:
            rag_result = self.rag_service.enhance_response(
                message=message,
                emotion=emotion,
                conversation_history=chat_history
            )
            return rag_result
        except Exception as e:
            print(f"RAG增强失败: {e}")
            return None
    
    async def _generate_response(self, request: ChatRequest, rag_result: Optional[Dict],
                                session_id: str, emotion: str, 
                                emotion_intensity: float) -> ChatResponse:
        """生成回复"""
        if rag_result and rag_result.get("use_rag"):
            # 使用RAG增强的回复
            return ChatResponse(
                response=rag_result["answer"],
                emotion=emotion,
                emotion_intensity=emotion_intensity,
                session_id=session_id,
                timestamp=datetime.now()
            )
        else:
            # 使用常规引擎
            try:
                return self.chat_engine.chat(request)
            except Exception as e:
                print(f"常规引擎调用失败: {e}")
                return ChatResponse(
                    response="抱歉，我遇到了一些技术问题，请稍后再试。",
                    session_id=session_id,
                    emotion="neutral",
                    timestamp=datetime.now()
                )
    
    def _enrich_response_context(self, response: ChatResponse, context: Dict[str, Any],
                                 intent_result: Optional[Dict], preprocessed: Optional[Dict],
                                 rag_result: Optional[Dict]):
        """丰富响应上下文信息"""
        response.context = {
            # 记忆信息
            "short_term_messages": context.get("short_term_memory", {}).get("count", 0),
            "long_term_memories": context.get("long_term_memory", {}).get("count", 0),
            "important_turns": len(context.get("short_term_memory", {}).get("important_turns", [])),
            
            # 用户画像
            "user_profile_summary": context.get("user_profile", {}).get("summary", ""),
            
            # 对话图谱
            "conversation_nodes": len(context.get("conversation_graph", {}).get("nodes", {})),
            "conversation_edges": len(context.get("conversation_graph", {}).get("edges", [])),
            
            # 意图识别
            "intent": intent_result.get('intent') if intent_result else None,
            "intent_confidence": intent_result.get('confidence') if intent_result else None,
            
            # 输入处理
            "input_preprocessed": preprocessed is not None,
            "input_metadata": preprocessed.get("metadata") if preprocessed else None,
            
            # RAG使用情况
            "used_rag": bool(rag_result and rag_result.get("use_rag")),
            "knowledge_sources": len(rag_result.get("sources", [])) if rag_result else 0,
            
            # 系统版本
            "system_version": "enhanced_v1.0"
        }
    
    async def _save_conversation(self, session_id: str, user_id: str, 
                                user_message: str, bot_response: str,
                                emotion: str, emotion_intensity: float):
        """保存对话到数据库"""
        try:
            with DatabaseManager() as db:
                # 检查会话是否存在
                existing_session = db.db.query(ChatSession).filter(
                    ChatSession.session_id == session_id
                ).first()
                
                if not existing_session:
                    db.create_session(session_id, user_id)
                
                # 保存用户消息
                db.save_message(
                    session_id=session_id,
                    user_id=user_id,
                    role="user",
                    content=user_message,
                    emotion=emotion,
                    emotion_intensity=emotion_intensity
                )
                
                # 保存助手消息
                db.save_message(
                    session_id=session_id,
                    user_id=user_id,
                    role="assistant",
                    content=bot_response,
                    emotion="empathetic"
                )
                
        except Exception as e:
            print(f"保存对话失败: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_blocked_response(self, session_id: str, preprocessed: Dict) -> ChatResponse:
        """创建被阻止的响应"""
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
    
    # ============ 辅助接口方法 ============
    
    async def get_session_history(self, session_id: str, limit: int = 20) -> Dict[str, Any]:
        """获取会话历史"""
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
    
    async def get_user_sessions(self, user_id: str, limit: int = 50) -> Dict[str, Any]:
        """获取用户的所有会话"""
        try:
            with DatabaseManager() as db:
                sessions = db.get_user_sessions(user_id, limit)
                
                session_list = []
                for session in sessions:
                    first_message = db.db.query(ChatMessage)\
                        .filter(ChatMessage.session_id == session.session_id)\
                        .filter(ChatMessage.role == 'user')\
                        .order_by(ChatMessage.created_at.asc())\
                        .first()
                    
                    title = first_message.content[:30] + "..." if first_message and len(first_message.content) > 30 else (first_message.content if first_message else "新对话")
                    
                    session_list.append({
                        "session_id": session.session_id,
                        "title": title,
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
        """删除会话"""
        try:
            with DatabaseManager() as db:
                return db.delete_session(session_id)
        except Exception as e:
            print(f"删除会话失败: {e}")
            return False
    
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """获取用户画像"""
        return await self.profile_builder.build_profile(user_id)
    
    async def get_user_memories(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取用户重要记忆"""
        return await self.memory_manager.get_important_memories(user_id, limit)
    
    async def get_emotion_insights(self, user_id: str) -> Dict[str, Any]:
        """获取用户情绪洞察"""
        if self.proactive_recall:
            trend_data = await self.proactive_recall.emotion_tracker.track_emotion_changes(
                user_id, days=7
            )
            return trend_data
        return {}

