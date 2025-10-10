from typing import List, Dict, Any, Optional
import openai
import json
import uuid
from datetime import datetime

from config import Config
from .models import ChatSession, Message, ChatRequest, ChatResponse

class SimpleEmotionalChatEngine:
    def __init__(self):
        openai.api_key = Config.OPENAI_API_KEY
        self.sessions: Dict[str, ChatSession] = {}
        
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
    
    def analyze_emotion(self, message: str) -> Dict:
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
        
        return {
            "emotion": dominant_emotion,
            "intensity": intensity,
            "suggestions": self._get_emotion_suggestions(dominant_emotion)
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
    
    def generate_response(self, user_message: str, emotion_data: Dict, conversation_history: List[Dict]) -> str:
        """生成回应"""
        emotion = emotion_data.get("emotion", "neutral")
        intensity = emotion_data.get("intensity", 5)
        
        # 构建对话历史
        history_text = ""
        for msg in conversation_history[-5:]:  # 最近5轮对话
            if msg["role"] == "user":
                history_text += f"用户: {msg['content']}\n"
            else:
                history_text += f"助手: {msg['content']}\n"
        
        # 构建系统提示
        system_prompt = """你是一个专业的情感支持聊天机器人，具有以下特点：

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

请用中文回应，保持温暖、真诚的语调，回应长度控制在50-100字。"""
        
        # 构建用户提示
        user_prompt = f"""用户情感分析: {emotion} (强度: {intensity}/10)

对话历史:
{history_text}

当前用户消息: {user_message}

请生成一个温暖、共情的回应。"""
        
        try:
            response = openai.ChatCompletion.create(
                model=Config.DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=Config.TEMPERATURE,
                max_tokens=Config.MAX_TOKENS
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"生成回应出错: {e}")
            # 备选回应
            suggestions = emotion_data.get("suggestions", [])
            return suggestions[0] if suggestions else "我理解你的感受，我在这里倾听。"
    
    def chat(self, request: ChatRequest) -> ChatResponse:
        """处理聊天请求"""
        # 获取或创建会话
        session = self.get_or_create_session(request.session_id, request.user_id)
        
        # 分析用户消息的情感
        emotion_data = self.analyze_emotion(request.message)
        
        # 添加用户消息到会话
        user_message = Message(
            role="user",
            content=request.message,
            emotion=emotion_data.get("emotion")
        )
        session.messages.append(user_message)
        
        # 获取对话历史
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in session.messages[-10:]  # 最近10条消息
        ]
        
        # 生成回应
        response_text = self.generate_response(
            request.message, 
            emotion_data, 
            conversation_history
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
        
        # 生成建议
        suggestions = emotion_data.get("suggestions", [])
        
        return ChatResponse(
            response=response_text,
            session_id=session.session_id,
            emotion=emotion_data.get("emotion"),
            suggestions=suggestions[:3]  # 返回前3个建议
        )
    
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
