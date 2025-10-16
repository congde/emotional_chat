#!/usr/bin/env python3
"""
配置管理模块
统一管理系统配置和环境变量
"""

import os
from typing import Optional, Dict, Any
from functools import lru_cache
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

from dotenv import load_dotenv


class Environment(Enum):
    """环境类型枚举"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class DatabaseConfig:
    """数据库配置"""
    host: str = "localhost"
    port: int = 3306
    username: str = "root"
    password: str = ""
    database: str = "emotional_chat"
    charset: str = "utf8mb4"
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    @property
    def url(self) -> str:
        """数据库连接URL"""
        return (
            f"mysql+pymysql://{self.username}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
            f"?charset={self.charset}"
        )


@dataclass
class RedisConfig:
    """Redis配置"""
    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None
    db: int = 0
    max_connections: int = 10
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    
    @property
    def url(self) -> str:
        """Redis连接URL"""
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"


@dataclass
class OpenAIConfig:
    """OpenAI配置"""
    api_key: str = ""
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 30
    max_retries: int = 3


@dataclass
class VectorDBConfig:
    """向量数据库配置"""
    persist_directory: str = "./chroma_db"
    collection_name: str = "emotional_memories"
    chunk_size: int = 500
    chunk_overlap: int = 50
    embedding_model: str = "text-embedding-ada-002"


@dataclass
class RAGConfig:
    """RAG知识库配置"""
    enabled: bool = True
    knowledge_base_path: str = "./chroma_db/psychology_kb"
    search_k: int = 3
    max_context_length: int = 4000
    similarity_threshold: float = 0.7


@dataclass
class LoggingConfig:
    """日志配置"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str = "./logs/emotional_chat.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_console: bool = True
    enable_file: bool = True


@dataclass
class SecurityConfig:
    """安全配置"""
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    cors_origins: list = field(default_factory=lambda: ["*"])
    rate_limit_enabled: bool = True
    max_requests_per_minute: int = 60


@dataclass
class APIConfig:
    """API配置"""
    title: str = "心语情感陪伴机器人 API"
    description: str = "基于LangChain和记忆系统的情感支持聊天机器人"
    version: str = "3.0.0"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    reload: bool = False


@dataclass
class Config:
    """主配置类"""
    # 环境配置
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = True
    
    # 子配置
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    openai: OpenAIConfig = field(default_factory=OpenAIConfig)
    vector_db: VectorDBConfig = field(default_factory=VectorDBConfig)
    rag: RAGConfig = field(default_factory=RAGConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    api: APIConfig = field(default_factory=APIConfig)
    
    def __post_init__(self):
        """初始化后处理"""
        self._load_from_env()
        self._validate_config()
        self._setup_directories()
    
    def _load_from_env(self):
        """从环境变量加载配置"""
        # 基础环境
        self.environment = Environment(
            os.getenv("ENVIRONMENT", self.environment.value)
        )
        self.debug = os.getenv("DEBUG", str(self.debug)).lower() == "true"
        
        # 数据库配置
        self.database.host = os.getenv("DB_HOST", self.database.host)
        self.database.port = int(os.getenv("DB_PORT", self.database.port))
        self.database.username = os.getenv("DB_USERNAME", self.database.username)
        self.database.password = os.getenv("DB_PASSWORD", self.database.password)
        self.database.database = os.getenv("DB_DATABASE", self.database.database)
        
        # Redis配置
        self.redis.host = os.getenv("REDIS_HOST", self.redis.host)
        self.redis.port = int(os.getenv("REDIS_PORT", self.redis.port))
        self.redis.password = os.getenv("REDIS_PASSWORD", self.redis.password)
        
        # OpenAI配置
        self.openai.api_key = os.getenv("OPENAI_API_KEY", self.openai.api_key)
        self.openai.model = os.getenv("OPENAI_MODEL", self.openai.model)
        self.openai.base_url = os.getenv("OPENAI_BASE_URL", self.openai.base_url)
        
        # API配置
        self.api.host = os.getenv("API_HOST", self.api.host)
        self.api.port = int(os.getenv("API_PORT", self.api.port))
        self.api.workers = int(os.getenv("API_WORKERS", self.api.workers))
        
        # 安全配置
        self.security.secret_key = os.getenv("SECRET_KEY", self.security.secret_key)
        
        # 日志配置
        self.logging.level = os.getenv("LOG_LEVEL", self.logging.level)
        self.logging.file_path = os.getenv("LOG_FILE_PATH", self.logging.file_path)
        
        # RAG配置
        self.rag.enabled = os.getenv("RAG_ENABLED", str(self.rag.enabled)).lower() == "true"
        self.rag.knowledge_base_path = os.getenv("RAG_KNOWLEDGE_BASE_PATH", self.rag.knowledge_base_path)
    
    def _validate_config(self):
        """验证配置"""
        if not self.openai.api_key:
            raise ValueError("OpenAI API key is required")
        
        if self.database.password is None:
            print("Warning: Database password is not set")
        
        if self.security.secret_key == "your-secret-key-here":
            print("Warning: Using default secret key, change it in production")
    
    def _setup_directories(self):
        """创建必要的目录"""
        directories = [
            Path(self.logging.file_path).parent,
            Path(self.vector_db.persist_directory),
            Path(self.rag.knowledge_base_path),
            Path("uploads"),
            Path("logs")
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "environment": self.environment.value,
            "debug": self.debug,
            "database": {
                "host": self.database.host,
                "port": self.database.port,
                "database": self.database.database
            },
            "openai": {
                "model": self.openai.model,
                "base_url": self.openai.base_url
            },
            "rag": {
                "enabled": self.rag.enabled,
                "knowledge_base_path": self.rag.knowledge_base_path
            },
            "api": {
                "host": self.api.host,
                "port": self.api.port,
                "title": self.api.title,
                "version": self.api.version
            }
        }
    
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.environment == Environment.DEVELOPMENT
    
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.environment == Environment.PRODUCTION
    
    def is_testing(self) -> bool:
        """是否为测试环境"""
        return self.environment == Environment.TESTING


@lru_cache()
def get_config() -> Config:
    """获取配置实例（单例模式）"""
    # 加载环境变量
    env_file = Path(".env")
    if env_file.exists():
        load_dotenv(env_file)
    
    # 尝试加载项目特定的环境文件
    config_file = Path("config.env")
    if config_file.exists():
        load_dotenv(config_file)
    
    return Config()


def reload_config() -> Config:
    """重新加载配置"""
    get_config.cache_clear()
    return get_config()
