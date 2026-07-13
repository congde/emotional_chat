"""
Hermes 风格工作区自动化 HTTP 接口（与 Agent 内 hermes_dispatch 能力一致）。
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.hermes.dispatch import run_hermes_dispatch
from backend.hermes.settings import get_hermes_settings, hermes_ready

router = APIRouter(prefix="/hermes", tags=["hermes"])


class HermesDispatchBody(BaseModel):
    instruction: str = Field(..., min_length=1, description="自然语言指令")
    user_id: Optional[str] = Field(None, description="可选，用于审计日志占位")


@router.get("/status")
async def hermes_status() -> Dict[str, Any]:
    s = get_hermes_settings()
    return {
        "tools_enabled": s.tools_enabled,
        "workspace_configured": bool(s.workspace_root),
        "workspace_ready": hermes_ready(),
        "web_fetch_enabled": s.web_fetch_enabled,
        "shell_enabled": s.shell_enabled,
        "shell_timeout_sec": s.shell_timeout_sec,
        "figma_token_set": bool(s.figma_token),
        "reference": "https://github.com/nousresearch/hermes-agent",
    }


@router.post("/dispatch")
async def hermes_dispatch_http(body: HermesDispatchBody) -> Dict[str, Any]:
    """直接执行 hermes_dispatch（不经过 Agent 规划器）。"""
    result = run_hermes_dispatch(body.instruction)
    return {"code": 200, "ok": result.get("ok", False), "data": result}
