#!/usr/bin/env python3
"""
错误处理中间件
统一处理应用程序错误
"""

import logging
import traceback
from typing import Callable, Dict, Any
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..core.exceptions import EXCEPTION_HANDLERS, EmotionalChatException
from ..core.utils.formatters import format_error

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """错误处理中间件"""
    
    def __init__(self, app, debug: bool = False):
        super().__init__(app)
        self.debug = debug
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并捕获错误"""
        try:
            response = await call_next(request)
            return response
        
        except EmotionalChatException as e:
            # 处理自定义异常
            logger.error(f"自定义异常: {e.error_code} - {e.message}", extra={
                "error_code": e.error_code,
                "details": e.details,
                "path": str(request.url),
                "method": request.method
            })
            
            # 查找对应的处理器
            handler = EXCEPTION_HANDLERS.get(type(e))
            if handler:
                status_code, error_data = handler(e)
            else:
                status_code, error_data = 500, {"error": "系统错误", "details": str(e)}
            
            return JSONResponse(
                status_code=status_code,
                content=format_error(
                    error=e,
                    error_code=e.error_code,
                    status_code=status_code,
                    details=e.details
                )
            )
        
        except HTTPException as e:
            # 处理FastAPI HTTP异常
            logger.warning(f"HTTP异常: {e.status_code} - {e.detail}", extra={
                "status_code": e.status_code,
                "path": str(request.url),
                "method": request.method
            })
            
            return JSONResponse(
                status_code=e.status_code,
                content=format_error(
                    error=e.detail,
                    error_code="HTTP_EXCEPTION",
                    status_code=e.status_code
                )
            )
        
        except Exception as e:
            # 处理未预期的异常
            logger.error(f"未预期异常: {type(e).__name__} - {str(e)}", extra={
                "exception_type": type(e).__name__,
                "path": str(request.url),
                "method": request.method,
                "traceback": traceback.format_exc()
            })
            
            error_message = str(e) if self.debug else "服务器内部错误"
            
            return JSONResponse(
                status_code=500,
                content=format_error(
                    error=error_message,
                    error_code="INTERNAL_SERVER_ERROR",
                    status_code=500,
                    details={"debug": self.debug}
                )
            )
