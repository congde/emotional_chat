-- 个性化配置表迁移脚本
-- 创建时间: 2025-01-20
-- 版本: v1.0

-- 创建用户个性化配置表
CREATE TABLE IF NOT EXISTS user_personalizations (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    user_id VARCHAR(100) UNIQUE NOT NULL COMMENT '用户ID',
    
    -- 角色层：AI身份与人格
    role VARCHAR(100) DEFAULT '温暖倾听者' COMMENT '角色类型',
    role_name VARCHAR(100) DEFAULT '心语' COMMENT '角色名称',
    role_background TEXT COMMENT '角色背景故事',
    personality VARCHAR(100) DEFAULT '温暖耐心' COMMENT '性格特征',
    core_principles TEXT COMMENT '核心原则(JSON数组)',
    forbidden_behaviors TEXT COMMENT '禁忌行为(JSON数组)',
    
    -- 表达层：风格与语气
    tone VARCHAR(50) DEFAULT '温和' COMMENT '语气',
    style VARCHAR(50) DEFAULT '简洁' COMMENT '风格',
    formality FLOAT DEFAULT 0.3 COMMENT '正式程度(0-1)',
    enthusiasm FLOAT DEFAULT 0.5 COMMENT '活泼度(0-1)',
    empathy_level FLOAT DEFAULT 0.8 COMMENT '共情程度(0-1)',
    humor_level FLOAT DEFAULT 0.3 COMMENT '幽默程度(0-1)',
    response_length VARCHAR(20) DEFAULT 'medium' COMMENT '回复长度',
    use_emoji BOOLEAN DEFAULT FALSE COMMENT '是否使用emoji',
    
    -- 记忆层：长期偏好
    preferred_topics TEXT COMMENT '偏好话题(JSON数组)',
    avoided_topics TEXT COMMENT '避免话题(JSON数组)',
    communication_preferences TEXT COMMENT '沟通偏好(JSON对象)',
    
    -- 高级设置
    learning_mode BOOLEAN DEFAULT TRUE COMMENT '是否启用学习模式',
    safety_level VARCHAR(20) DEFAULT 'standard' COMMENT '安全级别',
    context_window INT DEFAULT 10 COMMENT '上下文窗口大小',
    
    -- 情境化角色
    situational_roles TEXT COMMENT '情境角色配置(JSON对象)',
    active_role VARCHAR(50) DEFAULT 'default' COMMENT '当前激活的角色',
    
    -- 统计信息
    total_interactions INT DEFAULT 0 COMMENT '总交互次数',
    positive_feedbacks INT DEFAULT 0 COMMENT '正向反馈次数',
    config_version INT DEFAULT 1 COMMENT '配置版本号',
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 索引
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    INDEX idx_updated_at (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户个性化配置表';

-- 插入默认配置示例（可选）
-- INSERT INTO user_personalizations (user_id, role, role_name) 
-- VALUES ('demo_user', '温暖倾听者', '心语');

-- 查询验证
SELECT COUNT(*) as table_exists 
FROM information_schema.tables 
WHERE table_schema = DATABASE() 
AND table_name = 'user_personalizations';

-- 显示表结构
DESCRIBE user_personalizations;












