# 情感聊天机器人 🤖💝

一个基于 **阿里云通义千问(Qwen)** + MySQL + 向量数据库的智能情感支持聊天机器人，具有情感识别、共情回应、长期记忆和数据分析能力。

> **参考项目**: [emotional_chat](https://github.com/congde/emotional_chat.git)

> **🆕 更新说明**: 本项目已从 OpenAI GPT 迁移至阿里云通义千问(Qwen)，提供更好的中文支持和更稳定的服务。

## ✨ 功能特点

- 🎭 **情感识别**: 智能分析用户情感状态（开心、难过、焦虑、愤怒等）
- 💝 **共情回应**: 根据情感状态生成温暖、理解的回应力
- 🧠 **长期记忆**: ✅ 已集成 Chroma 向量数据库，支持跨会话语义检索
- 🗄️ **数据持久化**: MySQL数据库存储所有聊天记录和用户数据
- 📊 **情感趋势分析**: 分析用户情感变化趋势和模式
- 🔒 **安全过滤**: 自动检测高风险词汇并提供专业求助信息
- 🔄 **上下文理解**: 基于对话历史提供连贯的回应
- 🎨 **美观界面**: 现代化的React前端界面
- 🚀 **高性能**: 基于FastAPI + LangChain的高性能后端服务
- 🇨🇳 **中文优化**: 使用通义千问模型，对中文理解和表达更加自然

### 🌟 通义千问模型优势

- **卓越的中文能力**: 针对中文场景深度优化，理解和表达更自然
- **情感共情出色**: 在心理健康场景表现优异，回复温暖细腻
- **稳定可靠**: 阿里云基础设施保障，服务稳定性高
- **成本优化**: 相比国外模型，性价比更高

### 🧠 向量数据库长期记忆（新功能）

**状态**: ✅ 已完成集成

**特性**:
- 🔍 **语义检索**: 基于语义相似度检索历史对话
- 🌐 **跨会话记忆**: 不限于当前会话，可访问所有历史对话
- 📚 **知识库管理**: 支持存储和检索心理健康知识
- 😊 **情感模式学习**: 学习用户的情感表达模式

**工作原理**:
```
短期记忆 (MySQL)    +    长期记忆 (Chroma向量数据库)
最近5条对话              跨会话语义相似对话
      ↓                        ↓
            上下文融合
                 ↓
          智能回复生成
```

**安装向量数据库** (可选，但推荐):
```bash
# 安装依赖 (需要 Python 3.8+)
pip3 install --user chromadb sentence-transformers

# 查看详细指南
cat VECTOR_DB_GUIDE.md
```

**注意**: 向量数据库是可选功能，不安装也不影响基本聊天功能，系统会自动降级为仅使用 MySQL 短期记忆。

## 🏗️ 系统架构

### 总体架构图

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React前端     │    │   FastAPI后端   │    │   MySQL数据库   │
│   (端口3000)    │◄──►│   (端口8000)    │◄──►│   (端口3306)    │
│                 │    │                 │    │                 │
│ • 聊天界面      │    │ • 情感分析      │    │ • 用户数据      │
│ • 实时交互      │    │ • 通义千问API   │    │ • 对话历史      │
│ • 响应式设计    │    │ • 会话管理      │    │ • 情感记录      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 详细架构

```
┌─────────────────────────────────────────┐
│              访问层 (Access Layer)        │
│        用户界面 (Web/App/小程序)          │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│           对话管理层                     │
│   会话状态管理、上下文维护                │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│           核心引擎层                     │
│   大模型API+提示工程+Agent逻辑            │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│        知识与记忆层                      │
│  向量数据库(长期记忆)、规则库(安全过滤)    │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│        数据与服务层                      │
│  用户数据、日志、第三方服务(TTS/语音)     │
└─────────────────────────────────────────┘
```

## 🗄️ 数据库设计

### MySQL数据库表结构

#### 1. users - 用户表
```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id VARCHAR(100) UNIQUE NOT NULL,
    username VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

#### 2. chat_sessions - 会话表
```sql
CREATE TABLE chat_sessions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

#### 3. chat_messages - 消息表
```sql
CREATE TABLE chat_messages (
    id INT PRIMARY KEY AUTO_INCREMENT,
    session_id VARCHAR(100) NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL,  -- user, assistant
    content TEXT NOT NULL,
    emotion VARCHAR(50),
    emotion_intensity FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4. emotion_analysis - 情感分析表
```sql
CREATE TABLE emotion_analysis (
    id INT PRIMARY KEY AUTO_INCREMENT,
    session_id VARCHAR(100) NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    message_id INT NOT NULL,
    emotion VARCHAR(50) NOT NULL,
    intensity FLOAT NOT NULL,
    keywords TEXT,
    suggestions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 5. knowledge - 知识库表
```sql
CREATE TABLE knowledge (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100),
    tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

#### 6. system_logs - 系统日志表
```sql
CREATE TABLE system_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    session_id VARCHAR(100),
    user_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🛠️ 技术栈

### 后端
- **Python 3.8+**
- **阿里云通义千问 (Qwen)**: 大语言模型 (qwen-plus)
- **LangChain**: 对话流管理和记忆管理  
- **MySQL**: 关系型数据库存储
- **Chroma**: 向量数据库（长期记忆）
- **FastAPI**: Web框架
- **SQLAlchemy**: ORM框架
- **Sentence Transformers**: 文本嵌入

### 前端
- **React 18**
- **Styled Components**: CSS-in-JS
- **Framer Motion**: 动画效果
- **Axios**: HTTP客户端

## 🚀 快速开始

### 1. 环境准备

#### 1.1 安装依赖
```bash
# 进入项目目录
cd /home/emotional_chat

# 安装Python依赖
pip3 install --user -r requirements.txt

# 安装前端依赖
cd frontend
npm install
cd ..
```

#### 1.2 配置环境变量
```bash
# 复制环境变量模板
cp env_example.txt .env

# 编辑配置文件
nano .env
```

配置内容：
```bash
# API配置 - 使用阿里云通义千问(Qwen)
DASHSCOPE_API_KEY=your_qwen_api_key_here
API_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# MySQL数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=emotional_chat

# 模型配置 - 使用通义千问
DEFAULT_MODEL=qwen-plus
TEMPERATURE=0.7
MAX_TOKENS=1000

# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

**获取通义千问 API Key**：
1. 访问阿里云 DashScope 平台：https://dashscope.console.aliyun.com/
2. 登录阿里云账号
3. 创建 API Key
4. 将 API Key 填入 `config.env` 文件

#### 1.3 安装和配置MySQL
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server mysql-client

# CentOS/RHEL
sudo yum install mysql-server mysql

# 启动MySQL服务
sudo systemctl start mysql
sudo systemctl enable mysql

# 配置MySQL（可选）
sudo mysql_secure_installation
```

### 2. 初始化数据库

```bash
# 初始化MySQL数据库和表结构
python3 setup_database.py
```

### 3. 启动服务

#### 3.1 启动后端服务
```bash
# 方法1：使用启动脚本（推荐，避免文件监视限制问题）
python3 run_backend.py

# 方法2：直接在backend目录启动
cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

> **注意**：启动脚本会自动切换到 backend 目录运行，避免 watchfiles 扫描 frontend/node_modules 导致的文件监视限制问题。

后端服务将在 `http://localhost:8000` 启动，API文档可在 `http://localhost:8000/docs` 查看。

#### 3.2 启动前端服务
```bash
# 新开一个终端窗口
cd /home/emotional_chat/frontend

# 启动前端服务（端口3000）
npm start
```

前端应用将在 `http://localhost:3000` 启动。


### 4. 验证服务

**检查后端服务**
```bash
# 健康检查
curl http://localhost:8000/health

# 测试聊天接口
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好，我今天心情很好！", "user_id": "test_user"}'
```

**检查前端服务**
- 打开浏览器访问 `http://localhost:3000`
- 应该能看到聊天界面

### 5. 使用说明

1. 打开浏览器访问 `http://localhost:3000`
2. 在输入框中输入你的想法和感受
3. 机器人会分析你的情感并给出共情回应
4. 支持多轮对话，机器人会记住对话历史
5. 查看API文档：http://localhost:8000/docs

### 6. 故障排除

**后端启动失败**
```bash
# 检查Python版本
python3 --version

# 检查依赖安装
pip3 list | grep fastapi

# 手动安装依赖
pip3 install --user -r requirements.txt

# 检查MySQL连接
python3 setup_database.py
```

**前端启动失败**
```bash
# 检查Node.js版本
node --version
npm --version

# 清理并重新安装依赖
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**端口冲突**
```bash
# 检查端口占用
netstat -tulpn | grep :8000
netstat -tulpn | grep :3000

# 杀死占用端口的进程
sudo kill -9 <PID>
```

## 🎯 快速启动总结

如果您已经安装了依赖，可以直接使用以下命令启动：

**终端1 - 启动后端：**
```bash
# 在项目根目录运行（推荐）
python3 run_backend.py

# 或者进入backend目录运行
cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**终端2 - 启动前端：**
```bash
cd /home/emotional_chat/frontend
npm start
```

**访问地址：**
- 前端界面：http://localhost:3000
- 后端API：http://localhost:8000

**测试系统：**
```bash
# 测试后端健康状态
curl http://localhost:8000/health

# 测试聊天功能
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好", "user_id": "test_user"}'
```

## 📁 项目结构

```
emotional_chat/
├── backend/                          # 后端代码目录
│   ├── __init__.py                  # 包初始化文件
│   ├── main.py                      # FastAPI主应用（当前使用）
│   ├── database.py                  # 数据库模型和操作（SQLAlchemy + MySQL）
│   ├── models.py                    # Pydantic数据模型
│   ├── simple_langchain_engine.py   # ✅ 主聊天引擎（Qwen API + 情感分析）
│   ├── emotion_analyzer.py          # 情感分析器
│   └── vector_store.py              # 向量数据库操作
│
├── frontend/                         # 前端代码目录
│   ├── public/                      # 静态资源
│   │   └── index.html               # HTML模板
│   ├── src/                         # 源代码
│   │   ├── App.js                   # 主应用组件
│   │   ├── index.js                 # 入口文件
│   │   ├── index.css                # 全局样式
│   │   └── services/                # 服务层
│   │       └── ChatAPI.js           # API调用封装
│   ├── package.json                 # 项目配置和依赖
│   └── package-lock.json            # 依赖锁定文件
│
├── config.py                         # 配置文件（包含端口等配置）
├── config.env                        # 环境变量配置（Qwen API Key等）
├── env_example.txt                   # 环境变量模板（参考）
├── setup_database.py                 # 数据库初始化脚本
├── run_backend.py                    # 后端启动脚本（主入口）
├── start.sh                          # 一键启动脚本
├── requirements.txt                  # Python依赖列表
├── LICENSE                           # 开源许可证
└── README.md                         # 项目文档（本文件）
```

### 文件说明

#### 🔥 核心文件（当前使用）

| 文件 | 用途 | 说明 |
|------|------|------|
| `backend/main.py` | 后端主程序 | FastAPI应用入口 |
| `backend/simple_langchain_engine.py` | 聊天引擎 | 核心业务逻辑 |
| `backend/database.py` | 数据库层 | MySQL操作封装 |
| `frontend/src/App.js` | 前端主组件 | React应用入口 |
| `setup_database.py` | 数据库初始化 | 创建表结构 |
| `run_backend.py` | 启动脚本 | 启动后端服务 |

#### 📚 辅助文件

| 文件 | 说明 |
|------|------|
| `backend/emotion_analyzer.py` | 独立情感分析模块 |
| `backend/vector_store.py` | 向量数据库操作封装 |

#### ⚙️ 配置文件

| 文件 | 说明 |
|------|------|
| `config.py` | Python配置（端口、主机等） |
| `config.env` | 环境变量（通义千问API密钥、MySQL配置） |
| `env_example.txt` | 环境变量模板 |

## 📡 API接口文档

### 1. 健康检查
```bash
GET /health
```
**响应示例:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-10T16:56:41.721768",
  "version": "2.0.0",
  "database": "connected",
  "vector_db": "ready"
}
```

### 2. 聊天接口
```bash
POST /chat
Content-Type: application/json

{
  "message": "你好，我今天心情很好！",
  "user_id": "test_user",
  "session_id": "optional-session-id"
}
```
**响应示例:**
```json
{
  "response": "你好，听到你今天心情很好，真是太棒了！😊",
  "session_id": "0ccdde5c-8592-4e23-893a-8e1a8d8bbaf7",
  "emotion": "happy",
  "suggestions": [
    "很高兴看到你这么开心！",
    "有什么特别的事情想要分享吗？"
  ],
  "timestamp": "2025-10-10T16:57:50.584646"
}
```

### 3. 获取会话历史
```bash
GET /sessions/{session_id}/history?limit=20
```
**响应示例:**
```json
{
  "session_id": "0ccdde5c-8592-4e23-893a-8e1a8d8bbaf7",
  "messages": [
    {
      "role": "user",
      "content": "你好，我今天心情很好！",
      "emotion": "happy",
      "emotion_intensity": 8,
      "timestamp": "2025-10-10T16:57:50.000000"
    },
    {
      "role": "assistant",
      "content": "你好，听到你今天心情很好，真是太棒了！😊",
      "emotion": "empathetic",
      "timestamp": "2025-10-10T16:57:52.000000"
    }
  ]
}
```

### 4. 获取会话摘要
```bash
GET /sessions/{session_id}/summary
```
**响应示例:**
```json
{
  "session_id": "0ccdde5c-8592-4e23-893a-8e1a8d8bbaf7",
  "message_count": 10,
  "emotion_distribution": {
    "happy": 5,
    "neutral": 3,
    "anxious": 2
  },
  "created_at": "2025-10-10T16:57:50.000000",
  "updated_at": "2025-10-10T17:05:20.000000"
}
```

### 5. 获取用户情感趋势
```bash
GET /users/{user_id}/emotion-trends
```
**响应示例:**
```json
{
  "user_id": "test_user",
  "total_records": 50,
  "recent_emotions": ["happy", "neutral", "anxious"],
  "average_intensity": 6.5,
  "emotion_counts": {
    "happy": 20,
    "neutral": 15,
    "anxious": 10,
    "sad": 5
  }
}
```

### 完整API文档
访问 http://localhost:8000/docs 查看完整的交互式API文档（Swagger UI）

## 🎯 核心功能实现

### 情感分析
- 使用通义千问 API 进行智能对话生成
- 支持多种情感类型：开心、难过、焦虑、愤怒等
- 提供情感强度评估（0-10分）

### 共情回应生成
- 基于情感状态生成个性化回应
- 结合对话历史和知识库提供上下文相关回复
- 支持情感标签和建议生成

### 向量数据库集成
- 使用Chroma存储对话历史
- 支持相似对话检索
- 知识库管理和检索
- 情感模式学习

## 🔧 API接口

### 聊天接口
```http
POST http://localhost:8000/chat
Content-Type: application/json

{
  "message": "用户消息",
  "session_id": "会话ID（可选）",
  "user_id": "用户ID（可选）"
}
```

### 会话历史
```http
GET http://localhost:8000/sessions/{session_id}/history?limit=20
```

### 会话摘要
```http
GET http://localhost:8000/sessions/{session_id}/summary
```

## 🎨 界面预览

- 现代化的聊天界面设计
- 情感标签可视化
- 建议按钮快速回复
- 流畅的动画效果
- 响应式设计，支持移动端

## 🔮 未来规划

- [ ] 集成LlamaIndex进行知识增强
- [ ] 添加语音交互功能
- [ ] 支持多语言
- [ ] 情感趋势分析
- [ ] 个性化推荐系统
- [ ] 移动端App开发

## 🚀 生产部署

### 部署检查清单

- [ ] 配置生产环境的`.env`文件
- [ ] 更新CORS允许的域名（不要使用`*`）
- [ ] 配置反向代理（Nginx）
- [ ] 启用HTTPS/SSL证书
- [ ] 配置数据库备份策略
- [ ] 设置日志轮转
- [ ] 配置监控和告警

### Nginx配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 后端API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 数据库备份

```bash
# 备份数据库
mysqldump -u root -p emotional_chat > backup_$(date +%Y%m%d).sql

# 恢复数据库
mysql -u root -p emotional_chat < backup_20251010.sql

# 设置自动备份（crontab）
0 2 * * * mysqldump -u root -p[password] emotional_chat > /backup/emotional_chat_$(date +\%Y\%m\%d).sql
```

## 📊 监控和维护

### 系统监控

```bash
# 检查后端健康状态
curl http://localhost:8000/health

# 查看MySQL连接数
mysql -u root -p -e "SHOW STATUS LIKE 'Threads_connected';"

# 查看数据库大小
mysql -u root -p -e "SELECT table_schema AS 'Database', ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)' FROM information_schema.tables WHERE table_schema = 'emotional_chat' GROUP BY table_schema;"
```

### 日志管理

```bash
# 查看系统日志（存储在数据库中）
mysql -u root -p -e "SELECT * FROM emotional_chat.system_logs ORDER BY created_at DESC LIMIT 20;"

# 查看用户活跃度
mysql -u root -p -e "SELECT DATE(created_at) as date, COUNT(DISTINCT user_id) as active_users FROM emotional_chat.chat_messages GROUP BY DATE(created_at) ORDER BY date DESC LIMIT 7;"

# 查看情感分布统计
mysql -u root -p -e "SELECT emotion, COUNT(*) as count FROM emotional_chat.chat_messages WHERE emotion IS NOT NULL GROUP BY emotion ORDER BY count DESC;"
```

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

---

💝 **让AI更有温度，让陪伴更懂你** 💝
