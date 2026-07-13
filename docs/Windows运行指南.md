# Windows 运行指南

本文档介绍如何在 Windows 系统上运行心语情感陪伴机器人项目。

## 📋 环境要求

- Windows 10/11
- Python 3.10+
- Node.js 16+
- MySQL 8.0+
- Git

## 🚀 快速开始

### 1. 安装基础软件

#### 1.1 安装 Python

1. 访问 [Python 官网](https://www.python.org/downloads/) 下载 Python 3.10+
2. 安装时 **务必勾选** "Add Python to PATH"
3. 验证安装：
   ```powershell
   python --version
   pip --version
   ```

#### 1.2 安装 Node.js

1. 访问 [Node.js 官网](https://nodejs.org/) 下载 LTS 版本
2. 按默认选项安装
3. 验证安装：
   ```powershell
   node --version
   npm --version
   ```

#### 1.3 安装 MySQL

1. 访问 [MySQL 下载页面](https://dev.mysql.com/downloads/installer/) 下载 MySQL Installer
2. 选择 "MySQL Server" 进行安装
3. 记住设置的 root 密码
4. 验证安装：
   ```powershell
   mysql --version
   ```

#### 1.4 安装 Git（可选）

1. 访问 [Git 官网](https://git-scm.com/download/win) 下载安装
2. 克隆项目：
   ```powershell
   git clone https://github.com/congde/emotional_chat.git
   cd emotional_chat
   ```

### 2. 安装项目依赖

打开 PowerShell，进入项目目录：

```powershell
cd emotional_chat

# 安装后端依赖
pip install -r requirements.txt

# 安装前端依赖
cd frontend
npm install
cd ..
```

> ⚠️ **注意**：如果安装 `dlib` 或 `face-recognition` 失败，可以在 `requirements.txt` 中注释掉这两行（人脸识别功能将不可用）。

### 3. 配置环境变量

```powershell
# 复制配置文件模板
copy config.env.example config.env

# 使用记事本编辑
notepad config.env
```

编辑 `config.env`，填入以下必要配置：

```bash
# 阿里云通义千问 API Key（必填）
LLM_API_KEY=your_qwen_api_key_here
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# MySQL 数据库配置（必填）
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=emotional_chat

# 模型配置
DEFAULT_MODEL=qwen-plus
TEMPERATURE=0.7
MAX_TOKENS=1000

# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

**获取通义千问 API Key**：
1. 访问 [阿里云 DashScope](https://dashscope.console.aliyun.com/)
2. 注册/登录阿里云账号
3. 创建 API Key

### 4. 初始化数据库

#### 4.1 创建数据库

打开 MySQL 命令行或使用 MySQL Workbench：

```sql
CREATE DATABASE emotional_chat CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 4.2 运行数据库迁移

```powershell
# 在项目根目录执行
alembic upgrade head
```

#### 4.3 初始化 RAG 知识库（可选但推荐）

```powershell
python scripts/init_rag_knowledge.py
```

### 5. 启动服务

需要打开 **两个** PowerShell 窗口。

#### 终端 1：启动后端服务

```powershell
cd emotional_chat
python run_backend.py
```

后端启动成功后会显示：
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### 终端 2：启动前端服务

```powershell
cd emotional_chat\frontend
npm start
```

前端启动成功后会自动打开浏览器。

### 6. 访问应用

- 🌐 **前端界面**：http://localhost:3000
- 🔌 **后端 API**：http://localhost:8000
- 📖 **API 文档**：http://localhost:8000/docs

### 7. 验证服务

```powershell
# 健康检查
curl http://localhost:8000/health

# 测试聊天接口
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"message\": \"你好\", \"user_id\": \"test_user\"}"
```

## 🐳 Docker 部署（可选）

如果你安装了 Docker Desktop for Windows，可以使用 Docker 一键部署：

```powershell
# 配置环境变量
copy config.env.example config.env
notepad config.env

# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

## ❓ 常见问题

### 1. pip 安装依赖失败

```powershell
# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. npm 安装依赖慢

```powershell
# 设置淘宝镜像
npm config set registry https://registry.npmmirror.com

# 重新安装
cd frontend
npm install
```

### 3. MySQL 连接失败

- 确认 MySQL 服务已启动（服务管理器中查看 MySQL80）
- 检查 `config.env` 中的数据库配置是否正确
- 确认数据库 `emotional_chat` 已创建

### 4. 端口被占用

```powershell
# 查看端口占用
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# 结束占用进程（替换 PID）
taskkill /PID <PID> /F
```

### 5. dlib/face-recognition 安装失败

这两个包需要 C++ 编译环境，如果不需要人脸识别功能，可以在 `requirements.txt` 中注释掉：

```
# face-recognition>=1.3.0
# dlib>=19.24.0
```

### 6. pysqlite3-binary 不支持 Windows

Windows 不支持 `pysqlite3-binary`，项目已在 `backend/main.py` 中做了兼容处理：

```python
import sys
# 使用内置sqlite3替代pysqlite3-binary (Windows不支持pysqlite3-binary)
sys.modules['pysqlite3'] = __import__('sqlite3')
```

如果遇到 sqlite3 相关错误，确保这段代码在 `backend/main.py` 文件开头。

### 7. PowerShell 执行策略限制

如果遇到脚本执行限制，以管理员身份运行：

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 📝 开发建议

### 使用 VS Code

推荐使用 VS Code 进行开发，安装以下扩展：
- Python
- Pylance
- ES7+ React/Redux/React-Native snippets
- MySQL (可选)

### 虚拟环境（推荐）

```powershell
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt
```

## 🔗 相关链接

- [项目主页](https://github.com/congde/emotional_chat)
- [阿里云 DashScope](https://dashscope.console.aliyun.com/)
- [Python 下载](https://www.python.org/downloads/)
- [Node.js 下载](https://nodejs.org/)
- [MySQL 下载](https://dev.mysql.com/downloads/installer/)

---

如有问题，欢迎提交 Issue 或联系维护者。

