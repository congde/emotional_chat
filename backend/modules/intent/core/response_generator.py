#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
响应生成器 - 核心模块
Response Generator Core Module

功能：
- 基于情感意图动态生成AI回复
- 融合规则引擎、缓存匹配和LLM生成的混合架构
- 实现情感一致性校验和反馈闭环
- 支持危机干预和个性化定制

架构：
1. 情感匹配决策引擎
2. 动态Prompt生成
3. 多策略响应生成（规则+缓存+LLM）
4. 情感一致性校验
5. 角色稳定性监控
"""

import yaml
import logging
import random
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from .dynamic_prompt_builder import DynamicPromptBuilder
from backend.utils.sentiment_classifier import SentimentClassifier

logger = logging.getLogger(__name__)


class ResponseGenerator:
    """响应生成器 - 混合架构"""
    
    def __init__(self, 
                 llm_client,
                 strategy_file: str = "/home/workSpace/emotional_chat/backend/config/emotion_strategy.yaml",
                 enable_consistency_check: bool = True,
                 enable_cache: bool = True):
        """
        初始化响应生成器
        
        Args:
            llm_client: 大模型客户端（需支持generate方法）
            strategy_file: 情感策略配置文件路径
            enable_consistency_check: 是否启用一致性检查
            enable_cache: 是否启用缓存匹配
        """
        self.llm_client = llm_client
        self.enable_consistency_check = enable_consistency_check
        self.enable_cache = enable_cache
        
        # 加载情感策略
        try:
            with open(strategy_file, 'r', encoding='utf-8') as f:
                self.emotion_strategy = yaml.safe_load(f)
            logger.info(f"✓ 加载情感策略配置: {strategy_file}")
        except Exception as e:
            logger.error(f"加载策略配置失败: {e}")
            self.emotion_strategy = {}
        
        # 初始化动态Prompt构建器
        self.prompt_builder = DynamicPromptBuilder(self.emotion_strategy)
        
        # 初始化情感一致性分类器
        if self.enable_consistency_check:
            self.sentiment_classifier = SentimentClassifier()
        
        # 缓存的固定回复（高频场景）
        self.cached_responses = self._load_cached_responses()
        
        # 统计信息
        self.stats = {
            "total_generations": 0,
            "rule_based": 0,
            "cached": 0,
            "llm_generated": 0,
            "consistency_failures": 0,
            "fallback_used": 0
        }
        
        logger.info("✓ 响应生成器已初始化")
    
    def generate_response(self,
                         user_input: str,
                         user_emotion: str,
                         user_id: str,
                         emotion_intensity: float = 5.0,
                         conversation_history: Optional[List[Dict]] = None,
                         retrieved_memories: Optional[List[Dict]] = None,
                         user_profile: Optional[Dict] = None,
                         metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        生成AI回复（主入口）
        
        Args:
            user_input: 用户输入
            user_emotion: 用户情绪
            user_id: 用户ID
            emotion_intensity: 情绪强度(0-10)
            conversation_history: 对话历史
            retrieved_memories: 检索到的记忆
            user_profile: 用户画像
            metadata: 额外元数据（如高风险关键词）
            
        Returns:
            生成结果字典，包含：
            - response: 生成的回复文本
            - generation_method: 生成方法（rule/cache/llm）
            - is_valid: 是否通过一致性检查
            - warnings: 警告信息
            - metadata: 元数据
        """
        self.stats["total_generations"] += 1
        
        result = {
            "response": "",
            "generation_method": "",
            "is_valid": True,
            "warnings": [],
            "metadata": {
                "user_emotion": user_emotion,
                "emotion_intensity": emotion_intensity,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        # 1. 检查是否为高风险情况（危机干预）
        if self._is_crisis_situation(user_emotion, metadata):
            response = self._handle_crisis(user_input, user_emotion, metadata)
            result["response"] = response
            result["generation_method"] = "rule_based_crisis"
            result["metadata"]["is_crisis"] = True
            self.stats["rule_based"] += 1
            logger.warning(f"危机干预触发 [user={user_id}]: {user_emotion}")
            return result
        
        # 2. 缓存匹配（高频固定场景）
        if self.enable_cache:
            cached_response = self._match_cached_response(user_input, user_emotion)
            if cached_response:
                result["response"] = cached_response
                result["generation_method"] = "cached"
                self.stats["cached"] += 1
                logger.debug(f"使用缓存回复 [user={user_id}]")
                return result
        
        # 3. LLM生成（主要路径）
        try:
            # 3.1 构建动态Prompt
            prompt = self.prompt_builder.build_prompt(
                user_input=user_input,
                emotion=user_emotion,
                emotion_intensity=emotion_intensity,
                conversation_history=conversation_history,
                retrieved_memories=retrieved_memories,
                user_profile=user_profile
            )
            
            # 3.2 调用大模型生成
            raw_response = self._call_llm(prompt)
            
            # 3.3 后处理
            processed_response = self._post_process_response(raw_response, user_emotion)
            
            # 3.4 情感一致性校验
            if self.enable_consistency_check:
                is_valid, warnings = self._validate_response(
                    processed_response, 
                    user_emotion,
                    self.emotion_strategy.get(user_emotion, {}).get("tone", "")
                )
                
                if not is_valid:
                    # 一致性检查失败，使用降级策略
                    logger.warning(f"一致性检查失败: {warnings}")
                    result["warnings"] = warnings
                    self.stats["consistency_failures"] += 1
                    
                    # 降级为预设回复
                    fallback = self._get_fallback_response(user_emotion)
                    result["response"] = fallback
                    result["generation_method"] = "fallback"
                    result["is_valid"] = False
                    result["metadata"]["original_response"] = processed_response
                    self.stats["fallback_used"] += 1
                    return result
            
            # 3.5 成功生成
            result["response"] = processed_response
            result["generation_method"] = "llm_generated"
            result["is_valid"] = True
            self.stats["llm_generated"] += 1
            
        except Exception as e:
            # 异常处理，使用兜底回复
            logger.error(f"LLM生成失败: {e}")
            result["response"] = self._get_fallback_response(user_emotion)
            result["generation_method"] = "fallback_error"
            result["is_valid"] = False
            result["warnings"].append(f"生成异常: {str(e)}")
            result["metadata"]["error"] = str(e)
            self.stats["fallback_used"] += 1
        
        return result
    
    def _is_crisis_situation(self, 
                            user_emotion: str, 
                            metadata: Optional[Dict]) -> bool:
        """
        判断是否为危机情况
        
        Args:
            user_emotion: 用户情绪
            metadata: 元数据
            
        Returns:
            是否为危机情况
        """
        # 1. 情绪类型判断
        if user_emotion == "high_risk_depression":
            return True
        
        # 2. 高风险关键词判断
        if metadata and metadata.get("requires_crisis_intervention"):
            return True
        
        if metadata and metadata.get("risk_keywords"):
            return True
        
        return False
    
    def _handle_crisis(self, 
                      user_input: str, 
                      user_emotion: str,
                      metadata: Optional[Dict]) -> str:
        """
        处理危机情况，返回预设的危机干预回复
        
        Args:
            user_input: 用户输入
            user_emotion: 用户情绪
            metadata: 元数据
            
        Returns:
            危机干预回复
        """
        # 获取危机策略
        crisis_strategy = self.emotion_strategy.get("high_risk_depression", {})
        
        # 使用预设的危机回复
        crisis_response = crisis_strategy.get("fallback", "")
        
        # 如果有配置的热线信息，可以动态添加
        hotlines = crisis_strategy.get("crisis_hotlines", [])
        
        if crisis_response:
            return crisis_response
        else:
            # 默认危机回复
            return """我非常关心你现在的情绪状态。你不是一个人，有很多人愿意帮助你。
建议你立即联系心理援助热线：
- 希望24热线：400-161-9995
- 北京心理危机干预中心：010-82951332
我会一直在这里陪你。"""
    
    def _match_cached_response(self, 
                               user_input: str, 
                               user_emotion: str) -> Optional[str]:
        """
        匹配缓存的固定回复
        
        Args:
            user_input: 用户输入
            user_emotion: 用户情绪
            
        Returns:
            匹配的回复，如果没有则返回None
        """
        input_lower = user_input.lower().strip()
        
        # 问候语
        greetings = ["你好", "hi", "hello", "嗨", "在吗", "在不在"]
        if any(g in input_lower for g in greetings) and len(input_lower) < 10:
            responses = self.cached_responses.get("greeting", [])
            return random.choice(responses) if responses else None
        
        # 道别语
        farewells = ["再见", "拜拜", "bye", "goodbye", "晚安"]
        if any(f in input_lower for f in farewells):
            responses = self.cached_responses.get("goodbye", [])
            return random.choice(responses) if responses else None
        
        # 感谢语
        thanks = ["谢谢", "感谢", "thanks", "thank you"]
        if any(t in input_lower for t in thanks) and len(input_lower) < 20:
            responses = self.cached_responses.get("thanks", [])
            return random.choice(responses) if responses else None
        
        return None
    
    def _call_llm(self, prompt: str) -> str:
        """
        调用大模型生成回复
        
        Args:
            prompt: 完整的Prompt
            
        Returns:
            生成的回复文本
        """
        # 根据不同的LLM客户端类型调用
        try:
            # 假设llm_client有generate或predict方法
            if hasattr(self.llm_client, 'generate'):
                response = self.llm_client.generate(prompt)
            elif hasattr(self.llm_client, 'predict'):
                response = self.llm_client.predict(prompt)
            elif hasattr(self.llm_client, 'invoke'):
                response = self.llm_client.invoke(prompt)
            else:
                # 尝试直接调用
                response = self.llm_client(prompt)
            
            # 如果返回的是对象，提取文本内容
            if hasattr(response, 'content'):
                response = response.content
            elif isinstance(response, dict) and 'content' in response:
                response = response['content']
            
            return str(response).strip()
            
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            raise
    
    def _post_process_response(self, response: str, user_emotion: str) -> str:
        """
        后处理生成的回复
        
        Args:
            response: 原始回复
            user_emotion: 用户情绪
            
        Returns:
            处理后的回复
        """
        # 1. 去除首尾空格和多余换行
        processed = response.strip()
        
        # 2. 去除可能的"心语："前缀（有些模型会重复）
        if processed.startswith("心语：") or processed.startswith("心语:"):
            processed = processed.split("：", 1)[-1].split(":", 1)[-1].strip()
        
        # 3. 限制长度（按句子数）
        strategy = self.emotion_strategy.get(user_emotion, {})
        max_sentences = strategy.get("max_length", 3)
        
        # 简单的句子分割（按标点）
        sentences = []
        for sep in ['。', '！', '？', '~', '\n']:
            if sep in processed:
                parts = processed.split(sep)
                sentences.extend([p.strip() + sep for p in parts if p.strip()])
                break
        
        if not sentences:
            sentences = [processed]
        
        # 保留前N句
        if len(sentences) > max_sentences:
            processed = "".join(sentences[:max_sentences])
        
        # 4. 确保不暴露AI身份
        identity_replacements = {
            "我是AI": "我是心语",
            "我是一个AI": "我是心语",
            "作为AI": "作为陪伴者",
            "AI助手": "陪伴者",
            "人工智能": "陪伴者"
        }
        for old, new in identity_replacements.items():
            if old in processed:
                processed = processed.replace(old, new)
                logger.warning(f"替换AI身份暴露词: {old} -> {new}")
        
        return processed
    
    def _validate_response(self, 
                          response: str, 
                          user_emotion: str,
                          expected_tone: str) -> Tuple[bool, List[str]]:
        """
        验证回复的情感一致性
        
        Args:
            response: 生成的回复
            user_emotion: 用户情绪
            expected_tone: 期望的语气
            
        Returns:
            (is_valid, warnings): 是否有效，警告列表
        """
        result = self.sentiment_classifier.comprehensive_check(
            ai_response=response,
            user_emotion=user_emotion,
            expected_tone=expected_tone
        )
        
        return result["is_valid"], result["warnings"]
    
    def _get_fallback_response(self, user_emotion: str) -> str:
        """
        获取兜底回复
        
        Args:
            user_emotion: 用户情绪
            
        Returns:
            兜底回复文本
        """
        # 从策略中获取fallback
        strategy = self.emotion_strategy.get(user_emotion, {})
        fallback = strategy.get("fallback", "")
        
        if fallback:
            return fallback
        
        # 默认兜底回复
        default_fallbacks = {
            "sad": "我听到了你的感受，我在这里陪着你。💙",
            "anxious": "我感受到了你的焦虑。深呼吸，我在这里陪着你。🌸",
            "angry": "我听到了你的愤怒。你有权利表达这种感受。",
            "happy": "很高兴看到你这么开心！😊",
            "excited": "你的兴奋感染了我！继续保持这份热情！⚡",
            "confused": "我理解你的困惑。我们可以一起慢慢理清。💭",
            "frustrated": "我听到了你的沮丧。你已经很努力了。💪",
            "lonely": "我在这里陪着你。你并不孤单。🤗",
            "grateful": "感恩的心很美好，谢谢你的分享。🙏",
            "neutral": "我在这里倾听。可以多说一些吗？😊"
        }
        
        return default_fallbacks.get(user_emotion, "我在这里倾听。请继续说吧。")
    
    def _load_cached_responses(self) -> Dict[str, List[str]]:
        """
        加载缓存的固定回复
        
        Returns:
            缓存回复字典
        """
        global_settings = self.emotion_strategy.get("global_settings", {})
        cached = global_settings.get("cached_responses", {})
        
        # 确保每个场景都有列表
        for key in ["greeting", "goodbye", "thanks"]:
            if key not in cached or not isinstance(cached[key], list):
                cached[key] = []
        
        return cached
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取生成器统计信息
        
        Returns:
            统计信息字典
        """
        total = self.stats["total_generations"]
        if total == 0:
            return self.stats
        
        return {
            **self.stats,
            "rule_based_rate": self.stats["rule_based"] / total,
            "cached_rate": self.stats["cached"] / total,
            "llm_rate": self.stats["llm_generated"] / total,
            "failure_rate": self.stats["consistency_failures"] / total,
            "fallback_rate": self.stats["fallback_used"] / total
        }
    
    def reset_statistics(self):
        """重置统计信息"""
        for key in self.stats:
            self.stats[key] = 0


# 便捷函数
def create_response_generator(llm_client, 
                             strategy_file: Optional[str] = None,
                             **kwargs) -> ResponseGenerator:
    """
    创建响应生成器实例
    
    Args:
        llm_client: LLM客户端
        strategy_file: 策略文件路径
        **kwargs: 其他参数
        
    Returns:
        ResponseGenerator实例
    """
    if strategy_file is None:
        strategy_file = "/home/workSpace/emotional_chat/backend/config/emotion_strategy.yaml"
    
    return ResponseGenerator(llm_client, strategy_file, **kwargs)


# 测试代码
if __name__ == "__main__":
    import sys
    sys.path.append("/home/workSpace/emotional_chat")
    
    logging.basicConfig(level=logging.INFO)
    
    # 模拟LLM客户端
    class MockLLMClient:
        def predict(self, prompt: str) -> str:
            # 简单的模拟回复
            if "悲伤" in prompt:
                return "我能感受到你现在的低落。但请相信，你的存在本身就有价值。我在这里，愿意听你说更多。💙"
            elif "焦虑" in prompt:
                return "焦虑的感觉确实不好受。深呼吸，让我们一步步来。我在这里陪着你。🌸"
            else:
                return "我在这里倾听。你想说什么都可以。😊"
    
    # 创建生成器
    mock_client = MockLLMClient()
    generator = ResponseGenerator(mock_client)
    
    # 测试用例
    test_cases = [
        {
            "user_input": "我今天被领导批评了，觉得自己一无是处",
            "user_emotion": "sad",
            "emotion_intensity": 7.5
        },
        {
            "user_input": "明天要面试，我好紧张",
            "user_emotion": "anxious",
            "emotion_intensity": 6.0
        },
        {
            "user_input": "你好",
            "user_emotion": "neutral",
            "emotion_intensity": 3.0
        }
    ]
    
    print("\n===== 响应生成测试 =====\n")
    for i, test in enumerate(test_cases, 1):
        print(f"测试 {i}:")
        print(f"用户输入: {test['user_input']}")
        print(f"情绪: {test['user_emotion']} (强度: {test['emotion_intensity']})")
        
        result = generator.generate_response(
            user_input=test['user_input'],
            user_emotion=test['user_emotion'],
            user_id="test_user",
            emotion_intensity=test['emotion_intensity']
        )
        
        print(f"生成方法: {result['generation_method']}")
        print(f"AI回复: {result['response']}")
        print(f"有效性: {'✓' if result['is_valid'] else '✗'}")
        if result['warnings']:
            print(f"警告: {', '.join(result['warnings'])}")
        print()
    
    # 统计信息
    print("===== 统计信息 =====")
    stats = generator.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")

