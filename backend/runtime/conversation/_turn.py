# -*- coding: utf-8 -*-
"""
TurnMixin — ReAct loop (替代原 7 阶段线性 Workflow)

核心循环：
  用户输入 → Skill 链执行 → LLM 响应 → 工具调用(可选) → 下一次迭代

与原 AgentCore.process() 的区别：
  原: 7 阶段顺序执行 (感知→记忆→规划→执行→巩固→反思→记录)
  新: ReAct loop + Skill 链 (每次迭代执行适用的 Skill 集合)
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, AsyncGenerator, Dict, List, Optional

from backend.runtime.skills.base import SkillContext, SkillResult
from backend.runtime.session.fsm import SessionState
from backend.runtime.config.guards import is_module_enabled
from backend.runtime.hooks.base import HookContext
from backend.runtime.conversation._helpers import TurnResult, _done_dict, _error_dict

logger = logging.getLogger(__name__)


class TurnMixin:
    """
    Turn 执行 Mixin — ReAct loop

    负责：
    - 执行 Skill 链
    - LLM 调用 (stream / complete)
    - 工具调用循环
    - 策略评估
    - 预算管理
    """

    async def process_turn(
        self,
        user_input: str,
        **kwargs,
    ) -> TurnResult:
        """
        处理一轮对话 — 替代原 AgentCore.process()

        ReAct loop:
          1. 构建 SkillContext
          2. 执行 Skill 链 (emotion → memory → planning → tool → reflect)
          3. 策略评估 (policy engine)
          4. LLM 生成响应
          5. 记忆巩固
          6. 返回 TurnResult

        Args:
            user_input: 用户输入
            **kwargs: 额外参数

        Returns:
            TurnResult
        """
        start_time = time.time()
        self._current_iteration = 0
        self._tool_call_count = 0

        try:
            # ── 1. 构建 SkillContext ──
            context = SkillContext(
                session_id=self._session_id,
                user_id=self._user_id,
                workspace_id=self._workspace_id,
                user_input=user_input,
                iteration=1,
            )

            # ── 2. 执行 Skill 链 ──
            skill_results: Dict[str, SkillResult] = {}

            # 获取适用的 Skills
            applicable_skills = self._skill_registry.get_applicable_skills(context)

            for skill in applicable_skills:
                if self._cancel_requested:
                    break

                self._current_iteration += 1
                context.iteration = self._current_iteration

                # 更新 context 中的前序结果
                context.prev_results = skill_results

                # 策略评估
                if is_module_enabled("policy_engine"):
                    policy_context = self._build_policy_context(context, skill.name)
                    actions = self._policy_engine.evaluate(policy_context)
                    if self._should_skip_skill(actions):
                        logger.info("Skill '%s' skipped by policy", skill.name)
                        continue

                # 执行 Skill
                try:
                    result = await skill.execute(context)
                    skill_results[skill.name] = result

                    # 更新 context
                    if skill.name == "emotion_skill" and result.success:
                        context.emotion_data = result.output or {}
                    elif skill.name == "memory_skill" and result.success and result.output:
                        if isinstance(result.output, list):
                            context.memories = result.output

                except Exception as e:
                    logger.error("Skill '%s' failed: %s", skill.name, e, exc_info=True)
                    skill_results[skill.name] = SkillResult(
                        success=False,
                        error=str(e),
                        skill_name=skill.name,
                    )

                # 检查迭代上限
                if self._current_iteration >= self._max_iterations:
                    logger.warning("Max iterations reached: %d", self._max_iterations)
                    break

            # ── 3. LLM 生成响应 ──
            response = ""
            if self._llm and not self._cancel_requested:
                response = await self._generate_response(user_input, context, skill_results)

            # ── 4. 记忆巩固 ──
            if is_module_enabled("memory_skill"):
                memory_skill = self._skill_registry.get_skill("memory_skill")
                if memory_skill:
                    try:
                        await memory_skill.execute(context, mode="consolidate")
                    except Exception as e:
                        logger.warning("Memory consolidation failed: %s", e)

            # ── 5. 反思评估 ──
            if is_module_enabled("reflect_skill"):
                reflect_skill = self._skill_registry.get_skill("reflect_skill")
                if reflect_skill:
                    try:
                        evaluate_context = SkillContext(
                            session_id=self._session_id,
                            user_id=self._user_id,
                            workspace_id=self._workspace_id,
                            metadata={"interaction_complete": True},
                        )
                        evaluation = await reflect_skill.execute(
                            evaluate_context,
                            mode="evaluate",
                            interaction={
                                "id": self._session_id,
                                "user_input": user_input,
                                "emotion_data": context.emotion_data,
                                "skill_results": {k: v.to_dict() for k, v in skill_results.items()},
                                "response": response,
                                "response_time": time.time() - start_time,
                            },
                        )
                        skill_results["reflect_skill"] = evaluation
                    except Exception as e:
                        logger.warning("Reflect evaluation failed: %s", e)

            # ── 6. 返回结果 ──
            emotion_tag = context.emotion_data.get("emotion") if context.emotion_data else None

            return TurnResult(
                success=True,
                response=response,
                skill_results={k: v.to_dict() for k, v in skill_results.items()},
                emotion_tag=emotion_tag,
                iterations=self._current_iteration,
                stop_reason="complete" if not self._cancel_requested else "cancelled",
                usage={
                    "input_tokens": self._input_tokens_last,
                    "output_tokens": self._output_tokens_last,
                    "total_tokens": self._tokens_total,
                },
            )

        except Exception as e:
            logger.error("Turn processing failed: %s", e, exc_info=True)
            return TurnResult(
                success=False,
                stop_reason="error",
                metadata={"error": str(e)},
            )

    async def _generate_response(
        self,
        user_input: str,
        context: SkillContext,
        skill_results: Dict[str, SkillResult],
    ) -> str:
        """使用 LLM 生成响应"""
        if not self._llm:
            return ""

        try:
            # 构建消息
            messages = self._build_messages(user_input, context, skill_results)

            # Hook: pre_llm_call
            hook_ctx = HookContext(
                session_id=self._session_id,
                workspace_id=self._workspace_id,
                iteration=self._current_iteration,
                model=getattr(self._llm, "model_name", "unknown"),
                is_fallback=False,
                emotion_tag=context.emotion_data.get("emotion", ""),
                user_id=self._user_id,
            )
            injection = self._dispatcher.dispatch_pre_llm_call(hook_ctx)
            if injection and "context" in injection:
                messages[-1]["content"] += f"\n{injection['context']}"

            # LLM 调用
            if hasattr(self._llm, "complete"):
                system_prompt = self._build_system_prompt(context, skill_results)
                summary = await self._llm.complete(
                    messages=messages,
                    system_prompt=system_prompt,
                )
                response = summary.text
                self._input_tokens_last = summary.usage.get("input_tokens", 0)
                self._output_tokens_last = summary.usage.get("output_tokens", 0)
                self._tokens_total += self._input_tokens_last + self._output_tokens_last
            elif hasattr(self._llm, "chat"):
                result = await self._llm.chat(messages)
                response = result if isinstance(result, str) else str(result)
            else:
                response = ""

            # Hook: post_llm_call
            self._dispatcher.dispatch_post_llm_call(hook_ctx, response)

            return response

        except Exception as e:
            logger.error("LLM response generation failed: %s", e, exc_info=True)
            return "抱歉，我遇到了一些问题，请稍后再试。"

    def _build_messages(
        self,
        user_input: str,
        context: SkillContext,
        skill_results: Dict[str, SkillResult],
    ) -> List[Dict[str, Any]]:
        """构建 LLM 消息列表"""
        messages = [{"role": "user", "content": user_input}]

        # 注入 Skill 结果到消息中
        context_parts = []

        if context.emotion_data:
            emotion = context.emotion_data.get("emotion", "neutral")
            intensity = context.emotion_data.get("emotion_intensity", 5.0)
            context_parts.append(f"[情感状态: {emotion}, 强度: {intensity:.1f}]")

        if context.memories:
            mem_texts = [m.get("content", "") for m in context.memories[:3] if m.get("content")]
            if mem_texts:
                context_parts.append(f"[相关记忆: {'; '.join(mem_texts)}]")

        planning_result = skill_results.get("planning_skill")
        if planning_result and planning_result.success and planning_result.output:
            strategy = planning_result.output.get("strategy", "")
            context_parts.append(f"[执行策略: {strategy}]")

        if context_parts:
            messages[-1]["content"] += "\n\n" + "\n".join(context_parts)

        return messages

    def _build_policy_context(
        self, context: SkillContext, skill_name: str
    ) -> Dict[str, Any]:
        """构建策略评估上下文"""
        return {
            "tool": skill_name,
            "args": {},
            "emotion": context.emotion_data,
            "tool_call_count": self._tool_call_count,
        }

    def _build_system_prompt(
        self,
        context: SkillContext,
        skill_results: Dict[str, SkillResult],
    ) -> str:
        """使用 SystemPromptBuilder 构建系统提示"""
        from runtime.prompt_builder import SystemPromptBuilder

        builder = SystemPromptBuilder(
            base_identity="你是一位温暖、耐心的心理陪伴者，名叫'心语'。你的职责是倾听、理解和陪伴。",
            session_id=self._session_id,
        )

        # 注入 Skill 描述
        skill_summaries = []
        for skill in self._skill_registry.list_skills():
            skill_summaries.append({
                "name": skill.get("name", ""),
                "description": skill.get("description", ""),
            })
        builder.set_skill_summaries(skill_summaries)

        return builder.build()

    def _should_skip_skill(self, actions: list) -> bool:
        """根据策略动作判断是否跳过 Skill"""
        from runtime.policy.policy_engine import ActionType

        for action in actions:
            if action.type in (ActionType.DENY, ActionType.ESCALATE_TO_HUMAN):
                return True
        return False
