#!/usr/bin/env python3
"""
LLM Harness — 心语后台的「模型网关」层。

设计对齐 Nous Research Hermes Agent 的思路：单一入口解析密钥与 endpoint，
通过修改 LLM_BASE_URL / DEFAULT_MODEL 即可切换智谱、OpenRouter、自建兼容端等，
无需在各业务模块重复读环境变量。参考: https://github.com/nousresearch/hermes-agent
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Optional

from config import Config

from backend.logging_config import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class LLMHarnessSettings:
    """当前解析得到的 LLM 连接参数。"""

    api_key: Optional[str]
    base_url: str
    model: str


def resolve_llm_settings(
    *,
    model: Optional[str] = None,
    prefer_evaluation_model: bool = False,
) -> LLMHarnessSettings:
    """
    从 Config / 环境变量解析 api_key、base_url、默认模型。

    Args:
        model: 显式指定模型时优先生效。
        prefer_evaluation_model: 为 True 且无 model 时，使用 EVALUATION_MODEL，否则 DEFAULT_MODEL。
    """
    api_key = Config.LLM_API_KEY
    base_url = Config.LLM_BASE_URL
    if model is not None:
        resolved_model = model
    elif prefer_evaluation_model:
        resolved_model = os.getenv("EVALUATION_MODEL") or Config.DEFAULT_MODEL
    else:
        resolved_model = Config.DEFAULT_MODEL
    return LLMHarnessSettings(api_key=api_key, base_url=base_url, model=resolved_model)


def try_create_chat_openai(
    *,
    temperature: float = 0.7,
    model: Optional[str] = None,
    prefer_evaluation_model: bool = False,
    **extra: Any,
) -> Optional[Any]:
    """
    创建 langchain_openai.ChatOpenAI；LangChain 不可用、无密钥或构造失败时返回 None。
    """
    settings = resolve_llm_settings(
        model=model, prefer_evaluation_model=prefer_evaluation_model
    )
    if not settings.api_key:
        return None
    try:
        from langchain_openai import ChatOpenAI
    except ImportError:
        return None
    kwargs: dict[str, Any] = {
        "model": settings.model,
        "temperature": temperature,
        "api_key": settings.api_key,
        "base_url": settings.base_url,
    }
    kwargs.update(extra)
    try:
        return ChatOpenAI(**kwargs)
    except Exception as e:
        logger.warning("LLM Harness: ChatOpenAI 初始化失败: %s", e)
        return None


def try_create_openai_sync_client() -> Optional[Any]:
    """
    创建 OpenAI SDK 同步客户端（记忆提取等）；无密钥或失败时返回 None。
    """
    settings = resolve_llm_settings()
    if not settings.api_key:
        return None
    try:
        from openai import OpenAI
    except ImportError:
        return None
    try:
        return OpenAI(api_key=settings.api_key, base_url=settings.base_url)
    except Exception as e:
        logger.warning("LLM Harness: OpenAI 同步客户端初始化失败: %s", e)
        return None
