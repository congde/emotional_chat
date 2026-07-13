#!/usr/bin/env python3
"""
简化版LangChain聊天引擎（支持LCEL表达式，Python 3.10+）
"""
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests

# 导入 LangChain (Python 3.10+, langchain 0.2.x+)
try:
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    ChatPromptTemplate = None
    StrOutputParser = None
    print("提示: LangChain 模块未安装，将使用传统 HTTP 请求方式")

# 数据库和模型
from backend.database import DatabaseManager, create_tables
from backend.models import ChatRequest, ChatResponse
from backend.modules.llm.harness import resolve_llm_settings, try_create_chat_openai

# 导入心语Prompt配置
from backend.xinyu_prompt import (
    get_system_prompt,
    build_full_prompt,
    validate_and_filter_input,
    XINYU_SYSTEM_PROMPT
)

# 尝试导入向量数据库（可选）
try:
    from backend.vector_store import VectorStore
    VECTOR_STORE_AVAILABLE = True
except ImportError as e:
    VECTOR_STORE_AVAILABLE = False
    print("提示: 向量数据库模块未安装 ({}), 将仅使用MySQL短期记忆".format(e))


class SimpleEmotionalChatEngine:
    def __init__(self):
        # 初始化API配置 - 经 LLM Harness 统一解析
        _cfg = resolve_llm_settings()
        self.api_key = _cfg.api_key
        self.api_base_url = _cfg.base_url
        self.model = _cfg.model
        
        if not self.api_key:
            print("警告: API_KEY 未设置，将使用本地fallback模式")
            self.api_key = None
        
        # 创建数据库表
        create_tables()
        
        # 初始化向量数据库（长期记忆）
        if VECTOR_STORE_AVAILABLE:
            try:
                self.vector_store = VectorStore()
                print("✓ 向量数据库 (Chroma) 初始化成功")
            except Exception as e:
                print("警告: 向量数据库初始化失败: {}，将仅使用MySQL".format(e))
                self.vector_store = None
        else:
            self.vector_store = None
            print("⚠ 向量数据库未安装，仅使用MySQL短期记忆")
        
        # 初始化 LangChain 组件（LCEL 表达式）- 如果可用
        if self.api_key and LANGCHAIN_AVAILABLE:
            try:
                # 1. 经 LLM Harness 创建 OpenAI 兼容客户端（与 Hermes 式网关一致）
                self.llm = try_create_chat_openai(temperature=0.7, model=self.model)
                if not self.llm:
                    print("警告: LangChain ChatOpenAI 不可用，将使用传统方式")
                    self.chain = None
                else:
                    # 2. 定义 AI 人格与行为准则（使用完整的心语Prompt）
                    self.template = """{system_prompt}

{{long_term_memory}}

对话历史：
{{history}}

用户：{{input}}
心语：""".format(system_prompt=XINYU_SYSTEM_PROMPT)

                    # 3. 创建提示模板和链（LCEL表达式）
                    self.prompt = ChatPromptTemplate.from_template(self.template)
                    self.output_parser = StrOutputParser()
                    self.chain = self.prompt | self.llm | self.output_parser
                    print("✓ LangChain LCEL 链初始化成功")
            except Exception as e:
                print("警告: LangChain 初始化失败，将使用传统方式: {}".format(e))
                self.llm = None
                self.chain = None
        else:
            self.llm = None
            self.chain = None
        
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
        
    
    def analyze_emotion(self, message):
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
    
    def _get_emotion_suggestions(self, emotion):
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
    
    def is_safe_input(self, text):
        """
        安全检查（使用完整的验证机制）
        Returns: (is_valid, filtered_response)
        """
        return validate_and_filter_input(text)
    
    def get_openai_response(self, user_input, user_id, session_id):
        """使用 LangChain LCEL 链生成回应（如果可用），否则使用传统HTTP请求"""
        # 安全检查
        is_safe, warning = self.is_safe_input(user_input)
        if not is_safe:
            return warning
        
        # 如果没有API key，直接使用fallback
        if not self.api_key:
            emotion_data = self.analyze_emotion(user_input)
            return self._get_fallback_response(user_input, emotion_data)
        
        # 构建历史对话（短期记忆 - MySQL）
        db_manager = DatabaseManager()
        with db_manager as db:
            recent_messages = db.get_session_messages(session_id, limit=10)
            history_text = ""
            for msg in reversed(recent_messages[-5:]):  # 最近5条消息
                history_text += "{}: {}\n".format('用户' if msg.role == 'user' else '心语', msg.content)
        
        # 从向量数据库检索相似对话（长期记忆）
        long_term_context = ""
        if self.vector_store:
            try:
                # 检索相似的历史对话（跨会话）
                similar_conversations = self.vector_store.search_similar_conversations(
                    query=user_input,
                    session_id=None,  # 不限制会话，检索所有历史
                    n_results=3
                )
                
                if similar_conversations and similar_conversations['documents']:
                    long_term_context = "\n相关历史对话参考：\n"
                    for doc in similar_conversations['documents'][0][:2]:  # 取前2个最相似的
                        long_term_context += "- {}\n".format(doc[:100])  # 限制长度
                    long_term_context += "\n"
            except Exception as e:
                print("向量检索失败: {}".format(e))
        
        # 优先使用 LCEL 链（如果可用）
        if self.chain:
            try:
                # 4. 使用链生成回应 (chain.invoke) - 包含长期记忆
                response = self.chain.invoke({
                    "long_term_memory": long_term_context,
                    "history": history_text.strip(),
                    "input": user_input
                })
                return response
            except Exception as e:
                print("LangChain调用失败 ({}): {}，尝试传统方式".format(self.model, e))
                # 继续使用传统方式
        
        # 使用传统 HTTP 请求方式（兼容模式）
        return self._call_api_traditional(user_input, history_text, long_term_context)
    
    def _call_api_traditional(self, user_input, history_text, long_term_context=""):
        """传统HTTP请求方式调用API（兼容旧环境）"""
        # 使用完整的心语Prompt构建提示词
        full_prompt = build_full_prompt(
            user_input=user_input,
            history_text=history_text,
            long_term_memory=long_term_context
        )
        
        # 调用API (支持Qwen和OpenAI)
        try:
            headers = {
                "Authorization": "Bearer {}".format(self.api_key),
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": full_prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 300  # 控制响应长度（3-4句话）
            }
            
            api_url = "{}/chat/completions".format(self.api_base_url)
            response = requests.post(
                api_url,
                headers=headers,
                json=data,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                print("API错误 ({}): {} - {}".format(self.model, response.status_code, response.text))
                return self._get_fallback_response(user_input)
                
        except Exception as e:
            print("API调用失败 ({}): {}".format(self.model, e))
            return self._get_fallback_response(user_input)
    
    def _get_fallback_response(self, user_input, emotion_data=None):
        """提供备选回应当API调用失败时"""
        if emotion_data is None:
            # 如果没有提供情感数据，则分析用户输入
            emotion_data = self.analyze_emotion(user_input)
        emotion = emotion_data.get("emotion", "neutral")
        suggestions = emotion_data.get("suggestions", [])
        
        # 基于情感类型提供合适的回应（符合心语Prompt：3-4句话，不使用表情符号）
        fallback_responses = {
            "happy": [
                "听起来你心情很好。你的快乐让我也感到温暖。有什么特别的事情想要分享吗？",
                "看到你这么开心，我也替你高兴。这种积极的状态真好。愿意多说说是什么让你这么开心吗？",
                "你的愉快心情很有感染力。保持这样的状态很重要。想聊聊让你开心的事情吗？"
            ],
            "sad": [
                "听起来你现在很难过。这种感觉确实不好受。我在这里倾听，你愿意说说发生了什么吗？",
                "我能感受到你的伤心。每个人都会有这样的时刻，这些感受都是正常的。你并不孤单。",
                "你现在的心情一定很沉重。谢谢你愿意告诉我。想多聊聊吗？"
            ],
            "angry": [
                "听起来你很愤怒。这种情绪确实很强烈。是什么事情让你这么生气？",
                "我能感受到你的愤怒。这确实让人很不舒服。你愿意说说具体发生了什么吗？",
                "听起来有些事情真的惹恼了你。这种感觉很正常。想聊聊是什么让你这么生气吗？"
            ],
            "anxious": [
                "听起来你很焦虑。这种不安的感觉确实让人难受。你在担心什么呢？",
                "我能感受到你的紧张。焦虑的时候确实很不好受。可以跟我说说你担心的事情吗？",
                "你现在似乎很不安。这种焦虑感很沉重。想聊聊让你担心的事情吗？"
            ],
            "excited": [
                "听起来你很兴奋。这种期待的感觉真好。有什么好事要发生了吗？",
                "我能感受到你的激动。这种兴奋很有感染力。是什么让你这么期待呢？",
                "你似乎对某件事充满期待。这种感觉真棒。愿意分享一下吗？"
            ],
            "confused": [
                "听起来你感到困惑。这种迷茫的感觉确实让人不安。能说说是什么让你困惑吗？",
                "我能理解你的迷茫。有些事情确实让人摸不着头脑。想聊聊具体是什么让你困惑吗？",
                "你现在似乎有些迷茫。这种感觉很正常。愿意说说让你困惑的事情吗？"
            ],
            "frustrated": [
                "听起来你很挫败。这种感觉确实很沮丧。是什么事情让你这么受挫？",
                "我能感受到你的沮丧。这确实很让人失望。想说说发生了什么吗？",
                "你现在一定很沮丧。这种挫败感真的不好受。愿意聊聊吗？"
            ],
            "lonely": [
                "听起来你感到孤独。这种感觉确实很难受。我在这里陪着你。你想聊聊吗？",
                "我能理解你的孤独感。这种时候确实让人难过。你并不孤单，我在这里倾听。",
                "你现在一定很孤单。这种感觉很沉重。想说说你的想法吗？"
            ],
            "grateful": [
                "听起来你心怀感激。这种感恩的心很美好。是什么让你有这样的感受？",
                "我能感受到你的感恩之心。这很温暖。愿意分享是什么让你心存感激吗？",
                "你的感恩之心很动人。这种积极的情绪很珍贵。想多说说吗？"
            ],
            "neutral": [
                "今天感觉怎么样？我在这里倾听。有什么想聊的吗？",
                "我在这里陪伴你。无论你想说什么，我都愿意倾听。",
                "你现在的心情如何？想聊聊今天的事情吗？"
            ]
        }
        
        # 根据情感选择回应，如果没有对应的情感则使用建议或默认回应
        if emotion in fallback_responses and fallback_responses[emotion]:
            import random
            return random.choice(fallback_responses[emotion])
        elif suggestions:
            return suggestions[0]
        else:
            return "我在这里倾听你的心声。无论你想说什么，我都会认真倾听。你并不孤单。"
    
    def chat(self, request):
        """处理聊天请求"""
        session_id = request.session_id or str(uuid.uuid4())
        user_id = request.user_id or "anonymous"
        
        print(f"Chat请求: session_id={session_id}, user_id={user_id}, message={request.message[:50]}...")
        
        # 分析情感
        emotion_data = self.analyze_emotion(request.message)
        
        # 保存用户消息到数据库
        user_message = None
        try:
            db_manager = DatabaseManager()
            with db_manager as db:
                # 如果是新会话，创建会话记录
                if not request.session_id:
                    print(f"创建新会话: {session_id} for user: {user_id}")
                    db.create_session(session_id, user_id)
                    print(f"会话创建完成")
                
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
        except Exception as e:
            print(f"数据库操作失败: {e}")
            import traceback
            traceback.print_exc()
        
        # 生成回应
        response_text = self.get_openai_response(request.message, user_id, session_id)
        
        # 保存助手消息到数据库
        db_manager = DatabaseManager()
        with db_manager as db:
            assistant_message = db.save_message(
                session_id=session_id,
                user_id=user_id,
                role="assistant",
                content=response_text,
                emotion=emotion_data.get("emotion", "neutral")
            )
        
        # 保存对话到向量数据库（长期记忆）
        if self.vector_store:
            try:
                self.vector_store.add_conversation(
                    session_id=session_id,
                    message=request.message,
                    response=response_text,
                    emotion=emotion_data["emotion"]
                )
            except Exception as e:
                print("保存到向量数据库失败: {}".format(e))
        
        return ChatResponse(
            response=response_text,
            session_id=session_id,
            emotion=emotion_data["emotion"],
            suggestions=emotion_data["suggestions"][:3]
        )
    
    def get_session_summary(self, session_id):
        """获取会话摘要"""
        db_manager = DatabaseManager()
        with db_manager as db:
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
    
    def get_user_emotion_trends(self, user_id):
        """获取用户情感趋势"""
        db_manager = DatabaseManager()
        with db_manager as db:
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
