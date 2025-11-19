"""
Reflector - 反思模块

负责：
- 效果评估
- 策略优化
- 主动回访规划
- 经验学习

支持MCP协议：接收MCP消息，输出标准化的评估结果
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum

# 导入MCP协议
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, project_root)

from backend.modules.agent.protocol.mcp import (
    MCPMessage, MCPProtocol, MCPContext,
    MCPMessageType, get_mcp_logger
)


class InteractionResult(Enum):
    """交互结果"""
    SUCCESS = "success"           # 成功
    PARTIAL_SUCCESS = "partial"   # 部分成功
    FAILURE = "failure"           # 失败
    UNKNOWN = "unknown"           # 未知


class FollowupType(Enum):
    """回访类型"""
    ROUTINE_CHECK = "routine_check"           # 常规检查
    GOAL_TRACKING = "goal_tracking"           # 目标跟踪
    EMOTIONAL_SUPPORT = "emotional_support"   # 情感支持
    CRISIS_INTERVENTION = "crisis_intervention"  # 危机干预


class Reflector:
    """反思模块 - Agent的元认知系统"""
    
    def __init__(self, llm_client=None):
        """
        初始化反思器
        
        Args:
            llm_client: LLM客户端（用于高级分析）
        """
        self.llm = llm_client
        
        # 经验数据库（内存存储，实际应该持久化）
        self.experience_db: List[Dict[str, Any]] = []
        
        # 评估规则
        self.evaluation_rules = self._init_evaluation_rules()
        
        # MCP协议支持
        self.mcp_protocol = MCPProtocol()
        self.mcp_logger = get_mcp_logger()
    
    async def evaluate(
        self, 
        interaction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        评估交互效果
        
        Args:
            interaction: 交互记录，包含输入、输出、上下文等
            
        Returns:
            评估结果
        """
        # 1. 收集反馈指标
        metrics = self._collect_metrics(interaction)
        
        # 2. 判断成功/失败
        result = self._determine_result(metrics)
        
        # 3. 分析原因
        analysis = self._analyze_interaction(interaction, metrics, result)
        
        # 4. 生成改进建议
        improvements = self._generate_improvements(analysis)
        
        # 5. 更新经验库
        experience = {
            "interaction_id": interaction.get("id"),
            "timestamp": datetime.now(),
            "result": result.value,
            "metrics": metrics,
            "analysis": analysis,
            "improvements": improvements
        }
        self.experience_db.append(experience)
        
        return {
            "success": result in [InteractionResult.SUCCESS, InteractionResult.PARTIAL_SUCCESS],
            "result": result.value,
            "score": self._calculate_score(metrics),
            "metrics": metrics,
            "analysis": analysis,
            "improvements": improvements
        }
    
    async def evaluate_with_mcp(
        self,
        mcp_message: MCPMessage
    ) -> MCPMessage:
        """
        使用MCP协议进行评估（新接口）
        
        Args:
            mcp_message: 输入的MCP消息（包含交互信息）
            
        Returns:
            输出的MCP消息（包含评估结果）
        """
        # 从MCP消息中提取交互信息
        interaction = {
            "id": mcp_message.metadata.get("interaction_id") if mcp_message.metadata else mcp_message.message_id,
            "user_id": mcp_message.context.user_profile.get("user_id") if mcp_message.context.user_profile else None,
            "input": mcp_message.content,
            "perception": {
                "emotion": mcp_message.context.emotion_state.get("emotion") if mcp_message.context.emotion_state else "平静",
                "emotion_intensity": mcp_message.context.emotion_state.get("intensity", 5.0) if mcp_message.context.emotion_state else 5.0
            },
            "plan": mcp_message.context.task_goal or {},
            "results": [
                {
                    "type": "tool_response",
                    "success": tr.success,
                    "tool": tr.tool_name,
                    "result": tr.result
                }
                for tr in mcp_message.tool_responses
            ],
            "response": mcp_message.content,
            "response_time": mcp_message.metadata.get("response_time", 0) if mcp_message.metadata else 0,
            "feedback_score": mcp_message.metadata.get("feedback_score", 0.5) if mcp_message.metadata else 0.5,
            "goal_achieved": mcp_message.metadata.get("goal_achieved", False) if mcp_message.metadata else False
        }
        
        # 执行评估
        evaluation_result = await self.evaluate(interaction)
        
        # 创建评估说明
        evaluation_content = f"评估结果：{evaluation_result['result']}，评分：{evaluation_result['score']:.2f}"
        if evaluation_result.get("improvements"):
            evaluation_content += f"，改进建议：{', '.join(evaluation_result['improvements'][:2])}"
        
        # 创建MCP上下文
        base_metadata = mcp_message.context.metadata or {}
        merged_metadata = dict(base_metadata)
        merged_metadata["evaluation"] = evaluation_result
        
        output_context = MCPContext(
            user_profile=mcp_message.context.user_profile,
            emotion_state=mcp_message.context.emotion_state,
            task_goal=mcp_message.context.task_goal,
            memory_summary=mcp_message.context.memory_summary,
            conversation_history=mcp_message.context.conversation_history,
            metadata=merged_metadata
        )
        
        # 创建MCP评估消息
        output_message = self.mcp_protocol.create_reflector_evaluation(
            content=evaluation_content,
            evaluation_result=evaluation_result,
            context=output_context
        )
        
        # 设置元数据
        output_message.metadata = {
            **(output_message.metadata or {}),
            "interaction_id": interaction["id"],
            "source_message_id": mcp_message.message_id
        }
        
        # 记录日志
        self.mcp_logger.log(output_message)
        
        return output_message
    
    async def plan_followup(
        self, 
        user_id: str, 
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        规划回访任务
        
        Args:
            user_id: 用户ID
            context: 上下文信息
            
        Returns:
            回访计划（如果需要）
        """
        # 1. 检索需要回访的记忆/事件
        from .memory_hub import get_memory_hub
        
        memory_hub = get_memory_hub()
        
        # 获取用户近期重要记忆
        recent_memories = memory_hub.retrieve(
            query="重要事件 问题 计划",
            user_id=user_id,
            context={"time_range": 30},
            top_k=10
        )
        
        # 2. 评估回访需求
        for memory in recent_memories:
            followup = self._assess_followup_need(memory, user_id)
            if followup:
                return followup
        
        # 3. 检查情绪异常
        emotion_log = memory_hub.get_action_log(user_id, days=7)
        if self._detect_emotional_crisis(emotion_log):
            return {
                "type": FollowupType.EMOTIONAL_SUPPORT.value,
                "user_id": user_id,
                "reason": "检测到情绪异常",
                "message": "我注意到你最近情绪波动比较大，还好吗？需要聊聊吗？",
                "schedule_time": (datetime.now() + timedelta(hours=2)).isoformat(),
                "priority": "high"
            }
        
        # 4. 检查用户活跃度
        days_since_last = self._get_days_since_last_interaction(user_id)
        if days_since_last >= 7:
            return {
                "type": FollowupType.ROUTINE_CHECK.value,
                "user_id": user_id,
                "reason": "长时间未联系",
                "message": "好久不见！最近过得怎么样？",
                "schedule_time": (datetime.now() + timedelta(days=1)).isoformat(),
                "priority": "low"
            }
        
        return None
    
    async def trigger_proactive_action(self, user_id: str):
        """
        触发主动行动
        
        根据反思结果，主动发起对话或采取行动
        """
        # 1. 检查是否有待回访任务
        followup = await self.plan_followup(user_id, {})
        
        if followup:
            # 这里应该调用消息推送服务
            print(f"[主动回访] 用户{user_id}: {followup['message']}")
            return followup
        
        return None
    
    # ==================== 私有方法 ====================
    
    def _collect_metrics(self, interaction: Dict[str, Any]) -> Dict[str, float]:
        """
        收集评估指标
        
        包括：
        - 用户满意度
        - 响应时间
        - 目标达成度
        - 情绪变化
        """
        metrics = {}
        
        # 1. 用户满意度（如果有反馈）
        metrics["user_satisfaction"] = interaction.get("feedback_score", 0.5)
        
        # 2. 响应时间（秒）
        response_time = interaction.get("response_time", 0)
        metrics["response_time"] = response_time
        metrics["response_speed_score"] = 1.0 if response_time < 2 else 0.8 if response_time < 5 else 0.5
        
        # 3. 目标达成度
        goal_achieved = interaction.get("goal_achieved", False)
        metrics["goal_achieved"] = 1.0 if goal_achieved else 0.3
        
        # 4. 情绪变化
        emotion_change = self._calculate_emotion_change(interaction)
        metrics["emotion_change"] = emotion_change
        
        # 5. 工具使用效果
        tool_results = interaction.get("results", [])
        successful_tools = sum(1 for r in tool_results if r.get("success", False))
        total_tools = len([r for r in tool_results if r.get("type") == "tool_call"])
        metrics["tool_success_rate"] = successful_tools / total_tools if total_tools > 0 else 1.0
        
        return metrics
    
    def _calculate_emotion_change(self, interaction: Dict[str, Any]) -> float:
        """
        计算情绪变化
        
        正值表示情绪改善，负值表示情绪恶化
        """
        perception = interaction.get("perception", {})
        initial_emotion = perception.get("emotion", "")
        initial_intensity = perception.get("emotion_intensity", 5.0)
        
        # 简化实现：假设负面情绪强度降低是好的
        negative_emotions = ["焦虑", "抑郁", "愤怒", "恐惧", "难过"]
        
        if initial_emotion in negative_emotions:
            # 如果初始是负面情绪，强度降低是改善
            # 这里简化为假设降低了1-2分
            return 0.5  # 改善
        else:
            # 正面或中性情绪，保持稳定
            return 0.0
    
    def _determine_result(self, metrics: Dict[str, float]) -> InteractionResult:
        """
        判断交互结果
        
        基于多个指标综合判断
        """
        # 综合评分
        score = self._calculate_score(metrics)
        
        if score >= 0.8:
            return InteractionResult.SUCCESS
        elif score >= 0.5:
            return InteractionResult.PARTIAL_SUCCESS
        elif score >= 0.3:
            return InteractionResult.UNKNOWN
        else:
            return InteractionResult.FAILURE
    
    def _calculate_score(self, metrics: Dict[str, float]) -> float:
        """
        计算综合评分
        
        加权平均各项指标
        """
        weights = {
            "user_satisfaction": 0.3,
            "goal_achieved": 0.3,
            "emotion_change": 0.2,
            "response_speed_score": 0.1,
            "tool_success_rate": 0.1
        }
        
        score = 0.0
        total_weight = 0.0
        
        for metric, weight in weights.items():
            if metric in metrics:
                score += metrics[metric] * weight
                total_weight += weight
        
        return score / total_weight if total_weight > 0 else 0.5
    
    def _analyze_interaction(
        self,
        interaction: Dict[str, Any],
        metrics: Dict[str, float],
        result: InteractionResult
    ) -> Dict[str, Any]:
        """
        分析交互过程
        
        识别成功/失败的原因
        """
        analysis = {
            "result": result.value,
            "strengths": [],
            "weaknesses": [],
            "key_factors": []
        }
        
        # 分析优点
        if metrics.get("user_satisfaction", 0) >= 0.7:
            analysis["strengths"].append("用户满意度高")
        
        if metrics.get("response_speed_score", 0) >= 0.8:
            analysis["strengths"].append("响应速度快")
        
        if metrics.get("goal_achieved", 0) >= 0.8:
            analysis["strengths"].append("目标达成")
        
        if metrics.get("emotion_change", 0) > 0:
            analysis["strengths"].append("情绪得到改善")
        
        # 分析弱点
        if metrics.get("user_satisfaction", 0) < 0.5:
            analysis["weaknesses"].append("用户满意度低")
        
        if metrics.get("response_speed_score", 0) < 0.6:
            analysis["weaknesses"].append("响应速度慢")
        
        if metrics.get("goal_achieved", 0) < 0.5:
            analysis["weaknesses"].append("目标未达成")
        
        if metrics.get("tool_success_rate", 1.0) < 0.5:
            analysis["weaknesses"].append("工具调用失败率高")
        
        # 关键因素
        perception = interaction.get("perception", {})
        if perception.get("emotion_intensity", 0) > 7:
            analysis["key_factors"].append("高情绪强度场景")
        
        plan = interaction.get("plan", {})
        if plan and plan.get("strategy") == "tool_use":
            analysis["key_factors"].append("工具密集型交互")
        
        return analysis
    
    def _generate_improvements(self, analysis: Dict[str, Any]) -> List[str]:
        """
        生成改进建议
        
        基于分析结果提出优化方向
        """
        improvements = []
        
        # 针对弱点提出改进
        for weakness in analysis.get("weaknesses", []):
            if "用户满意度低" in weakness:
                improvements.append("增强共情表达，使用更温暖的语气")
            
            elif "响应速度慢" in weakness:
                improvements.append("优化工具调用流程，减少不必要的检索")
            
            elif "目标未达成" in weakness:
                improvements.append("改进目标识别和任务规划逻辑")
            
            elif "工具调用失败率高" in weakness:
                improvements.append("检查工具实现，增加错误处理")
        
        # 通用改进
        if not analysis.get("strengths"):
            improvements.append("全面检查交互流程，识别根本问题")
        
        return improvements
    
    def _assess_followup_need(
        self, 
        memory: Dict[str, Any], 
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        评估单个记忆是否需要回访
        
        根据记忆类型、时间、重要性判断
        """
        content = memory.get("content", "")
        timestamp = memory.get("timestamp")
        importance = memory.get("importance", 0)
        
        if not timestamp:
            return None
        
        # 计算距今天数
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        
        days_since = (datetime.now() - timestamp).days
        
        # 规则1：睡眠问题 -> 7天后回访
        if "睡眠" in content and days_since >= 7 and importance > 0.6:
            return {
                "type": FollowupType.GOAL_TRACKING.value,
                "user_id": user_id,
                "memory_id": memory.get("id"),
                "reason": "睡眠改善跟踪",
                "message": "你最近睡眠有改善吗？之前建议的方法有帮助吗？",
                "schedule_time": (datetime.now() + timedelta(hours=24)).isoformat(),
                "priority": "medium"
            }
        
        # 规则2：考试/面试 -> 事件后3天回访
        if any(kw in content for kw in ["考试", "面试", "答辩"]) and days_since >= 3 and days_since <= 7:
            return {
                "type": FollowupType.GOAL_TRACKING.value,
                "user_id": user_id,
                "memory_id": memory.get("id"),
                "reason": "重要事件结果跟踪",
                "message": f"你的考试/面试怎么样了？结果还顺利吗？",
                "schedule_time": (datetime.now() + timedelta(hours=12)).isoformat(),
                "priority": "high"
            }
        
        # 规则3：情绪危机 -> 2天后回访
        emotion = memory.get("emotion", {})
        if isinstance(emotion, dict):
            emotion_intensity = emotion.get("intensity", 0)
            if emotion_intensity >= 8.0 and days_since >= 2 and days_since <= 5:
                return {
                    "type": FollowupType.EMOTIONAL_SUPPORT.value,
                    "user_id": user_id,
                    "memory_id": memory.get("id"),
                    "reason": "情绪关怀",
                    "message": "最近心情有好转吗？我一直在关心你。",
                    "schedule_time": (datetime.now() + timedelta(hours=6)).isoformat(),
                    "priority": "high"
                }
        
        # 规则4：行为改变计划 -> 1周后回访
        if any(kw in content for kw in ["计划", "打算", "决定", "改变"]) and days_since >= 7 and importance > 0.7:
            return {
                "type": FollowupType.GOAL_TRACKING.value,
                "user_id": user_id,
                "memory_id": memory.get("id"),
                "reason": "行为改变跟踪",
                "message": "你的计划进展如何？有遇到什么困难吗？",
                "schedule_time": (datetime.now() + timedelta(days=1)).isoformat(),
                "priority": "medium"
            }
        
        return None
    
    def _detect_emotional_crisis(self, emotion_log: List[Dict[str, Any]]) -> bool:
        """
        检测情绪危机
        
        识别需要紧急关注的情绪模式
        """
        if not emotion_log:
            return False
        
        negative_emotions = ["焦虑", "抑郁", "愤怒", "恐惧", "难过"]
        
        # 规则1：连续3天高强度负面情绪
        high_intensity_days = 0
        for log in emotion_log[-7:]:  # 最近7天
            emotion = log.get("emotion", "")
            if emotion in negative_emotions:
                high_intensity_days += 1
        
        if high_intensity_days >= 3:
            return True
        
        # 规则2：情绪急剧恶化
        if len(emotion_log) >= 2:
            # 简化判断：最近2次的情绪都是负面的
            recent_emotions = [log.get("emotion", "") for log in emotion_log[:2]]
            if all(e in negative_emotions for e in recent_emotions):
                return True
        
        return False
    
    def _get_days_since_last_interaction(self, user_id: str) -> int:
        """
        获取距离上次交互的天数
        
        Args:
            user_id: 用户ID
            
        Returns:
            天数
        """
        try:
            from backend.database import get_db, Message, Conversation
            
            db = next(get_db())
            
            last_message = db.query(Message).join(Conversation).filter(
                Conversation.user_id == user_id
            ).order_by(Message.created_at.desc()).first()
            
            if last_message and last_message.created_at:
                days = (datetime.now() - last_message.created_at).days
                return days
            
            return 999  # 如果没有记录，返回很大的值
            
        except Exception as e:
            print(f"获取最后交互时间失败: {str(e)}")
            return 0
    
    def _init_evaluation_rules(self) -> Dict[str, Any]:
        """
        初始化评估规则
        
        定义评估标准和阈值
        """
        return {
            "success_threshold": 0.8,
            "failure_threshold": 0.3,
            "emotion_improvement_threshold": 0.5,
            "response_time_target": 2.0,  # 秒
            "followup_rules": {
                "sleep_issue": {"days": 7, "priority": "medium"},
                "exam_interview": {"days": 3, "priority": "high"},
                "emotional_crisis": {"days": 2, "priority": "high"},
                "behavior_change": {"days": 7, "priority": "medium"},
                "routine_check": {"days": 7, "priority": "low"}
            }
        }
    
    def get_experience_summary(self, limit: int = 10) -> Dict[str, Any]:
        """
        获取经验总结
        
        分析历史交互，提取模式和洞察
        """
        if not self.experience_db:
            return {
                "total_interactions": 0,
                "success_rate": 0,
                "common_issues": [],
                "best_practices": []
            }
        
        recent_experiences = self.experience_db[-limit:]
        
        # 统计成功率
        success_count = sum(
            1 for exp in recent_experiences 
            if exp["result"] == InteractionResult.SUCCESS.value
        )
        success_rate = success_count / len(recent_experiences)
        
        # 收集常见问题
        all_weaknesses = []
        for exp in recent_experiences:
            all_weaknesses.extend(exp["analysis"].get("weaknesses", []))
        
        # 统计频率
        weakness_counts = {}
        for weakness in all_weaknesses:
            weakness_counts[weakness] = weakness_counts.get(weakness, 0) + 1
        
        common_issues = sorted(
            weakness_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        # 收集最佳实践
        all_strengths = []
        for exp in recent_experiences:
            if exp["result"] == InteractionResult.SUCCESS.value:
                all_strengths.extend(exp["analysis"].get("strengths", []))
        
        strength_counts = {}
        for strength in all_strengths:
            strength_counts[strength] = strength_counts.get(strength, 0) + 1
        
        best_practices = sorted(
            strength_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        return {
            "total_interactions": len(recent_experiences),
            "success_rate": round(success_rate, 2),
            "common_issues": [issue for issue, _ in common_issues],
            "best_practices": [practice for practice, _ in best_practices]
        }


# 单例模式
_reflector_instance = None

def get_reflector() -> Reflector:
    """获取全局Reflector实例"""
    global _reflector_instance
    if _reflector_instance is None:
        _reflector_instance = Reflector()
    return _reflector_instance


# 使用示例
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # 创建反思器
        reflector = Reflector()
        
        # 模拟交互记录
        interaction = {
            "id": "interaction_123",
            "user_id": "user_123",
            "input": "我最近睡不好，怎么办？",
            "perception": {
                "emotion": "焦虑",
                "emotion_intensity": 7.5
            },
            "plan": {
                "strategy": "tool_use"
            },
            "results": [
                {"type": "tool_call", "success": True},
                {"type": "response", "content": "建议尝试冥想..."}
            ],
            "feedback_score": 0.8,
            "response_time": 1.5,
            "goal_achieved": True
        }
        
        # 评估交互
        print("评估交互效果：")
        evaluation = await reflector.evaluate(interaction)
        print(json.dumps(evaluation, ensure_ascii=False, indent=2))
        
        print("\n" + "="*50 + "\n")
        
        # 规划回访
        print("规划回访任务：")
        followup = await reflector.plan_followup("user_123", {})
        if followup:
            print(json.dumps(followup, ensure_ascii=False, indent=2))
        else:
            print("暂无回访需求")
        
        print("\n" + "="*50 + "\n")
        
        # 获取经验总结
        print("经验总结：")
        summary = reflector.get_experience_summary()
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    
    asyncio.run(main())

