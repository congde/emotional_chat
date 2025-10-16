#!/usr/bin/env python3
"""
日志中间件
记录HTTP请求和响应
"""

import time
import logging
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """日志中间件"""
    
    def __init__(self, app, log_requests: bool = True, log_responses: bool = True):
        super().__init__(app)
        self.log_requests = log_requests
        self.log_responses = log_responses
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并记录日志"""
        # 生成请求ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 记录请求信息
        if self.log_requests:
            await self._log_request(request, request_id)
        
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 记录响应信息
        if self.log_responses:
            await self._log_response(request, response, process_time, request_id)
        
        return response
    
    async def _log_request(self, request: Request, request_id: str):
        """记录请求信息"""
        # 获取客户端IP
        client_ip = request.client.host if request.client else "unknown"
        
        # 获取用户代理
        user_agent = request.headers.get("user-agent", "unknown")
        
        # 记录请求日志
        logger.info(
            f"请求开始",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": str(request.url.path),
                "query_params": dict(request.query_params),
                "client_ip": client_ip,
                "user_agent": user_agent,
                "content_type": request.headers.get("content-type"),
                "content_length": request.headers.get("content-length")
            }
        )
    
    async def _log_response(
        self,
        request: Request,
        response: Response,
        process_time: float,
        request_id: str
    ):
        """记录响应信息"""
        # 记录响应日志
        logger.info(
            f"请求完成",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": str(request.url.path),
                "status_code": response.status_code,
                "process_time": round(process_time, 4),
                "response_size": response.headers.get("content-length"),
                "content_type": response.headers.get("content-type")
            }
        )
        
        # 记录慢请求警告
        if process_time > 5.0:
            logger.warning(
                f"慢请求检测",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": str(request.url.path),
                    "process_time": round(process_time, 4),
                    "threshold": 5.0
                }
            )
        
        # 记录错误响应
        if response.status_code >= 400:
            logger.error(
                f"错误响应",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": str(request.url.path),
                    "status_code": response.status_code,
                    "process_time": round(process_time, 4)
                }
            )
