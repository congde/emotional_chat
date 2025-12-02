"""
带插件支持的聊天引擎 - 扩展 SimpleEmotionalChatEngine 以支持 Function Calling
"""
import os
import json
import uuid
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests

# 导入 LangChain (Python 3.10+, langchain 0.2.x+)
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    ChatOpenAI = None
    ChatPromptTemplate = None
    StrOutputParser = None

from backend.database import DatabaseManager, create_tables, get_db
from backend.models import ChatRequest, ChatResponse
from backend.xinyu_prompt import get_system_prompt, build_full_prompt, validate_and_filter_input, XINYU_SYSTEM_PROMPT
from backend.plugins.plugin_manager import PluginManager
from backend.plugins.weather_plugin import WeatherPlugin
from backend.plugins.news_plugin import NewsPlugin
from backend.plugins.holiday_plugin import HolidayPlugin
from backend.services.personalization_service import get_personalization_service

try:
    from backend.vector_store import VectorStore
    VECTOR_STORE_AVAILABLE = True
except ImportError:
    VECTOR_STORE_AVAILABLE = False


class EmotionalChatEngineWithPlugins:
    """
    带插件支持的情感聊天引擎
    支持 Function Calling 机制，允许模型调用外部工具
    """
    
    def __init__(self):
        # 初始化API配置
        self.api_key = os.getenv("LLM_API_KEY") or os.getenv("DASHSCOPE_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.api_base_url = os.getenv("LLM_BASE_URL") or os.getenv("API_BASE_URL", "https://api.openai.com/v1")
        self.model = os.getenv("DEFAULT_MODEL", "qwen-plus")
        
        if not self.api_key:
            print("警告: API_KEY 未设置，将使用本地fallback模式")
            self.api_key = None
        
        # 创建数据库表
        create_tables()
        
        # 初始化向量数据库
        if VECTOR_STORE_AVAILABLE:
            try:
                self.vector_store = VectorStore()
                print("✓ 向量数据库初始化成功")
            except Exception as e:
                print(f"警告: 向量数据库初始化失败: {e}")
                self.vector_store = None
        else:
            self.vector_store = None
        
        # 初始化插件管理器
        self.plugin_manager = PluginManager()
        
        # 注册插件
        try:
            weather_plugin = WeatherPlugin()
            news_plugin = NewsPlugin()
            holiday_plugin = HolidayPlugin()
            self.plugin_manager.register_many([weather_plugin, news_plugin, holiday_plugin])
            print("✓ 插件系统初始化成功（天气、新闻、节假日）")
        except Exception as e:
            print(f"警告: 插件初始化失败: {e}")
        
        # 初始化个性化服务
        try:
            self.personalization_service = get_personalization_service()
            print("✓ 个性化配置服务初始化成功")
        except Exception as e:
            print(f"警告: 个性化服务初始化失败: {e}")
            self.personalization_service = None
        
        # 初始化 LLM
        if self.api_key and LANGCHAIN_AVAILABLE:
            try:
                self.llm = ChatOpenAI(
                    model=self.model,
                    temperature=0.7,
                    api_key=self.api_key,
                    base_url=self.api_base_url
                )
                
                self.template = """{system_prompt}

{{long_term_memory}}

对话历史：
{{history}}

用户：{{input}}
心语：""".format(system_prompt=XINYU_SYSTEM_PROMPT)
                
                self.prompt = ChatPromptTemplate.from_template(self.template)
                self.output_parser = StrOutputParser()
                self.chain = self.prompt | self.llm | self.output_parser
                print("✓ LangChain LCEL 链初始化成功")
            except Exception as e:
                print(f"警告: LangChain 初始化失败: {e}")
                self.llm = None
                self.chain = None
        else:
            self.llm = None
            self.chain = None
    
    def chat(self, request: ChatRequest) -> ChatResponse:
        """
        处理聊天请求（支持插件调用）
        """
        print(f"\n[CHAT] 收到聊天请求: {request.message[:50]}...")
        session_id = request.session_id or str(uuid.uuid4())
        user_id = request.user_id or "anonymous"
        
        # 分析情感
        emotion_data = self._analyze_emotion_simple(request.message)
        
        # 保存用户消息
        try:
            db_manager = DatabaseManager()
            with db_manager as db:
                if not request.session_id:
                    db.create_session(session_id, user_id)
                
                user_message = db.save_message(
                    session_id=session_id,
                    user_id=user_id,
                    role="user",
                    content=request.message,
                    emotion=emotion_data["emotion"],
                    emotion_intensity=emotion_data["intensity"]
                )
                
                db.save_emotion_analysis(
                    session_id=session_id,
                    user_id=user_id,
                    message_id=user_message.id,
                    emotion=emotion_data["emotion"],
                    intensity=emotion_data["intensity"],
                    keywords=emotion_data.get("keywords", []),
                    suggestions=emotion_data.get("suggestions", [])
                )
        except Exception as e:
            print(f"数据库操作失败: {e}")
            import traceback
            traceback.print_exc()
        
        # 生成回应（支持插件调用）
        plugin_used = None
        plugin_result = None
        
        response_text = self._generate_response_with_plugins(
            request.message, 
            session_id,
            user_id=user_id,
            emotion_state={
                "emotion": emotion_data["emotion"],
                "intensity": emotion_data["intensity"]
            },
            plugin_used_ref=[plugin_used],
            plugin_result_ref=[plugin_result],
            deep_thinking=request.deep_thinking or False
        )
        
        # 保存助手消息
        try:
            db_manager = DatabaseManager()
            with db_manager as db:
                assistant_message = db.save_message(
                    session_id=session_id,
                    user_id=user_id,
                    role="assistant",
                    content=response_text,
                    emotion=emotion_data.get("emotion", "neutral")
                )
        except Exception as e:
            print(f"保存消息失败: {e}")
            import traceback
            traceback.print_exc()
        
        # 保存到向量数据库
        if self.vector_store:
            try:
                self.vector_store.add_conversation(
                    session_id=session_id,
                    message=request.message,
                    response=response_text,
                    emotion=emotion_data["emotion"]
                )
            except Exception as e:
                print(f"保存到向量数据库失败: {e}")
        
        return ChatResponse(
            response=response_text,
            session_id=session_id,
            emotion=emotion_data["emotion"],
            suggestions=emotion_data.get("suggestions", [])[:3],
            plugin_used=plugin_used,
            plugin_result=plugin_result
        )
    
    def _detect_weather_intent(self, user_input: str) -> Optional[str]:
        """检测用户是否在询问天气，如果是则返回城市名称"""
        weather_keywords = ["天气", "温度", "下雨", "晴天", "阴天", "weather", "温度", "气温", "降雨", "下雪"]
        location_keywords = ["北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "西安", "南京", "重庆"]
        
        # 检查是否包含天气相关关键词
        has_weather_keyword = any(keyword in user_input for keyword in weather_keywords)
        if not has_weather_keyword:
            return None
        
        # 尝试提取城市名称
        for city in location_keywords:
            if city in user_input:
                return city
        
        # 如果没有明确城市，尝试从输入中提取
        # 简单提取：查找"XX的天气"或"XX天气"模式
        patterns = [
            r"([\u4e00-\u9fa5]+)的?天气",
            r"([\u4e00-\u9fa5]+)天气",
            r"天气.*?([\u4e00-\u9fa5]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, user_input)
            if match:
                city = match.group(1)
                if len(city) <= 4:  # 城市名通常不超过4个字
                    return city
        
        # 如果没有找到具体城市，返回默认值（让API决定）
        return "当前城市" if "当前" in user_input or "这里" in user_input else None
    
    def _detect_holiday_intent(self, user_input: str) -> Optional[Dict[str, str]]:
        """检测用户是否在询问节假日信息，如果是则返回日期信息"""
        # 出游、旅行相关关键词
        travel_keywords = [
            "出游", "旅行", "旅游", "出行", "出去玩", "去玩", "假期", "放假", 
            "节假日", "节日", "周末", "工作日", "调休", "假期安排",
            "travel", "trip", "vacation", "holiday", "weekend", "workday"
        ]
        
        # 检查是否包含出游/节假日相关关键词
        has_travel_keyword = any(keyword in user_input for keyword in travel_keywords)
        if not has_travel_keyword:
            return None
        
        # 尝试提取日期
        date_patterns = [
            r"(\d{4})[年\-/](\d{1,2})[月\-/](\d{1,2})[日]?",  # 2024-10-01, 2024/10/1, 2024年10月1日
            r"(\d{4})(\d{2})(\d{2})",  # 20241001
            r"(\d{1,2})[月\-/](\d{1,2})[日]?",  # 10月1日, 10/1
            r"今天", r"明天", r"后天", r"大后天",
            r"下周一", r"下周二", r"下周三", r"下周四", r"下周五", r"下周六", r"下周日",
            r"这周", r"下周", r"这周末", r"下周末"
        ]
        
        result = {"date": None, "year": None}
        
        # 提取具体日期
        for pattern in date_patterns:
            match = re.search(pattern, user_input)
            if match:
                if "今天" in user_input:
                    from datetime import datetime
                    result["date"] = datetime.now().strftime("%Y-%m-%d")
                    return result
                elif "明天" in user_input:
                    from datetime import datetime, timedelta
                    result["date"] = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                    return result
                elif "后天" in user_input:
                    from datetime import datetime, timedelta
                    result["date"] = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
                    return result
                elif len(match.groups()) == 3:
                    # 完整日期 YYYY-MM-DD
                    year, month, day = match.groups()
                    result["date"] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    return result
                elif len(match.groups()) == 2 and len(match.group(1)) == 4:
                    # YYYYMMDD格式
                    date_str = match.group(0)
                    if len(date_str) == 8:
                        result["date"] = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                        return result
                elif len(match.groups()) == 2:
                    # 月-日格式，需要补充年份
                    month, day = match.groups()
                    from datetime import datetime
                    year = datetime.now().year
                    result["date"] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    return result
        
        # 提取年份（用于查询整年节假日）
        year_match = re.search(r"(\d{4})年", user_input)
        if year_match:
            result["year"] = year_match.group(1)
            return result
        
        # 如果只是提到出游但没有具体日期，返回今天（让用户知道今天是否适合出游）
        return {"date": None, "year": None}
    
    def _generate_response_with_plugins(self, user_input: str, session_id: str, 
                                       user_id: str = "anonymous",
                                       emotion_state: Optional[Dict] = None,
                                       plugin_used_ref: List = None, 
                                       plugin_result_ref: List = None,
                                       deep_thinking: bool = False):
        """
        使用 Function Calling 生成回应
        如果模型决定调用插件，则执行插件并基于结果生成最终回复
        """
        print(f"\n{'='*60}")
        print(f"[DEBUG] _generate_response_with_plugins 被调用")
        print(f"[DEBUG] 用户输入: {user_input}")
        print(f"[DEBUG] session_id: {session_id}")
        print(f"{'='*60}\n")
        
        if not self.api_key:
            print("[WARNING] API_KEY 未设置，使用fallback响应")
            return self._get_fallback_response(user_input)
        
        # 获取个性化系统Prompt
        system_prompt = self._get_personalized_system_prompt(user_id, user_input, emotion_state)
        
        # 深度思考模式：在系统提示中添加深度思考指导
        if deep_thinking:
            deep_thinking_instruction = """
            
【深度思考模式已启用】
请对用户的输入进行更深入的思考和分析：
1. 仔细分析用户问题的核心和潜在意图
2. 考虑多个角度和可能性
3. 提供更全面、更有深度的回答
4. 如果涉及情感问题，请进行更深入的情感理解和共情
5. 考虑回答的长远影响和不同场景下的适用性

请给出经过深入思考的回应。"""
            system_prompt += deep_thinking_instruction
            print("[DEBUG] 深度思考模式已启用")
        
        # 根据深度思考模式调整temperature和max_tokens
        temperature = 0.5 if deep_thinking else 0.7  # 深度思考时降低temperature，使回答更稳定
        max_tokens = 2000 if deep_thinking else 1000  # 深度思考时允许更长的回答
        
        # 获取函数列表
        functions = self.plugin_manager.get_function_schemas()
        
        if not functions:
            # 没有插件，使用普通模式
            return self._call_llm_normal(user_input, session_id, user_id, emotion_state, deep_thinking)
        
        # 检测用户意图（仅用于辅助参数提取，不强制调用）
        weather_location = self._detect_weather_intent(user_input)
        holiday_info = self._detect_holiday_intent(user_input)
        
        print(f"[DEBUG] 意图检测 - 天气: location={weather_location}, 节假日: info={holiday_info}")
        
        # 构建消息 - 让大模型自己判断是否需要调用工具
        tools_description = "\n\n【工具使用说明】当用户需要实时信息时，你可以调用以下工具获取数据：\n"
        for func in functions:
            tools_description += f"- {func.get('name', 'unknown')}: {func.get('description', '')}\n"
        
        tools_description += "\n【使用原则】\n"
        tools_description += "1. 当用户询问天气相关信息时，调用get_weather工具获取实时天气数据。\n"
        tools_description += "2. 当用户询问新闻时，调用get_latest_news工具获取最新新闻。\n"
        tools_description += "3. 当用户提到出游、旅行、假期安排、节假日、工作日、调休等时，调用get_holiday_info工具查询节假日信息。\n"
        tools_description += "4. 根据用户的具体需求，选择合适的工具和参数。\n"
        tools_description += "5. 如果用户的问题不需要实时数据，直接回答即可，无需调用工具。"
        
        messages = [
            {
                "role": "system",
                "content": system_prompt + tools_description
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
        
        # 第一次调用：让模型决定是否需要调用工具
        try:
            # 检查是否支持 Function Calling
            api_url = f"{self.api_base_url}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 转换functions为tools格式（通义千问DashScope API使用tools格式）
            tools = [{"type": "function", "function": func} for func in functions]
            
            # 让模型自己决定是否调用工具（不强制）
            tool_choice = "auto"
            print(f"[DEBUG] 工具选择模式: auto（由模型决定是否调用工具）")
            
            # 优先尝试tools格式（通义千问）
            data = {
                "model": self.model,
                "messages": messages,
                "tools": tools,
                "tool_choice": tool_choice,  # 强制调用或让模型决定
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            print(f"[DEBUG] 发送API请求，tool_choice: {tool_choice}")
            
            response = requests.post(api_url, headers=headers, json=data, timeout=30)
            
            # 如果tools格式失败，尝试functions格式（OpenAI兼容）
            if response.status_code != 200:
                print(f"[WARNING] 尝试tools格式失败 ({response.status_code}): {response.text[:200]}")
                print(f"[DEBUG] 改用functions格式...")
                
                # 对于functions格式，也让模型自己决定
                function_call = "auto"
                print(f"[DEBUG] 函数调用模式: auto（由模型决定是否调用函数）")
                
                data = {
                    "model": self.model,
                    "messages": messages,
                    "functions": functions,
                    "function_call": function_call,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
                response = requests.post(api_url, headers=headers, json=data, timeout=30)
            
            if response.status_code != 200:
                print(f"API错误: {response.status_code} - {response.text[:500]}")
                return self._get_fallback_response(user_input)
            
            result = response.json()
            assistant_message = result["choices"][0]["message"]
            
            print(f"[DEBUG] API响应: {json.dumps(assistant_message, ensure_ascii=False, indent=2)[:500]}")
            
            # 检查是否有工具调用（支持两种格式）
            function_call = None
            func_name = None
            func_args = None
            
            # 检查tools格式（通义千问DashScope）
            if "tool_calls" in assistant_message and assistant_message.get("tool_calls"):
                tool_call = assistant_message["tool_calls"][0]
                function_call = tool_call.get("function", {})
                func_name = function_call.get("name")
                func_args_str = function_call.get("arguments", "{}")
                try:
                    func_args = json.loads(func_args_str) if isinstance(func_args_str, str) else func_args_str
                except:
                    func_args = {}
                print(f"[DEBUG] 检测到tools格式调用: {func_name}, 参数: {func_args}")
            
            # 检查functions格式（OpenAI兼容）
            elif "function_call" in assistant_message:
                # 模型决定调用函数
                function_call = assistant_message["function_call"]
                func_name = function_call.get("name")
                func_args_str = function_call.get("arguments", "{}")
                try:
                    func_args = json.loads(func_args_str) if isinstance(func_args_str, str) else func_args_str
                except:
                    func_args = {}
                print(f"[DEBUG] 检测到functions格式调用: {func_name}, 参数: {func_args}")
            
            if func_name:
                # 辅助参数提取：如果模型调用了工具但参数不完整，尝试从用户输入中提取
                if func_name == "get_weather" and "location" not in func_args:
                    if weather_location and weather_location != "当前城市":
                        func_args["location"] = weather_location
                        print(f"[DEBUG] 辅助提取location参数: {weather_location}")
                    elif weather_location == "当前城市" or not weather_location:
                        # 如果无法提取，使用默认值或让API决定
                        func_args["location"] = "深圳"  # 默认值，可以根据需要修改
                        print(f"[DEBUG] 使用默认location: 深圳")
                
                # 辅助参数提取：节假日查询
                if func_name == "get_holiday_info":
                    if holiday_info:
                        if holiday_info.get("date") and "date" not in func_args:
                            func_args["date"] = holiday_info["date"]
                            print(f"[DEBUG] 辅助提取date参数: {holiday_info['date']}")
                        elif holiday_info.get("year") and "year" not in func_args:
                            func_args["year"] = holiday_info["year"]
                            print(f"[DEBUG] 辅助提取year参数: {holiday_info['year']}")
                    # 如果模型没有提供参数，也不强制添加，让插件自己处理（插件有默认值）
                
                # 执行插件
                print(f"[DEBUG] 执行插件: {func_name}, 参数: {func_args}")
                plugin_result = self.plugin_manager.execute_plugin(func_name, **func_args)
                print(f"[DEBUG] 插件执行结果: {json.dumps(plugin_result, ensure_ascii=False)[:200]}")
                
                # 更新引用（如果需要）
                if plugin_used_ref is not None:
                    plugin_used_ref[0] = func_name
                if plugin_result_ref is not None:
                    plugin_result_ref[0] = plugin_result
                
                # 构建包含插件结果的系统消息
                plugin_result_text = self._format_plugin_result(func_name, plugin_result)
                print(f"[DEBUG] 格式化后的插件结果文本: {plugin_result_text}")
                
                # 第二次调用：让模型基于插件结果生成最终回复
                messages.append(assistant_message)
                
                # 根据格式添加工具响应
                if "tool_calls" in assistant_message:
                    # tools格式（通义千问）
                    messages.append({
                        "role": "tool",
                        "tool_call_id": assistant_message["tool_calls"][0].get("id"),
                        "name": func_name,
                        "content": json.dumps(plugin_result, ensure_ascii=False)
                    })
                else:
                    # functions格式（OpenAI兼容）
                    messages.append({
                        "role": "function",
                        "name": func_name,
                        "content": json.dumps(plugin_result, ensure_ascii=False)
                    })
                # 使用个性化Prompt生成最终回复
                personalized_prompt = self._get_personalized_system_prompt(user_id, user_input, emotion_state)
                
                # 根据插件类型构建不同的用户消息
                if func_name == "get_weather":
                    user_message_content = f"""用户询问了天气信息，我已经查询到了以下数据：

{plugin_result_text}

请基于这些真实的天气数据，用自然、温暖、陪伴式的语言回复用户。要求：
1. 必须包含具体的天气信息（温度、天气状况等）
2. 用温暖、关心的语气
3. 可以结合天气给出贴心的建议
4. 保持"心语"的陪伴者角色，不要只是冷冰冰地报数据"""
                elif func_name == "get_latest_news":
                    user_message_content = f"""用户询问了新闻信息，我已经查询到了以下新闻数据：

{plugin_result_text}

请基于这些真实的新闻数据，用自然、温暖、陪伴式的语言回复用户。要求：
1. 必须列出具体的新闻标题和摘要（不要只是泛泛而谈）
2. 每条新闻都要有明确的标题和简要描述
3. 用温暖、关心的语气介绍这些新闻
4. 可以询问用户对哪条新闻感兴趣，想了解更多
5. 保持"心语"的陪伴者角色，让用户感受到你在分享有用的信息"""
                elif func_name == "get_holiday_info":
                    user_message_content = f"""用户询问了节假日信息，我已经查询到了以下数据：

{plugin_result_text}

请基于这些真实的节假日数据，用自然、温暖、陪伴式的语言回复用户。要求：
1. 明确告诉用户该日期是否为节假日、工作日或周末
2. 如果是节假日，说明是什么节日
3. 结合用户提到的出游、旅行等需求，给出贴心的建议
4. 用温暖、关心的语气，帮助用户规划行程
5. 保持"心语"的陪伴者角色，让用户感受到你在关心他们的出行安排"""
                else:
                    user_message_content = f"""用户询问了相关信息，我已经查询到了以下数据：

{plugin_result_text}

请基于这些真实数据，用自然、温暖、陪伴式的语言回复用户。"""
                
                messages.append({
                    "role": "user",
                    "content": user_message_content
                })
                # 更新系统消息为个性化Prompt
                messages[0]["content"] = personalized_prompt
                
                print(f"[DEBUG] 发送最终回复请求，消息数量: {len(messages)}")
                print(f"[DEBUG] 最后一条用户消息: {user_message_content[:200]}...")
                
                # 生成最终回复
                final_response = requests.post(
                    api_url,
                    headers=headers,
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    },
                    timeout=30
                )
                
                if final_response.status_code == 200:
                    final_result = final_response.json()
                    final_content = final_result["choices"][0]["message"]["content"].strip()
                    print(f"[DEBUG] 最终回复内容: {final_content[:200]}...")
                    return final_content
                else:
                    # 如果失败，手动生成回复
                    print(f"[WARNING] 最终回复生成失败: {final_response.status_code} - {final_response.text[:200]}")
                    fallback_response = self._generate_response_from_plugin_result(func_name, plugin_result, user_input)
                    print(f"[DEBUG] 使用fallback回复: {fallback_response[:200]}...")
                    return fallback_response
            else:
                # 模型没有调用函数
                content = assistant_message.get("content", "").strip()
                print(f"[DEBUG] 模型未调用工具，直接返回回复: {content[:100]}...")
                
                # 如果用户明显在询问天气但模型没有调用工具，给出提示
                weather_keywords = ["天气", "温度", "下雨", "晴天", "阴天", "weather"]
                if any(keyword in user_input for keyword in weather_keywords):
                    print(f"[WARNING] 用户询问天气但模型未调用工具，可能需要改进提示")
                
                return content
        
        except Exception as e:
            import traceback
            print(f"[ERROR] 调用LLM失败: {e}")
            traceback.print_exc()
            return self._get_fallback_response(user_input)
    
    def _format_plugin_result(self, plugin_name: str, result: Dict[str, Any]) -> str:
        """格式化插件结果"""
        if plugin_name == "get_weather":
            if "error" in result:
                return f"天气查询失败: {result['error']}"
            
            # 构建详细的天气信息
            location = result.get('location', '未知地点')
            temperature = result.get('temperature', 0)
            description = result.get('description', '未知')
            humidity = result.get('humidity', 0)
            wind_speed = result.get('wind_speed', 0)
            feels_like = result.get('feels_like', temperature)
            pressure = result.get('pressure', 0)
            
            weather_info = f"""地点：{location}
温度：{temperature}℃
体感温度：{feels_like}℃
天气状况：{description}
湿度：{humidity}%
风速：{wind_speed}m/s
气压：{pressure}hPa"""
            
            return weather_info
        
        elif plugin_name == "get_latest_news":
            if "error" in result:
                return f"新闻查询失败: {result['error']}"
            articles = result.get('articles', [])
            if not articles:
                return "未能获取到新闻数据"
            
            category = result.get('category', '综合')
            category_cn = {
                "general": "综合",
                "technology": "科技",
                "health": "健康",
                "entertainment": "娱乐",
                "science": "科学"
            }.get(category, category)
            
            source = result.get('source', '新闻源')
            news_text = f"【{category_cn}新闻】共找到{len(articles)}条新闻（来源：{source}）：\n\n"
            for i, article in enumerate(articles, 1):
                title = article.get('title', '无标题')
                description = article.get('description', '')
                source_name = article.get('source', '')
                
                news_text += f"{i}. {title}\n"
                if description:
                    # 限制描述长度
                    desc = description[:150] + "..." if len(description) > 150 else description
                    news_text += f"   {desc}\n"
                if source_name:
                    news_text += f"   来源：{source_name}\n"
                news_text += "\n"
            
            return news_text
        
        elif plugin_name == "get_holiday_info":
            if "error" in result:
                return f"节假日查询失败: {result['error']}"
            
            date_str = result.get('date', '未知日期')
            is_holiday = result.get('is_holiday', False)
            holiday_name = result.get('holiday_name', '')
            is_workday = result.get('is_workday', False)
            is_weekend = result.get('is_weekend', False)
            weekday = result.get('weekday', '')
            
            holiday_info = f"""日期：{date_str}
是否为节假日：{'是' if is_holiday else '否'}
节假日名称：{holiday_name if holiday_name else '无'}
是否为工作日：{'是' if is_workday else '否'}
是否为周末：{'是' if is_weekend else '否'}
星期：{weekday}"""
            
            return holiday_info
        
        return json.dumps(result, ensure_ascii=False)
    
    def _generate_response_from_plugin_result(self, plugin_name: str, result: Dict[str, Any], user_input: str) -> str:
        """基于插件结果手动生成回复"""
        if "error" in result:
            error_msg = result['error']
            # 如果是API密钥未配置，给出更友好的提示
            if "API密钥" in error_msg or "未配置" in error_msg:
                return "我暂时无法获取实时天气信息，因为天气服务还没有配置好。不过无论天气如何，都希望你能找到让自己舒服的状态。你今天有什么特别的安排吗？"
            else:
                return f"很抱歉，{error_msg}。不过我还是想陪伴你，有什么想聊的吗？"
        
        if plugin_name == "get_weather":
            location = result.get('location', '该地')
            description = result.get('description', '晴朗')
            temperature = result.get('temperature', 20)
            humidity = result.get('humidity', 0)
            feels_like = result.get('feels_like', temperature)
            
            # 生成更自然的回复
            reply = f"我帮你查了{location}的天气，{description}，温度{temperature}℃"
            if feels_like != temperature:
                reply += f"，体感温度{feels_like}℃"
            if humidity:
                reply += f"，湿度{humidity}%"
            reply += "。"
            
            # 根据天气给出建议
            if "晴" in description or "sunny" in description.lower():
                reply += "很舒适的天气呢，适合出门走走~"
            elif "雨" in description or "rain" in description.lower():
                reply += "记得带伞哦，照顾好自己。"
            elif "阴" in description or "cloudy" in description.lower():
                reply += "天气有点阴沉，但心情可以保持晴朗呢。"
            else:
                reply += "无论天气如何，都希望你能找到让自己舒服的状态。"
            
            return reply
        
        elif plugin_name == "get_latest_news":
            articles = result.get('articles', [])
            if not articles:
                return "很抱歉，暂时没有找到相关新闻。不过我可以陪你聊聊其他话题，有什么想说的吗？"
            
            category = result.get('category', '综合')
            category_cn = {
                "general": "综合",
                "technology": "科技",
                "health": "健康",
                "entertainment": "娱乐",
                "science": "科学"
            }.get(category, category)
            
            news_list = []
            for i, article in enumerate(articles[:3], 1):
                title = article.get('title', '无标题')
                description = article.get('description', '')
                if description:
                    desc = description[:80] + "..." if len(description) > 80 else description
                    news_list.append(f"{i}. {title} - {desc}")
                else:
                    news_list.append(f"{i}. {title}")
            
            news_text = "\n".join(news_list)
            return f"我为你找到了{len(articles)}条{category_cn}新闻：\n\n{news_text}\n\n你对哪条新闻感兴趣，想了解更多吗？"
        
        return "我已经为你查询了相关信息，有什么想聊的吗？"
    
    def _call_llm_normal(self, user_input: str, session_id: str, 
                        user_id: str = "anonymous", 
                        emotion_state: Optional[Dict] = None,
                        deep_thinking: bool = False) -> str:
        """不使用插件的普通聊天"""
        # 获取历史
        db_manager = DatabaseManager()
        with db_manager as db:
            recent_messages = db.get_session_messages(session_id, limit=10)
            history_text = ""
            for msg in reversed(recent_messages[-5:]):
                history_text += "{}: {}\n".format('用户' if msg.role == 'user' else '心语', msg.content)
        
        # 获取个性化系统Prompt
        system_prompt = self._get_personalized_system_prompt(user_id, user_input, emotion_state)
        
        # 深度思考模式：在系统提示中添加深度思考指导
        if deep_thinking:
            deep_thinking_instruction = """
            
【深度思考模式已启用】
请对用户的输入进行更深入的思考和分析：
1. 仔细分析用户问题的核心和潜在意图
2. 考虑多个角度和可能性
3. 提供更全面、更有深度的回答
4. 如果涉及情感问题，请进行更深入的情感理解和共情
5. 考虑回答的长远影响和不同场景下的适用性

请给出经过深入思考的回应。"""
            system_prompt += deep_thinking_instruction
        
        # 根据深度思考模式调整temperature和max_tokens
        temperature = 0.5 if deep_thinking else 0.7  # 深度思考时降低temperature，使回答更稳定
        max_tokens = 2000 if deep_thinking else 1000  # 深度思考时允许更长的回答
        
        # 构建完整Prompt（包含历史对话）
        if history_text:
            full_prompt = f"{system_prompt}\n\n对话历史：\n{history_text}\n\n用户：{user_input}\n心语："
        else:
            full_prompt = f"{system_prompt}\n\n用户：{user_input}\n心语："
        
        try:
            api_url = f"{self.api_base_url}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [{"role": "system", "content": full_prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            response = requests.post(api_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                return self._get_fallback_response(user_input)
        except Exception as e:
            print(f"LLM调用失败: {e}")
            return self._get_fallback_response(user_input)
    
    def _get_personalized_system_prompt(self, user_id: str, user_input: str, 
                                       emotion_state: Optional[Dict] = None) -> str:
        """
        获取个性化系统Prompt
        如果用户配置了个性化设置，使用个性化Prompt；否则使用默认Prompt
        """
        if not self.personalization_service:
            return XINYU_SYSTEM_PROMPT
        
        try:
            # 获取数据库会话
            db_manager = DatabaseManager()
            with db_manager as db:
                # 生成个性化Prompt（传递数据库会话对象）
                personalized_prompt = self.personalization_service.generate_personalized_prompt(
                    user_id=user_id,
                    context=user_input,
                    emotion_state=emotion_state,
                    db=db.db  # 使用 db.db 访问实际的 Session 对象
                )
                return personalized_prompt
        except Exception as e:
            print(f"获取个性化Prompt失败，使用默认Prompt: {e}")
            import traceback
            traceback.print_exc()
            return XINYU_SYSTEM_PROMPT
    
    def analyze_emotion(self, message: str) -> Dict[str, Any]:
        """
        分析用户消息的情感（公开接口，兼容 SimpleEmotionalChatEngine）
        
        Args:
            message: 用户消息
            
        Returns:
            情感分析结果字典，包含 emotion, intensity, keywords, suggestions
        """
        return self._analyze_emotion_simple(message)
    
    def _analyze_emotion_simple(self, message: str) -> Dict[str, Any]:
        """简单的情感分析"""
        emotion_keywords = {
            "happy": ["开心", "高兴", "快乐", "兴奋", "满意", "幸福"],
            "sad": ["难过", "伤心", "沮丧", "失落", "痛苦", "抑郁"],
            "angry": ["愤怒", "生气", "恼火", "暴躁"],
            "anxious": ["焦虑", "担心", "紧张", "不安", "恐惧"],
            "excited": ["兴奋", "激动", "期待", "迫不及待"],
            "confused": ["困惑", "迷茫", "不明白", "不懂", "疑惑"],
            "frustrated": ["沮丧", "挫败", "失望", "无奈"],
            "lonely": ["孤独", "寂寞", "孤单"],
            "grateful": ["感谢", "感激", "谢谢"]
        }
        
        message_lower = message.lower()
        emotion_scores = {}
        
        for emotion, keywords in emotion_keywords.items():
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
            "keywords": emotion_keywords.get(dominant_emotion, []),
            "suggestions": suggestions
        }
    
    def _get_emotion_suggestions(self, emotion: str) -> List[str]:
        """获取情感建议"""
        suggestions_map = {
            "happy": ["很高兴看到你这么开心！", "你的快乐感染了我！", "太棒了！"],
            "sad": ["我理解你现在的心情。", "可以告诉我发生了什么吗？", "你并不孤单。"],
            "anxious": ["让我们先深呼吸一下。", "可以跟我说说你担心的事情吗？"],
            "neutral": ["今天感觉怎么样？", "我在这里倾听。"]
        }
        return suggestions_map.get(emotion, suggestions_map["neutral"])
    
    def _get_fallback_response(self, user_input: str) -> str:
        """备用回复"""
        emotion_data = self._analyze_emotion_simple(user_input)
        suggestions = emotion_data.get("suggestions", [])
        return suggestions[0] if suggestions else "我在这里倾听你的心声。"
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """获取会话摘要"""
        db_manager = DatabaseManager()
        with db_manager as db:
            messages = db.get_session_messages(session_id)
            
            if not messages:
                return {"error": "会话不存在"}
            
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
    
    def get_user_emotion_trends(self, user_id: str) -> Dict[str, Any]:
        """获取用户情感趋势"""
        db_manager = DatabaseManager()
        with db_manager as db:
            emotion_history = db.get_user_emotion_history(user_id, limit=100)
            
            if not emotion_history:
                return {"error": "没有情感数据"}
            
            emotions = [e.emotion for e in emotion_history]
            intensities = [e.intensity for e in emotion_history]
            
            return {
                "user_id": user_id,
                "total_records": len(emotion_history),
                "recent_emotions": emotions[:10],
                "average_intensity": sum(intensities) / len(intensities) if intensities else 0,
                "emotion_counts": {emotion: emotions.count(emotion) for emotion in set(emotions)}
            }
