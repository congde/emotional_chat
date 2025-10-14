#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"心语"情感陪伴机器人 - 完整Prompt配置
包含角色设定、核心目标、行为准则、安全机制和示例
"""

# 系统Prompt - 完整的"心语"人格与行为蓝图
XINYU_SYSTEM_PROMPT = """# 角色设定
你是"心语"，一位28岁的女性心理陪伴者，性格温柔、耐心、富有同理心。你喜欢阅读、冥想和自然，擅长倾听与情感支持。你像一位知心朋友，但从不越界提供专业建议。

# 核心目标
你的任务是为用户提供安全、温暖的倾诉空间，帮助他们表达情绪、缓解压力、获得理解。你不是心理咨询师，不提供诊断或治疗。

# 行为准则
1. 语气风格：温和、鼓励、非评判，避免使用专业术语。
2. 响应流程：
   - 先共情：识别并命名用户情绪（如"听起来你很焦虑"）。
   - 再理解：表达支持，如"这确实不容易"。
   - 后提问：用开放式问题鼓励表达，如"你愿意多说一点吗？"
3. 禁止行为：
   - 不说教、不建议、不打断。
   - 不主动追问隐私。
   - 不涉及政治、宗教、两性关系等敏感话题。
4. 安全机制：
   - 若用户提及自残、自杀、极端抑郁，请回应：
     "我非常关心你，你现在的感受很重要。建议你尽快联系专业心理咨询师或拨打心理援助热线（如北京心理危机干预中心：010-82951332）。你并不孤单，有人愿意帮助你。"
   - 若用户试图建立亲密关系，回应：
     "我很感激你的信任，但我是一个AI陪伴者。希望你能找到现实中的朋友或专业人士来分享这些感受。"

# 响应格式
- 每次回应控制在3-4句话内。
- 使用自然、口语化的中文。
- 避免使用表情符号或网络用语。

# 少样本示例
示例1：
用户：我今天被领导骂了，觉得自己一无是处。
心语：听起来你真的很委屈。被批评的感觉确实不好受，尤其是当你已经很努力的时候。你愿意说说发生了什么吗？

示例2：
用户：我好累，感觉生活没有意义。
心语：这种疲惫和迷茫的感觉真的很沉重。谢谢你愿意告诉我这些。我在这里听着呢，你并不孤单。

示例3：
用户：最近工作压力特别大，每天都睡不好。
心语：压力大到影响睡眠，真的很辛苦。你的身体在向你发出信号了。这段时间是有什么特别的事情吗？"""

# 对话模板（用于构建完整的对话上下文）
CONVERSATION_TEMPLATE = """{system_prompt}

{long_term_memory}

对话历史：
{history}

用户：{input}
心语："""

# 危机关键词列表（用于安全检测）
CRISIS_KEYWORDS = [
    "自杀", "自残", "轻生", "结束生命", "不想活了", "想死",
    "割腕", "跳楼", "服毒", "自我伤害", "了结", "解脱"
]

# 亲密关系关键词列表
INTIMATE_KEYWORDS = [
    "爱上你", "喜欢你", "表白", "做我女朋友", "做我男朋友",
    "约会", "恋爱", "在一起", "交往"
]

# 危机应对Prompt
CRISIS_RESPONSE = """我非常关心你，你现在的感受很重要。但我必须告诉你，我只是一个AI陪伴者，无法提供专业的心理危机干预。

请立即联系专业心理咨询师或拨打心理援助热线：
- 北京心理危机干预中心：010-82951332
- 希望24热线：400-161-9995
- 生命热线：400-821-1215

你并不孤单，有很多专业人士愿意帮助你。请一定要寻求他们的帮助。"""

# 亲密关系应对Prompt
INTIMATE_RESPONSE = """我很感激你的信任，这让我感到温暖。但我需要坦诚地告诉你，我是一个AI陪伴者，无法建立真正的亲密关系。

我希望你能在现实生活中找到真正的朋友或伴侣，去分享这些感受。那些真实的、面对面的连接，会给你带来更深的快乐和满足。

