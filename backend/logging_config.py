#!/usr/bin/env python3
"""
日志配置模块
"""
import os
import logging
import logging.handlers
from pathlib import Path

# 获取项目根目录
project_root = os.getenv('PROJECT_ROOT', str(Path(__file__).parent.parent))
log_dir = Path(project_root) / "log"

# 确保log目录存在
log_dir.mkdir(exist_ok=True)

def setup_logging():
    """设置日志配置"""
    # 创建日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # 清除现有的处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 文件处理器 - 所有日志
    all_log_file = log_dir / "application.log"
    file_handler = logging.handlers.RotatingFileHandler(
        all_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # 错误日志文件处理器
    error_log_file = log_dir / "error.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # 添加处理器到根日志记录器
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)
    
    # 设置第三方库的日志级别
    # 配置Uvicorn日志
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    
    # 过滤掉无效HTTP请求的警告（通常来自扫描器或格式错误的请求）
    class InvalidRequestFilter(logging.Filter):
        """过滤无效HTTP请求的警告"""
        def filter(self, record):
            # 过滤掉"Invalid HTTP request received"警告
            if "Invalid HTTP request received" in str(record.getMessage()):
                return False
            return True
    
    # 应用过滤器到uvicorn.error日志记录器
    invalid_request_filter = InvalidRequestFilter()
    logging.getLogger("uvicorn.error").addFilter(invalid_request_filter)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    
    return root_logger

def get_logger(name: str) -> logging.Logger:
    """获取指定名称的日志记录器"""
    return logging.getLogger(name)

# 初始化日志配置
setup_logging()
