-- 增强版多轮对话系统 - 数据库迁移脚本
-- 为现有表添加新字段，支持记忆衰减、访问统计等功能

-- 1. 更新 memory_items 表 - 添加访问统计字段（如果不存在）
ALTER TABLE memory_items 
ADD COLUMN IF NOT EXISTS access_count INT DEFAULT 0 COMMENT '访问次数';

ALTER TABLE memory_items 
ADD COLUMN IF NOT EXISTS last_accessed DATETIME COMMENT '最后访问时间';

ALTER TABLE memory_items 
ADD COLUMN IF NOT EXISTS decay_rate FLOAT DEFAULT 0.9 COMMENT '衰减率';

-- 2. 更新 user_profiles 表 - 扩展字段（如果不存在）
ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS last_interaction_date DATETIME COMMENT '最后互动日期';

ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS emotion_history TEXT COMMENT '情绪历史记录（JSON）';

-- 3. 创建对话图谱表（如果不存在）
CREATE TABLE IF NOT EXISTS conversation_graphs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    graph_data TEXT COMMENT '图谱数据（JSON格式）',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='对话脉络图谱表';

-- 4. 创建主动回忆触发记录表（如果不存在）
CREATE TABLE IF NOT EXISTS proactive_recalls (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    recall_type VARCHAR(50) NOT NULL COMMENT '回忆类型：unfollow_memory, emotion_check, long_absence',
    memory_id VARCHAR(100) COMMENT '关联的记忆ID',
    triggered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_response TEXT COMMENT '用户响应',
    was_helpful BOOLEAN COMMENT '是否有帮助',
    INDEX idx_user_id (user_id),
    INDEX idx_triggered_at (triggered_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='主动回忆触发记录表';

-- 5. 创建记忆重要性更新日志表（如果不存在）
CREATE TABLE IF NOT EXISTS memory_importance_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    memory_id VARCHAR(100) NOT NULL,
    old_importance FLOAT,
    new_importance FLOAT,
    reason VARCHAR(200) COMMENT '更新原因',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_memory_id (memory_id),
    INDEX idx_updated_at (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='记忆重要性更新日志';

-- 6. 为 chat_messages 表添加索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_user_created ON chat_messages(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_session_created ON chat_messages(session_id, created_at);

-- 7. 为 memory_items 表添加复合索引
CREATE INDEX IF NOT EXISTS idx_user_importance ON memory_items(user_id, importance);
CREATE INDEX IF NOT EXISTS idx_user_active ON memory_items(user_id, is_active);
CREATE INDEX IF NOT EXISTS idx_user_accessed ON memory_items(user_id, last_accessed);

COMMIT;