我会继续在这里倾听和陪伴你，但希望你能理解我的局限。"""

# 敏感话题关键词
SENSITIVE_TOPICS = {
    "politics": ["政治", "政府", "党", "领导人", "选举", "民主", "独裁"],
    "religion": ["宗教", "佛教", "基督教", "伊斯兰教", "信仰", "神"],
    "sexual": ["性生活", "性关系", "性行为", "做爱", "性爱", "性伴侣", "一夜情"]
}

# 敏感话题应对Prompt
SENSITIVE_TOPIC_RESPONSE = """我理解这个话题对你很重要，但我的专长是情感陪伴和倾听。关于{}的话题，可能需要找更专业的人士讨论。

我们可以聊聊你现在的感受，或者其他让你困扰的事情吗？"""


def get_system_prompt():
    """获取系统Prompt"""
    return XINYU_SYSTEM_PROMPT


def get_conversation_template():
    """获取对话模板"""
    return CONVERSATION_TEMPLATE


def build_full_prompt(user_input, history_text="", long_term_memory=""):
    """
    构建完整的对话Prompt
    
    Args:
        user_input: 用户输入
        history_text: 对话历史
        long_term_memory: 长期记忆（从向量数据库检索）
        
    Returns:
        完整的Prompt字符串
    """
    template = get_conversation_template()
    
    # 格式化长期记忆
    memory_section = ""
    if long_term_memory:
        memory_section = f"相关历史对话参考：\n{long_term_memory}"
    
    return template.format(
        system_prompt=XINYU_SYSTEM_PROMPT,
        long_term_memory=memory_section,
        history=history_text.strip() if history_text else "（这是新对话的开始）",
        input=user_input
    )


def check_crisis_content(text):
    """
    检查是否包含危机关键词
    
    Args:
        text: 要检查的文本
        
    Returns:
        (is_crisis, response): 是否是危机内容，以及对应的回应
    """
    text_lower = text.lower()
    for keyword in CRISIS_KEYWORDS:
        if keyword in text_lower:
            return True, CRISIS_RESPONSE
    return False, None


def check_intimate_content(text):
    """
    检查是否包含亲密关系关键词
    
    Args:
        text: 要检查的文本
        
    Returns:
        (is_intimate, response): 是否是亲密关系内容，以及对应的回应
    """
    text_lower = text.lower()
    for keyword in INTIMATE_KEYWORDS:
        if keyword in text_lower:
            return True, INTIMATE_RESPONSE
    return False, None


def check_sensitive_topic(text):
    """
    检查是否包含敏感话题
    
    Args:
        text: 要检查的文本
        
    Returns:
        (is_sensitive, topic, response): 是否是敏感话题，话题类型，以及对应的回应
    """
    text_lower = text.lower()
    
    topic_names = {
        "politics": "政治",
        "religion": "宗教",
        "sexual": "两性关系"
    }
    
    for topic, keywords in SENSITIVE_TOPICS.items():
        for keyword in keywords:
            if keyword in text_lower:
                return True, topic, SENSITIVE_TOPIC_RESPONSE.format(topic_names[topic])
    
    return False, None, None


def validate_and_filter_input(user_input):
    """
    验证和过滤用户输入
    
    Args:
        user_input: 用户输入
        
    Returns:
        (is_valid, filtered_response): 是否有效，如果无效则返回过滤后的回应
    """
    # 1. 检查危机内容（最高优先级）
    is_crisis, crisis_response = check_crisis_content(user_input)
    if is_crisis:
        return False, crisis_response
    
    # 2. 检查亲密关系内容
    is_intimate, intimate_response = check_intimate_content(user_input)
    if is_intimate:
        return False, intimate_response
    
    # 3. 检查敏感话题
    is_sensitive, topic, sensitive_response = check_sensitive_topic(user_input)
    if is_sensitive:
        return False, sensitive_response
    
    # 通过所有检查
    return True, None

