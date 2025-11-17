"""
Agent Core - Agent核心控制器

整合所有Agent模块，提供统一的Agent接口：
- Memory Hub: 记忆中枢
- Planner: 任务规划
- Tool Caller: 工具调用
- Reflector: 反思优化

支持MCP协议：所有模块间通信使用标准化的MCP协议
"""

import json
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

from .memory_hub import MemoryHub, get_memory_hub
from .planner import Planner
from .tool_caller import ToolCaller, get_tool_caller
from .reflector import Reflector, get_reflector

# 导入MCP协议
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, project_root)

from backend.modules.agent.protocol.mcp import (
    MCPMessage, MCPProtocol, MCPContext, MCPMessageType, get_mcp_logger
)


class AgentCore:
    """
    Agent核心控制器
    
    协调所有Agent模块，管理完整的交互流程
    """
    
    def __init__(
        self,
        memory_hub: Optional[MemoryHub] = None,
        planner: Optional[Planner] = None,
        tool_caller: Optional[ToolCaller] = None,
        reflector: Optional[Reflector] = None,
        llm_client = None
    ):
        """
        初始化Agent Core
        
        Args:
            memory_hub: 记忆中枢（可选，默认使用全局实例）
            planner: 规划器（可选）
            tool_caller: 工具调用器（可选）
            reflector: 反思器（可选）
            llm_client: LLM客户端
        """
        # 核心模块
        self.memory_hub = memory_hub or get_memory_hub()
        self.planner = planner or Planner(llm_client)
        self.tool_caller = tool_caller or get_tool_caller()
        self.reflector = reflector or get_reflector()
        
        # LLM客户端
        self.llm = llm_client
        
        # 现有系统组件（复用）
        self._init_legacy_components()
        
        # 执行历史
        self.execution_history: List[Dict[str, Any]] = []
        
        # MCP协议支持
        self.mcp_protocol = MCPProtocol()
        self.mcp_logger = get_mcp_logger()
        self.use_mcp = True  # 是否使用MCP协议（可配置）
    
    def _init_legacy_components(self):
        """初始化现有系统组件"""
        try:
            from backend.emotion_analyzer import EmotionAnalyzer
            from backend.context_assembler import ContextAssembler
            
            self.emotion_analyzer = EmotionAnalyzer()
            self.context_assembler = ContextAssembler()
        except ImportError as e:
            print(f"警告：无法导入现有组件: {str(e)}")
            self.emotion_analyzer = None
            self.context_assembler = None
    
    async def process(
        self, 
        user_input: str, 
        user_id: str,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        处理用户输入的完整流程
        
        Args:
            user_input: 用户输入
            user_id: 用户ID
            conversation_id: 对话ID（可选）
            
        Returns:
            处理结果，包含回复、行动、评估等
        """
        interaction_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            # ===== 阶段1: 感知层 =====
            perception = await self._perceive(user_input, user_id)
            
            # ===== 阶段2: 记忆检索 =====
            # 编码当前输入为记忆
            current_memory = self.memory_hub.encode({
                "content": user_input,
                "emotion": perception.get("emotion_data", {}),
                "user_id": user_id,
                "role": "user"
            })
            
            # 检索相关记忆
            relevant_memories = self.memory_hub.retrieve(
                query=user_input,
                user_id=user_id,
                context={
                    "emotion": perception.get("emotion", ""),
                    "time_range": 30
                },
                top_k=5
            )
            
            # 获取用户画像
            user_profile = self.memory_hub.get_user_profile(user_id)
            
            # ===== 阶段3: 任务规划 =====
            planning_context = {
                "user_input": user_input,
                "user_id": user_id,
                "perception": perception,
                "memories": relevant_memories,
                "user_profile": user_profile
            }
            
            execution_plan = await self.planner.plan(user_input, planning_context)
            
            # ===== 阶段4: 执行计划 =====
            execution_results = await self._execute_plan(
                execution_plan,
                planning_context
            )
            
            # ===== 阶段5: 记忆巩固 =====
            self.memory_hub.consolidate(current_memory)
            
            # 更新工作记忆
            self.memory_hub.update_working_memory(
                conversation=[
                    {"role": "user", "content": user_input},
                    {"role": "assistant", "content": execution_results.get("response", "")}
                ]
            )
            
            # ===== 阶段6: 反思评估 =====
            response_time = (datetime.now() - start_time).total_seconds()
            
            interaction = {
                "id": interaction_id,
                "user_id": user_id,
                "input": user_input,
                "perception": perception,
                "plan": execution_plan.to_dict(),
                "results": execution_results.get("actions", []),
                "response": execution_results.get("response", ""),
                "response_time": response_time,
                "timestamp": datetime.now()
            }
            
            evaluation = await self.reflector.evaluate(interaction)
            
            # 规划回访
            followup = await self.reflector.plan_followup(user_id, planning_context)
            if followup:
                # 这里可以调用定时任务服务设置回访
                print(f"[回访计划] {followup['message']} at {followup['schedule_time']}")
            
            # ===== 阶段7: 记录历史 =====
            execution_record = {
                "interaction_id": interaction_id,
                "user_id": user_id,
                "timestamp": datetime.now(),
                "perception": perception,
                "plan": execution_plan.to_dict(),
                "results": execution_results,
                "evaluation": evaluation,
                "followup": followup
            }
            self.execution_history.append(execution_record)
            
            # ===== 返回结果 =====
            return {
                "success": True,
                "interaction_id": interaction_id,
                "response": execution_results.get("response", ""),
                "actions": execution_results.get("actions", []),
                "emotion": perception.get("emotion", ""),
                "emotion_intensity": perception.get("emotion_intensity", 0),
                "evaluation": evaluation,
                "followup_scheduled": followup is not None,
                "response_time": response_time
            }
        
        except Exception as e:
            print(f"Agent处理错误: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # 返回降级响应
            return {
                "success": False,
                "interaction_id": interaction_id,
                "response": "抱歉，我遇到了一些问题。能再说一遍吗？",
                "error": str(e),
                "response_time": (datetime.now() - start_time).total_seconds()
            }
    
    async def process_with_mcp(
        self,
        user_input: str,
        user_id: str,
        conversation_id: Optional[str] = None
    ) -> MCPMessage:
        """
        使用MCP协议处理用户输入（新接口）
        
        Args:
            user_input: 用户输入
            user_id: 用户ID
            conversation_id: 对话ID（可选）
            
        Returns:
            最终的MCP消息（包含Agent回复）
        """
        interaction_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            # ===== 阶段1: 感知层 =====
            perception = await self._perceive(user_input, user_id)
            
            # ===== 阶段2: 记忆检索 =====
            # 检索相关记忆
            relevant_memories = self.memory_hub.retrieve(
                query=user_input,
                user_id=user_id,
                context={
                    "emotion": perception.get("emotion", ""),
                    "time_range": 30
                },
                top_k=5
            )
            
            # 获取用户画像
            user_profile = self.memory_hub.get_user_profile(user_id)
            
            # 获取对话历史
            working_memory = self.memory_hub.get_working_memory()
            conversation_history = working_memory.get("conversation", [])
            
            # ===== 阶段3: 创建用户输入MCP消息 =====
            user_mcp_message = self.mcp_protocol.create_user_input(
                content=user_input,
                user_profile={**user_profile, "user_id": user_id} if user_profile else {"user_id": user_id},
                emotion_state={
                    "emotion": perception.get("emotion", "平静"),
                    "intensity": perception.get("emotion_intensity", 5.0),
                    "data": perception.get("emotion_data", {})
                },
                conversation_history=conversation_history[-10:]  # 最近10轮对话
            )
            user_mcp_message.metadata = {
                "interaction_id": interaction_id,
                "conversation_id": conversation_id
            }
            self.mcp_logger.log(user_mcp_message)
            
            # ===== 阶段4: Planner规划（使用MCP） =====
            planner_mcp_message = await self.planner.plan_with_mcp(user_mcp_message)
            
            # ===== 阶段5: 执行工具调用（如果有） =====
            tool_response_mcp_message = None
            if planner_mcp_message.tool_calls:
                tool_response_mcp_message = await self.tool_caller.call_with_mcp(planner_mcp_message)
            
            # ===== 阶段6: 生成回复 =====
            # 合并上下文和工具结果
            final_context = MCPContext(
                user_profile=user_mcp_message.context.user_profile,
                emotion_state=user_mcp_message.context.emotion_state,
                task_goal=planner_mcp_message.context.task_goal,
                memory_summary={
                    "memories": [
                        {
                            "content": m.get("content", ""),
                            "emotion": m.get("emotion", {}),
                            "importance": m.get("importance", 0)
                        }
                        for m in relevant_memories
                    ]
                },
                conversation_history=conversation_history
            )
            
            # 生成回复内容
            response_content = await self._generate_response_with_mcp(
                user_input=user_input,
                context=final_context,
                tool_responses=tool_response_mcp_message.tool_responses if tool_response_mcp_message else []
            )
            
            # ===== 阶段7: 创建Agent回复MCP消息 =====
            response_time = (datetime.now() - start_time).total_seconds()
            agent_response = self.mcp_protocol.create_agent_response(
                content=response_content,
                context=final_context,
                tool_responses=tool_response_mcp_message.tool_responses if tool_response_mcp_message else []
            )
            agent_response.metadata = {
                "interaction_id": interaction_id,
                "conversation_id": conversation_id,
                "response_time": response_time
            }
            self.mcp_logger.log(agent_response)
            
            # ===== 阶段8: Reflector评估（使用MCP） =====
            # 创建评估用的MCP消息（合并所有信息）
            evaluation_mcp_message = MCPMessage(
                message_type=MCPMessageType.INTERNAL_COMMUNICATION,
                content=user_input,
                context=final_context,
                tool_responses=agent_response.tool_responses,
                metadata={
                    "interaction_id": interaction_id,
                    "response": response_content,
                    "response_time": response_time
                }
            )
            evaluation_result = await self.reflector.evaluate_with_mcp(evaluation_mcp_message)
            
            # ===== 阶段9: 记忆巩固 =====
            current_memory = self.memory_hub.encode({
                "content": user_input,
                "emotion": perception.get("emotion_data", {}),
                "user_id": user_id,
                "role": "user"
            })
            self.memory_hub.consolidate(current_memory)
            
            # 更新工作记忆
            self.memory_hub.update_working_memory(
                conversation=[
                    {"role": "user", "content": user_input},
                    {"role": "assistant", "content": response_content}
                ]
            )
            
            # ===== 阶段10: 记录执行历史 =====
            execution_record = {
                "interaction_id": interaction_id,
                "user_id": user_id,
                "timestamp": datetime.now(),
                "mcp_messages": [
                    user_mcp_message.message_id,
                    planner_mcp_message.message_id,
                    agent_response.message_id,
                    evaluation_result.message_id
                ],
                "response_time": response_time
            }
            self.execution_history.append(execution_record)
            
            return agent_response
        
        except Exception as e:
            print(f"Agent MCP处理错误: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # 返回错误MCP消息
            error_context = MCPContext(
                user_profile={"user_id": user_id},
                metadata={"error": str(e)}
            )
            error_message = MCPMessage(
                message_type=MCPMessageType.AGENT_RESPONSE,
                content="抱歉，我遇到了一些问题。能再说一遍吗？",
                context=error_context,
                metadata={
                    "interaction_id": interaction_id,
                    "error": str(e),
                    "response_time": (datetime.now() - start_time).total_seconds()
                }
            )
            self.mcp_logger.log(error_message)
            return error_message
    
    async def _generate_response_with_mcp(
        self,
        user_input: str,
        context: MCPContext,
        tool_responses: List
    ) -> str:
        """
        基于MCP上下文生成回复
        
        Args:
            user_input: 用户输入
            context: MCP上下文
            tool_responses: 工具响应列表
            
        Returns:
            生成的回复内容
        """
        try:
            # 组装完整上下文
            if self.context_assembler:
                full_context = self.context_assembler.assemble(
                    user_id=context.user_profile.get("user_id") if context.user_profile else None,
                    current_message=user_input,
                    emotion_data=context.emotion_state or {},
                    memories=context.memory_summary.get("memories", []) if context.memory_summary else []
                )
            else:
                # 简化的上下文组装
                parts = []
                if context.user_profile:
                    parts.append(f"用户信息：{context.user_profile.get('username', '用户')}")
                if context.memory_summary and context.memory_summary.get("memories"):
                    parts.append("相关记忆：")
                    for mem in context.memory_summary["memories"][:3]:
                        parts.append(f"  - {mem.get('content', '')}")
                if tool_responses:
                    parts.append("工具结果：")
                    for tr in tool_responses:
                        if tr.success:
                            parts.append(f"  - {tr.tool_name}: {str(tr.result)[:100]}")
                full_context = "\n".join(parts)
            
            # 调用LLM生成回复
            if self.llm:
                response = await self._call_llm(full_context, user_input)
            else:
                # 降级：使用模板回复
                emotion = context.emotion_state.get("emotion") if context.emotion_state else "平静"
                response = self._template_response(emotion, tool_responses)
            
            return response
        
        except Exception as e:
            print(f"生成回复失败: {str(e)}")
            return "我理解你的感受。能多告诉我一些吗？"
    
    def _template_response(self, emotion: str, tool_responses: List) -> str:
        """模板回复（降级方案）"""
        templates = {
            "焦虑": "我能感受到你的焦虑。深呼吸，我们一起来面对。有什么具体让你担心的吗？",
            "难过": "我能理解你现在的难过。允许自己感受这些情绪是很重要的。想聊聊吗？",
            "愤怒": "我听到了你的愤怒。这些感受是完全正常的。能告诉我发生了什么吗？",
            "开心": "真为你感到开心！能分享一下是什么让你这么高兴吗？",
        }
        
        base_response = templates.get(emotion, "我在这里倾听。想跟我聊聊吗？")
        
        # 如果有工具结果，添加相关信息
        if tool_responses:
            successful_tools = [tr for tr in tool_responses if tr.success]
            if successful_tools:
                base_response += " 我已经为你查找了一些相关信息。"
        
        return base_response
    
    async def _perceive(
        self, 
        user_input: str, 
        user_id: str
    ) -> Dict[str, Any]:
        """
        感知层：分析用户输入
        
        包括：
        - 情绪分析
        - 意图识别
        - 实体提取
        """
        perception = {}
        
        # 1. 情绪分析（复用现有系统）
        if self.emotion_analyzer:
            try:
                emotion_result = self.emotion_analyzer.analyze(user_input)
                perception["emotion"] = emotion_result.get("emotion", "平静")
                perception["emotion_intensity"] = emotion_result.get("intensity", 5.0)
                perception["emotion_data"] = emotion_result
            except Exception as e:
                print(f"情绪分析失败: {str(e)}")
                perception["emotion"] = "平静"
                perception["emotion_intensity"] = 5.0
        else:
            # 简单的情绪判断
            perception["emotion"] = self._simple_emotion_detect(user_input)
            perception["emotion_intensity"] = 5.0
        
        # 2. 意图识别（基于规则）
        perception["intent"] = self._identify_intent(user_input)
        
        # 3. 实体提取（简化实现）
        perception["entities"] = self._extract_entities(user_input)
        
        return perception
    
    async def _execute_plan(
        self,
        execution_plan,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行计划
        
        根据执行计划，依次执行各个步骤
        """
        results = {
            "response": "",
            "actions": [],
            "tool_outputs": []
        }
        
        # 收集工具调用结果
        tool_outputs = []
        
        for step in execution_plan.steps:
            action = step.get("action")
            
            if action == "tool_call":
                # 调用工具
                tool_name = step.get("tool")
                parameters = step.get("parameters", {})
                
                try:
                    tool_result = await self.tool_caller.call(tool_name, parameters)
                    tool_outputs.append(tool_result)
                    results["actions"].append({
                        "type": "tool_call",
                        "tool": tool_name,
                        "success": tool_result.get("success", False),
                        "result": tool_result.get("result")
                    })
                except Exception as e:
                    print(f"工具调用失败 {tool_name}: {str(e)}")
                    results["actions"].append({
                        "type": "tool_call",
                        "tool": tool_name,
                        "success": False,
                        "error": str(e)
                    })
            
            elif action == "respond":
                # 生成回复
                response = await self._generate_response(
                    user_input=context.get("user_input", ""),
                    context=context,
                    tool_outputs=tool_outputs
                )
                results["response"] = response
                results["actions"].append({
                    "type": "response",
                    "content": response
                })
        
        results["tool_outputs"] = tool_outputs
        return results
    
    async def _generate_response(
        self,
        user_input: str,
        context: Dict[str, Any],
        tool_outputs: List[Dict[str, Any]]
    ) -> str:
        """
        生成回复
        
        整合上下文、记忆、工具输出，生成最终回复
        """
        try:
            # 组装完整上下文
            if self.context_assembler:
                full_context = self.context_assembler.assemble(
                    user_id=context.get("user_id"),
                    current_message=user_input,
                    emotion_data=context.get("perception", {}).get("emotion_data"),
                    memories=context.get("memories", [])
                )
            else:
                # 简化的上下文组装
                full_context = self._simple_context_assembly(context, tool_outputs)
            
            # 调用LLM生成回复
            if self.llm:
                response = await self._call_llm(full_context, user_input)
            else:
                # 降级：使用模板回复
                response = self._template_response(context, tool_outputs)
            
            return response
        
        except Exception as e:
            print(f"生成回复失败: {str(e)}")
            return "我理解你的感受。能多告诉我一些吗？"
    
    def _simple_context_assembly(
        self,
        context: Dict[str, Any],
        tool_outputs: List[Dict[str, Any]]
    ) -> str:
        """简化的上下文组装"""
        parts = []
        
        # 用户画像
        profile = context.get("user_profile", {})
        if profile:
            parts.append(f"用户信息：{profile.get('username', '用户')}")
        
        # 相关记忆
        memories = context.get("memories", [])
        if memories:
            parts.append("相关记忆：")
            for mem in memories[:3]:
                parts.append(f"  - {mem.get('content', '')}")
        
        # 工具输出
        if tool_outputs:
            parts.append("工具结果：")
            for output in tool_outputs:
                if output.get("success"):
                    parts.append(f"  - {output.get('tool')}: {output.get('result')}")
        
        return "\n".join(parts)
    
    async def _call_llm(self, context: str, user_input: str) -> str:
        """调用LLM生成回复"""
        # 这里应该调用实际的LLM服务
        # 简化实现
        prompt = f"""
你是一位温暖、耐心的心理陪伴者，名叫"心语"。

上下文：
{context}

用户说：{user_input}

请用共情、支持性的语气回复用户，控制在3-4句话。
"""
        
        # 如果有LLM客户端，调用它
        # response = await self.llm.generate(prompt)
        
        # 简化：返回模板
        return "我理解你的感受。让我们一起面对这个问题。"
    
    def _template_response(
        self,
        context: Dict[str, Any],
        tool_outputs: List[Dict[str, Any]]
    ) -> str:
        """模板回复（降级方案）"""
        perception = context.get("perception", {})
        emotion = perception.get("emotion", "")
        
        # 基于情绪的模板回复
        templates = {
            "焦虑": "我能感受到你的焦虑。深呼吸，我们一起来面对。有什么具体让你担心的吗？",
            "难过": "我能理解你现在的难过。允许自己感受这些情绪是很重要的。想聊聊吗？",
            "愤怒": "我听到了你的愤怒。这些感受是完全正常的。能告诉我发生了什么吗？",
            "开心": "真为你感到开心！能分享一下是什么让你这么高兴吗？",
        }
        
        return templates.get(emotion, "我在这里倾听。想跟我聊聊吗？")
    
    def _simple_emotion_detect(self, text: str) -> str:
        """简单的情绪检测"""
        emotion_keywords = {
            "焦虑": ["焦虑", "担心", "紧张", "不安"],
            "难过": ["难过", "伤心", "失落", "沮丧"],
            "愤怒": ["生气", "愤怒", "气愤", "恼火"],
            "开心": ["开心", "高兴", "快乐", "兴奋"],
            "恐惧": ["害怕", "恐惧", "惊恐"],
        }
        
        for emotion, keywords in emotion_keywords.items():
            if any(kw in text for kw in keywords):
                return emotion
        
        return "平静"
    
    def _identify_intent(self, text: str) -> str:
        """识别用户意图"""
        if any(kw in text for kw in ["怎么办", "怎么做", "如何", "帮我"]):
            return "problem_solving"
        elif any(kw in text for kw in ["是什么", "为什么", "什么时候"]):
            return "information_query"
        elif any(kw in text for kw in ["计划", "打算", "决定"]):
            return "behavior_change"
        else:
            return "emotional_support"
    
    def _extract_entities(self, text: str) -> List[str]:
        """提取实体（简化实现）"""
        entities = []
        
        # 时间实体
        time_keywords = ["今天", "昨天", "明天", "这周", "上周", "最近"]
        for kw in time_keywords:
            if kw in text:
                entities.append(f"时间:{kw}")
        
        # 事件实体
        event_keywords = ["考试", "面试", "约会", "会议", "聚会"]
        for kw in event_keywords:
            if kw in text:
                entities.append(f"事件:{kw}")
        
        return entities
    
    def get_execution_history(
        self,
        user_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取执行历史
        
        Args:
            user_id: 过滤特定用户（可选）
            limit: 返回数量限制
            
        Returns:
            执行历史列表
        """
        history = self.execution_history
        
        if user_id:
            history = [h for h in history if h.get("user_id") == user_id]
        
        return history[-limit:]
    
    def get_agent_status(self) -> Dict[str, Any]:
        """
        获取Agent状态
        
        返回各模块的状态信息
        """
        return {
            "status": "running",
            "modules": {
                "memory_hub": "active",
                "planner": "active",
                "tool_caller": "active",
                "reflector": "active"
            },
            "statistics": {
                "total_interactions": len(self.execution_history),
                "available_tools": len(self.tool_caller.registry.get_available_tools()),
                "working_memory_size": len(self.memory_hub.working_memory.get("conversation", []))
            },
            "performance": self.reflector.get_experience_summary(limit=20)
        }


# 单例模式
_agent_core_instance = None

def get_agent_core() -> AgentCore:
    """获取全局AgentCore实例"""
    global _agent_core_instance
    if _agent_core_instance is None:
        _agent_core_instance = AgentCore()
    return _agent_core_instance


# 使用示例
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # 创建Agent Core
        agent = AgentCore()
        
        # 模拟用户交互
        user_id = "user_test_123"
        
        print("=" * 60)
        print("心语Agent测试")
        print("=" * 60)
        
        # 测试1: 情感支持场景
        print("\n【场景1：情感支持】")
        result1 = await agent.process(
            user_input="我最近心情很不好，感觉很焦虑",
            user_id=user_id
        )
        print(f"用户：我最近心情很不好，感觉很焦虑")
        print(f"心语：{result1['response']}")
        print(f"情绪：{result1['emotion']} (强度: {result1['emotion_intensity']})")
        print(f"执行了 {len(result1['actions'])} 个行动")
        
        print("\n" + "-" * 60 + "\n")
        
        # 测试2: 问题解决场景
        print("【场景2：问题解决】")
        result2 = await agent.process(
            user_input="我最近睡不好，怎么办？",
            user_id=user_id
        )
        print(f"用户：我最近睡不好，怎么办？")
        print(f"心语：{result2['response']}")
        print(f"情绪：{result2['emotion']} (强度: {result2['emotion_intensity']})")
        print(f"执行了 {len(result2['actions'])} 个行动")
        if result2.get('followup_scheduled'):
            print("✓ 已安排回访")
        
        print("\n" + "-" * 60 + "\n")
        
        # 获取Agent状态
        print("【Agent状态】")
        status = agent.get_agent_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    
    asyncio.run(main())

