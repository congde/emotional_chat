import os

class Config:
    # OpenAI配置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # 向量数据库配置
    CHROMA_PERSIST_DIRECTORY = "./chroma_db"
