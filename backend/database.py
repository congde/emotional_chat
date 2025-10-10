#!/usr/bin/env python3
"""
数据库配置和模型定义
"""
import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:emotional_chat_2025@localhost:3306/emotional_chat")

# 创建数据库引擎
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, index=True)
    username = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class ChatSession(Base):
    """聊天会话表"""
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True)
    user_id = Column(String(100), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class ChatMessage(Base):
    """聊天消息表"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    user_id = Column(String(100), index=True)
    role = Column(String(20))  # user, assistant
    content = Column(Text)
    emotion = Column(String(50))  # 情感标签
    emotion_intensity = Column(Float)  # 情感强度
    created_at = Column(DateTime, default=datetime.utcnow)

class EmotionAnalysis(Base):
    """情感分析记录表"""
    __tablename__ = "emotion_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    user_id = Column(String(100), index=True)
    message_id = Column(Integer)  # 关联到chat_messages.id
    emotion = Column(String(50))
    intensity = Column(Float)
    keywords = Column(Text)  # JSON格式存储关键词
    suggestions = Column(Text)  # JSON格式存储建议
    created_at = Column(DateTime, default=datetime.utcnow)

class Knowledge(Base):
    """知识库表"""
    __tablename__ = "knowledge"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    content = Column(Text)
    category = Column(String(100))
    tags = Column(Text)  # JSON格式存储标签
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class SystemLog(Base):
    """系统日志表"""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(20))  # INFO, WARNING, ERROR
    message = Column(Text)
    session_id = Column(String(100), index=True)
    user_id = Column(String(100), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# 创建所有表
def create_tables():
    """创建数据库表"""
    Base.metadata.create_all(bind=engine)

# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 数据库操作类
class DatabaseManager:
    def __init__(self):
        self.db = SessionLocal()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()
    
    def save_message(self, session_id, user_id, role, content, emotion=None, emotion_intensity=None):
        """保存聊天消息"""
        message = ChatMessage(
            session_id=session_id,
            user_id=user_id,
            role=role,
            content=content,
            emotion=emotion,
            emotion_intensity=emotion_intensity
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def get_session_messages(self, session_id, limit=50):
        """获取会话消息"""
        return self.db.query(ChatMessage)\
            .filter(ChatMessage.session_id == session_id)\
            .order_by(ChatMessage.created_at.desc())\
            .limit(limit)\
            .all()
    
    def save_emotion_analysis(self, session_id, user_id, message_id, emotion, intensity, keywords, suggestions):
        """保存情感分析结果"""
        analysis = EmotionAnalysis(
            session_id=session_id,
            user_id=user_id,
            message_id=message_id,
            emotion=emotion,
            intensity=intensity,
            keywords=str(keywords),
            suggestions=str(suggestions)
        )
        self.db.add(analysis)
        self.db.commit()
        return analysis
    
    def get_user_emotion_history(self, user_id, limit=100):
        """获取用户情感历史"""
        return self.db.query(EmotionAnalysis)\
            .filter(EmotionAnalysis.user_id == user_id)\
            .order_by(EmotionAnalysis.created_at.desc())\
            .limit(limit)\
            .all()
    
    def save_knowledge(self, title, content, category, tags=None):
        """保存知识"""
        knowledge = Knowledge(
            title=title,
            content=content,
            category=category,
            tags=str(tags) if tags else None
        )
        self.db.add(knowledge)
        self.db.commit()
        return knowledge
    
    def search_knowledge(self, query, category=None, limit=10):
        """搜索知识"""
        q = self.db.query(Knowledge).filter(Knowledge.is_active == True)
        if category:
            q = q.filter(Knowledge.category == category)
        # 简单的文本搜索，可以后续优化为全文搜索
        q = q.filter(Knowledge.content.contains(query))
        return q.limit(limit).all()
    
    def log_system_event(self, level, message, session_id=None, user_id=None):
        """记录系统日志"""
        log = SystemLog(
            level=level,
            message=message,
            session_id=session_id,
            user_id=user_id
        )
        self.db.add(log)
        self.db.commit()
        return log
