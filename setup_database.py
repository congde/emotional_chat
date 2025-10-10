#!/usr/bin/env python3
"""
数据库初始化脚本
"""
import os
import sys
import pymysql
from pymysql import Error

# 数据库配置
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'password'),
    'database': os.getenv('MYSQL_DATABASE', 'emotional_chat')
}

def create_database():
    """创建数据库"""
    try:
        # 连接MySQL服务器（不指定数据库）
        connection = pymysql.connect(
            host=MYSQL_CONFIG['host'],
            port=MYSQL_CONFIG['port'],
            user=MYSQL_CONFIG['user'],
            password=MYSQL_CONFIG['password']
        )
        
        cursor = connection.cursor()
        
        # 创建数据库
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✅ 数据库 {MYSQL_CONFIG['database']} 创建成功")
        
        # 使用数据库
        cursor.execute(f"USE {MYSQL_CONFIG['database']}")
        
        # 创建表的SQL语句
        create_tables_sql = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(100) UNIQUE NOT NULL,
                username VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                INDEX idx_user_id (user_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """,
            """
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(100) UNIQUE NOT NULL,
                user_id VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                INDEX idx_session_id (session_id),
                INDEX idx_user_id (user_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """,
            """
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(100) NOT NULL,
                user_id VARCHAR(100) NOT NULL,
                role VARCHAR(20) NOT NULL,
                content TEXT NOT NULL,
                emotion VARCHAR(50),
                emotion_intensity FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_session_id (session_id),
                INDEX idx_user_id (user_id),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """,
            """
            CREATE TABLE IF NOT EXISTS emotion_analysis (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(100) NOT NULL,
                user_id VARCHAR(100) NOT NULL,
                message_id INT NOT NULL,
                emotion VARCHAR(50) NOT NULL,
                intensity FLOAT NOT NULL,
                keywords TEXT,
                suggestions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_session_id (session_id),
                INDEX idx_user_id (user_id),
                INDEX idx_message_id (message_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """,
            """
            CREATE TABLE IF NOT EXISTS knowledge (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                content TEXT NOT NULL,
                category VARCHAR(100),
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                INDEX idx_category (category),
                INDEX idx_is_active (is_active)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """,
            """
            CREATE TABLE IF NOT EXISTS system_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                level VARCHAR(20) NOT NULL,
                message TEXT NOT NULL,
                session_id VARCHAR(100),
                user_id VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_level (level),
                INDEX idx_session_id (session_id),
                INDEX idx_user_id (user_id),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
        ]
        
        # 执行创建表的SQL
        for sql in create_tables_sql:
            cursor.execute(sql)
        
        print("✅ 所有表创建成功")
        
        # 插入示例数据
        insert_sample_data(cursor)
        
        cursor.close()
        connection.close()
        
        print("🎉 数据库初始化完成！")
        
    except Error as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False
    
    return True

def insert_sample_data(cursor):
    """插入示例数据"""
    try:
        # 插入示例知识
        sample_knowledge = [
            ("情感支持技巧", "当用户表达负面情绪时，要表现出理解和共情，避免说教。", "心理健康", '["情感支持", "共情", "倾听"]'),
            ("安全词汇过滤", "检测并处理高风险词汇，引导用户寻求专业帮助。", "安全", '["安全", "风险", "过滤"]'),
            ("对话记忆管理", "利用向量数据库存储和检索用户的历史对话，提供个性化回应。", "技术", '["记忆", "向量", "个性化"]')
        ]
        
        for title, content, category, tags in sample_knowledge:
            cursor.execute("""
                INSERT IGNORE INTO knowledge (title, content, category, tags) 
                VALUES (%s, %s, %s, %s)
            """, (title, content, category, tags))
        
        print("✅ 示例数据插入成功")
        
    except Error as e:
        print(f"⚠️ 插入示例数据失败: {e}")

def test_connection():
    """测试数据库连接"""
    try:
        connection = pymysql.connect(**MYSQL_CONFIG)
        if connection.open:
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE()")
            database = cursor.fetchone()
            print(f"✅ 数据库连接成功: {database[0]}")
            
            # 测试表是否存在
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"📊 数据库表: {[table[0] for table in tables]}")
            
            cursor.close()
            connection.close()
            return True
            
    except Error as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始初始化情感聊天机器人数据库...")
    print("=" * 50)
    
    # 显示配置信息
    print("📋 数据库配置:")
    for key, value in MYSQL_CONFIG.items():
        if key == 'password':
            print(f"   {key}: {'*' * len(str(value))}")
        else:
            print(f"   {key}: {value}")
    print()
    
    # 创建数据库和表
    if create_database():
        print("\n🔍 测试数据库连接...")
        test_connection()
        
        print("\n📝 后续步骤:")
        print("1. 启动后端服务: python3 run_backend.py")
        print("2. 访问API文档: http://localhost:8008/docs")
        print("3. 启动前端服务: cd frontend && npm start")
    else:
        print("\n❌ 数据库初始化失败，请检查配置")

if __name__ == "__main__":
    main()
