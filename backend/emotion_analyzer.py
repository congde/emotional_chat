from typing import Dict, List, Tuple
import re

# 导入 LangChain (Python 3.10+, langchain 0.2.x+)
try:
    from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
    from langchain_core.prompts import PromptTemplate
    from langchain_openai import ChatOpenAI
except ImportError:
    BaseMessage = None
    HumanMessage = None
    AIMessage = None
    PromptTemplate = None
    ChatOpenAI = None

from config import Config

class EmotionAnalyzer:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=Config.OPENAI_API_KEY,
            base_url=Config.API_BASE_URL,
            model_name=Config.DEFAULT_MODEL,
            temperature=0.3
        )
        
        # 情感分析提示模板
        self.emotion_prompt = PromptTemplate(
            input_variables=["message"],
            template="""
            请分析以下用户消息的情感状态，返回JSON格式：
            {{
                "emotion": "情感类型（happy/sad/angry/anxious/excited/neutral/confused/frustrated/lonely/grateful等）",
                "intensity": 情感强度（0-10的数字）,
                "keywords": ["关键词1", "关键词2"],
                "suggestions": ["建议1", "建议2", "建议3"]
            }}
            
            用户消息: {message}
            
            请只返回JSON格式的结果，不要其他内容。
            """
        )
        
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
    
    def analyze_emotion(self, message: str) -> Dict:
        """分析用户消息的情感"""
        try:
            # 使用LLM进行情感分析
            prompt = self.emotion_prompt.format(message=message)
            response = self.llm.predict(prompt)
            
            # 尝试解析JSON响应
            import json
            try:
                emotion_data = json.loads(response)
                return emotion_data
            except json.JSONDecodeError:
                # 如果JSON解析失败，使用关键词匹配作为备选
                return self._keyword_based_analysis(message)
                
        except Exception as e:
            print(f"情感分析出错: {e}")
            return self._keyword_based_analysis(message)
    
    def _keyword_based_analysis(self, message: str) -> Dict:
        """基于关键词的情感分析备选方案"""
        message_lower = message.lower()
        
        emotion_scores = {}
        for emotion, keywords in self.emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > 0:
                emotion_scores[emotion] = score
        
        if emotion_scores:
            # 找到得分最高的情感
            dominant_emotion = max(emotion_scores, key=emotion_scores.get)
            intensity = min(emotion_scores[dominant_emotion] * 2, 10)
        else:
            dominant_emotion = "neutral"
            intensity = 5
        
        return {
            "emotion": dominant_emotion,
            "intensity": intensity,
            "keywords": self.emotion_keywords.get(dominant_emotion, []),
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
    
    def generate_empathetic_response(self, user_message: str, emotion_data: Dict, conversation_history: List = None) -> str:
        """生成共情回应"""
        emotion = emotion_data.get("emotion", "neutral")
        intensity = emotion_data.get("intensity", 5)
        
        # 根据情感强度调整回应策略
        if intensity >= 7:
            # 高强度情感，需要更多关注
            empathy_level = "high"
        elif intensity >= 4:
            # 中等强度情感
            empathy_level = "medium"
        else:
            # 低强度情感
            empathy_level = "low"
        
        # 构建共情回应提示
        empathy_prompt = f"""
        用户说: "{user_message}"
        情感分析: {emotion} (强度: {intensity}/10)
        
        请生成一个温暖、共情的回应，要求：
        1. 承认并理解用户的情感
        2. 根据情感类型提供适当的支持
        3. 保持温暖、专业的语调
        4. 回应长度控制在50-100字
        5. 避免给出直接的解决方案，更多是情感支持
        
        回应：
        """
        
        try:
            response = self.llm.predict(empathy_prompt)
            return response.strip()
        except Exception as e:
            print(f"生成共情回应出错: {e}")
            # 备选回应
            suggestions = emotion_data.get("suggestions", [])
            return suggestions[0] if suggestions else "我理解你的感受，我在这里倾听。"
