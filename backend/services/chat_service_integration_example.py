#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatService集成个性化配置示例
展示如何将PersonalizationService集成到对话流程中
"""

from typing import Dict, Optional
from backend.services.personalization_service import get_personalization_service
from backend.database import DatabaseManager
import logging

logger = logging.getLogger(__name__)


class PersonalizedChatService:
    """
    集成个性化配置的聊天服务示例
    
    这个示例展示了如何在对话流程中应用个性化配置
    """
    
    def __init__(self):
        """初始化服务"""
        self.personalization_service = get_personalization_service()
    
    async def generate_personalized_response(
        self,
        user_id: str,
        user_message: str,
        emotion_state: Optional[Dict] = None,
        conversation_history: Optional[list] = None
    ) -> Dict:
        """
        生成个性化回复
        
        Args:
            user_id: 用户ID
            user_message: 用户消息
            emotion_state: 情绪状态（可选）
            conversation_history: 对话历史（可选）
        
        Returns:
            包含回复和元数据的字典
        """
        try:
            # 1. 获取用户个性化配置
            with DatabaseManager() as db:
                user_config = self.personalization_service.get_user_config(user_id, db.db)
            
            logger.info(f"用户 {user_id} 的配置: {user_config.get('role')} - {user_config.get('role_name')}")
            
            # 2. 构建对话上下文
            context = self._build_context(user_message, conversation_history)
            
            # 3. 生成个性化Prompt
            with DatabaseManager() as db:
                personalized_prompt = self.personalization_service.generate_personalized_prompt(
                    user_id=user_id,
                    context=context,
                    emotion_state=emotion_state,
                    db=db.db
                )
            
            logger.info(f"生成的个性化Prompt长度: {len(personalized_prompt)} 字符")
            
            # 4. 调用LLM生成回复（这里是示例，实际需要调用真实的LLM）
            # response = await llm.generate(personalized_prompt)
            response = self._mock_llm_response(user_config, emotion_state)
            
            # 5. 返回结果
            return {
                "response": response,
                "user_config": {
                    "role": user_config.get("role"),
                    "role_name": user_config.get("role_name"),
                    "tone": user_config.get("tone"),
                    "style": user_config.get("style")
                },
                "prompt_length": len(personalized_prompt),
                "emotion_state": emotion_state
            }
            
        except Exception as e:
            logger.error(f"生成个性化回复失败: {e}")
            return {
                "response": "抱歉，我现在遇到了一些问题，请稍后再试。",
                "error": str(e)
            }
    
    def _build_context(
        self,
        current_message: str,
        conversation_history: Optional[list] = None
    ) -> str:
        """构建对话上下文"""
        context_parts = []
        
        # 添加历史对话
        if conversation_history:
            history_str = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in conversation_history[-5:]  # 最近5条
            ])
            context_parts.append(f"最近对话:\n{history_str}")
        
        # 添加当前消息
        context_parts.append(f"\n当前用户消息: {current_message}")
        
        return "\n".join(context_parts)
    
    def _mock_llm_response(
        self,
        user_config: Dict,
        emotion_state: Optional[Dict] = None
    ) -> str:
        """
        模拟LLM回复（用于测试）
        实际使用时应调用真实的LLM
        """
        role_name = user_config.get("role_name", "心语")
        role = user_config.get("role", "温暖倾听者")
        tone = user_config.get("tone", "温和")
        
        # 根据角色和情绪生成示例回复
        if emotion_state and emotion_state.get("emotion") == "sad":
            return f"（以{role_name}的身份，{tone}地回应）我能感受到你的难过，让我们一起面对这些感受吧。作为一位{role}，我会一直陪伴着你。"
        elif emotion_state and emotion_state.get("emotion") == "happy":
            return f"（以{role_name}的身份，{tone}地回应）很高兴看到你这么开心！能分享一下是什么让你如此愉悦吗？"
        else:
            return f"（以{role_name}的身份，{tone}地回应）我在这里倾听你的心声。有什么想要分享的吗？"


# ============================================
# 集成到现有ChatService的示例
# ============================================

def integrate_personalization_to_chat_service():
    """
    如何将个性化配置集成到现有ChatService的示例代码
    
    在 backend/services/chat_service.py 的 _chat_with_memory 方法中添加：
    """
    example_code = '''
async def _chat_with_memory(self, request: ChatRequest) -> ChatResponse:
    """使用记忆系统的聊天（集成个性化配置）"""
    user_id = request.user_id or "anonymous"
    session_id = request.session_id
    message = request.message
    
    # ========== 新增：获取个性化配置 ==========
    from backend.services.personalization_service import get_personalization_service
    personalization_service = get_personalization_service()
    
    with DatabaseManager() as db:
        user_config = personalization_service.get_user_config(user_id, db.db)
        logger.info(f"用户个性化角色: {user_config.get('role_name')}")
    # ==========================================
    
    # 1. 分析情绪
    emotion_result = self.chat_engine.analyze_emotion(message)
    emotion = emotion_result.get("emotion", "neutral")
    emotion_intensity = emotion_result.get("intensity", 5.0)
    
    # 2. 构建上下文
    context = await self.context_service.build_context(
        user_id=user_id,
        session_id=session_id,
        current_message=message,
        emotion=emotion,
        emotion_intensity=emotion_intensity
    )
    
    # ========== 新增：生成个性化Prompt ==========
    with DatabaseManager() as db:
        personalized_prompt = personalization_service.generate_personalized_prompt(
            user_id=user_id,
            context=str(context),
            emotion_state={
                "emotion": emotion,
                "intensity": emotion_intensity
            },
            db=db.db
        )
    
    # 使用个性化Prompt替换原有的基础Prompt
    # 在调用LLM时使用 personalized_prompt 而不是默认的系统prompt
    # ==========================================
    
    # 3. 生成回复（使用个性化Prompt）
    response = self.chat_engine.chat_with_custom_prompt(
        message=message,
        system_prompt=personalized_prompt,
        context=context
    )
    
    return response
'''
    return example_code


# ============================================
# 测试代码
# ============================================

async def test_personalized_chat():
    """测试个性化聊天"""
    import asyncio
    
    service = PersonalizedChatService()
    
    # 测试场景1：用户情绪低落
    print("=" * 60)
    print("测试1: 用户情绪低落")
    print("=" * 60)
    
    result = await service.generate_personalized_response(
        user_id="test_user_1",
        user_message="今天工作压力好大，感觉很累...",
        emotion_state={
            "emotion": "sad",
            "intensity": 7.5
        }
    )
    
    print(f"AI角色: {result['user_config']['role_name']}")
    print(f"AI回复: {result['response']}")
    print()
    
    # 测试场景2：用户心情愉快
    print("=" * 60)
    print("测试2: 用户心情愉快")
    print("=" * 60)
    
    result = await service.generate_personalized_response(
        user_id="test_user_2",
        user_message="今天完成了一个大项目，超开心！",
        emotion_state={
            "emotion": "happy",
            "intensity": 8.5
        }
    )
    
    print(f"AI角色: {result['user_config']['role_name']}")
    print(f"AI回复: {result['response']}")
    print()
    
    # 打印集成示例代码
    print("=" * 60)
    print("集成到ChatService的示例代码:")
    print("=" * 60)
    print(integrate_personalization_to_chat_service())


if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    
    print("\n")
    print("=" * 60)
    print("个性化配置集成示例")
    print("=" * 60)
    print("\n")
    
    asyncio.run(test_personalized_chat())





