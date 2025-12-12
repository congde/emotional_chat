# MacBook 配置指南 🍎

本文档专门为 macOS (MacBook) 用户提供详细的配置和安装指南。

## 📋 目录

- [⚡ 快速开始（5分钟）](#快速开始5分钟)
- [系统要求](#系统要求)
- [环境准备](#环境准备)
- [安装步骤](#安装步骤)
- [启动服务](#启动服务)
- [常见问题](#常见问题)
- [性能优化](#性能优化)

## ⚡ 快速开始（5分钟）

### 方式一：自动配置脚本（最简单）

```bash
# 1. 运行自动配置脚本
./setup_macbook.sh

# 2. 配置环境变量
nano config.env
# 需要配置：LLM_API_KEY 和 MYSQL_PASSWORD

# 3. 创建数据库
mysql -u root -p -e "CREATE DATABASE emotional_chat CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 4. 安装依赖和初始化
source venv/bin/activate
make install
# 注意: 如果遇到 pysqlite3-binary 相关错误，可以忽略（代码会自动使用内置 sqlite3）
make db-upgrade
make rag-init

# 5. 安装前端依赖
cd frontend && npm install && cd ..

# 6. 启动服务（两个终端）
# 终端1：source venv/bin/activate && make run
# 终端2：cd frontend && npm start
```

### 方式二：手动安装

```bash
# 1. 安装 Homebrew（如果未安装）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. 安装依赖
brew install python@3.10 mysql node cmake

# 3. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 4. 安装 Python 依赖
pip install -r requirements.txt

# 5. 配置环境变量
cp config.env.example config.env
nano config.env

# 6. 创建数据库
mysql -u root -p -e "CREATE DATABASE emotional_chat CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 7. 初始化数据库和知识库
make db-upgrade
make rag-init

# 8. 安装前端依赖
cd frontend && npm install && cd ..
```

### 必需配置项

在 `config.env` 文件中必须配置：

```bash
# API 密钥（必需）
LLM_API_KEY=your_qwen_api_key_here
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# 数据库配置（必需）
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=emotional_chat
```

### 访问地址

- **前端界面**: http://localhost:3000
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

> 💡 **提示**: 如果你需要更详细的说明或遇到问题，请继续阅读下面的详细指南。

## 🖥️ 系统要求

### 最低要求

- **macOS**: 10.15 (Catalina) 或更高版本（推荐 macOS 12+）
- **Python**: 3.10 或更高版本（推荐 3.10-3.12）
- **内存**: 至少 8GB RAM（推荐 16GB+）
- **存储**: 至少 10GB 可用空间
- **处理器**: Intel 或 Apple Silicon (M1/M2/M3)

### 推荐配置

- **macOS**: 13.0 (Ventura) 或更高版本
- **Python**: 3.10 或 3.11
- **内存**: 16GB RAM 或更高
- **存储**: 20GB+ 可用空间
- **Homebrew**: 最新版本

## 🔧 环境准备

### 1. 安装 Homebrew（如果未安装）

Homebrew 是 macOS 上最常用的包管理器：

```bash
# 安装 Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 验证安装
brew --version
```

**Apple Silicon (M1/M2/M3) 用户注意**：
安装完成后，可能需要将 Homebrew 添加到 PATH：

```bash
# 对于 Apple Silicon Mac
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

### 2. 安装 Xcode Command Line Tools

这是编译 Python 包（如 dlib、opencv-python）所必需的：

```bash
# 安装 Xcode Command Line Tools
xcode-select --install

# 如果已安装，可以验证
xcode-select -p
```

### 3. 安装 Python 3.10+

```bash
# 使用 Homebrew 安装 Python 3.10（或其他版本）
brew install python@3.10

# 或者安装 Python 3.11
brew install python@3.11

# 验证安装
python3 --version
which python3

# 验证 pip
pip3 --version
```

**注意**：
- macOS 可能预装了 Python 3，但版本可能较旧，建议使用 Homebrew 安装最新版本
- 如果安装了多个 Python 版本，确保 `python3` 指向正确的版本

### 4. 安装系统依赖

```bash
# 安装编译工具和依赖
brew install cmake
brew install pkg-config
brew install libffi
brew install openssl

# 图像处理相关依赖
brew install jpeg
brew install libpng
brew install libtiff
brew install freetype

# 音频处理相关依赖（如果需要多模态功能）
brew install portaudio
brew install ffmpeg

# 验证安装
cmake --version
```

### 5. 安装 MySQL

```bash
# 使用 Homebrew 安装 MySQL
brew install mysql

# 启动 MySQL 服务
brew services start mysql

# 或者手动启动（不自动启动）
mysql.server start

# 设置 MySQL root 密码（首次安装需要）
mysql_secure_installation
```

**MySQL 配置**：
- 默认端口：3306
- 默认 socket：`/tmp/mysql.sock`
- 配置文件：`/opt/homebrew/etc/my.cnf` (Apple Silicon) 或 `/usr/local/etc/my.cnf` (Intel)

### 6. 安装 Node.js 和 npm（前端需要）

```bash
# 使用 Homebrew 安装 Node.js
brew install node

# 或者安装 LTS 版本
brew install node@18

# 验证安装
node --version
npm --version
```

## 📦 安装步骤

### 1. 克隆项目（如果还没有）

```bash
cd ~/workspace  # 或你喜欢的目录
git clone <repository-url> emotional_chat
cd emotional_chat
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp config.env.example config.env

# 编辑配置文件（使用你喜欢的编辑器）
nano config.env
# 或者
vim config.env
# 或者使用 VS Code
code config.env
```

**配置说明**：

```bash
# API配置 - 使用阿里云通义千问(Qwen)
LLM_API_KEY=your_qwen_api_key_here
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# MySQL数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=emotional_chat

# 模型配置
DEFAULT_MODEL=qwen-plus
TEMPERATURE=0.7
MAX_TOKENS=1000

# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=true

# ChromaDB配置
CHROMA_PERSIST_DIRECTORY=./chroma_db
```

### 3. 创建 Python 虚拟环境（推荐）

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 验证虚拟环境
which python
```

**提示**：每次打开新终端窗口时，需要重新激活虚拟环境：
```bash
source venv/bin/activate
```

### 4. 安装 Python 依赖

#### 方式一：使用 pip（标准方式）

```bash
# 确保在项目根目录
cd /home/workSpace/emotional_chat

# 升级 pip
pip install --upgrade pip

# 安装依赖（可能需要 10-30 分钟，特别是编译 dlib 和 opencv-python）
pip install -r requirements.txt

# 可选：Mac Python 3.10 用户可尝试安装 pysqlite3-binary（解决 SQLite3 兼容性问题）
# 如果安装失败（找不到版本），可以跳过，代码会自动使用内置 sqlite3
# pip install pysqlite3-binary || echo "pysqlite3-binary 安装失败，将使用内置 sqlite3"
```

**注意编译过程**：
- `dlib` 和 `face-recognition` 需要编译，可能需要 10-30 分钟
- 如果不需要人脸识别功能，可以编辑 `requirements.txt` 注释掉 `face-recognition>=1.3.0`

#### 方式二：使用 uv（推荐，更快）

```bash
# 安装 uv（如果未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 重新加载 shell 配置
source ~/.zshrc  # 或 ~/.bash_profile

# 使用 uv 安装依赖
make install-uv

# 或者直接使用 uv
uv sync
```

#### 方式三：使用 Makefile（推荐）

```bash
# 使用 Makefile 安装依赖
make install

# 或者使用 uv（更快）
make install-uv
```

### 5. 处理特殊依赖（可选，如果遇到问题）

#### 如果 dlib 安装失败

```bash
# 方法1：确保安装了所有依赖
brew install cmake pkg-config

# 方法2：使用 conda（如果安装了 Anaconda/Miniconda）
conda install -c conda-forge dlib

# 方法3：如果不需要人脸识别，可以跳过
# 编辑 requirements.txt，注释掉 face-recognition 相关行
```

#### 如果 opencv-python 安装失败

```bash
# 使用预编译的 wheel 文件
pip install opencv-python-headless

# 或者使用 conda
conda install -c conda-forge opencv
```

### 6. 初始化数据库

```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE emotional_chat CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 运行数据库迁移
make db-upgrade

# 或者手动运行
alembic upgrade head

# 验证数据库连接
make db-check
```

### 7. 初始化 RAG 知识库（推荐）

```bash
# 使用 Makefile
make rag-init

# 或者直接运行
python init_rag_knowledge.py
```

### 8. 安装前端依赖

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 如果遇到权限问题，可以使用
npm install --legacy-peer-deps

# 返回项目根目录
cd ..
```

## 🚀 启动服务

### 启动后端服务

**终端 1 - 后端服务**：

```bash
# 确保在项目根目录
cd /home/workSpace/emotional_chat

# 激活虚拟环境（如果使用）
source venv/bin/activate

# 启动后端服务
make run

# 或者直接运行
python run_backend.py

# 或者使用 uvicorn
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

后端服务将在 `http://localhost:8000` 启动。

### 启动前端服务

**终端 2 - 前端服务**：

```bash
# 进入前端目录
cd frontend

# 启动开发服务器
npm start
```

前端应用将在 `http://localhost:3000` 启动。

### 验证服务

```bash
# 健康检查
curl http://localhost:8000/health

# 测试聊天接口
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好", "user_id": "test_user"}'
```

在浏览器中访问：
- 前端界面：http://localhost:3000
- API 文档：http://localhost:8000/docs

## ⚠️ 常见问题

### 1. Python 版本问题

**问题**：`python3 --version` 显示旧版本

**解决方案**：
```bash
# 检查所有 Python 版本
which -a python3

# 使用 Homebrew 安装最新版本
brew install python@3.10

# 创建别名（添加到 ~/.zshrc 或 ~/.bash_profile）
alias python3='/opt/homebrew/bin/python3'  # Apple Silicon
# 或
alias python3='/usr/local/bin/python3'     # Intel

# 重新加载配置
source ~/.zshrc
```

### 2. 编译错误（dlib、opencv-python）

**问题**：编译 dlib 或 opencv-python 时出错

**解决方案**：
```bash
# 确保安装了所有编译工具
xcode-select --install
brew install cmake pkg-config

# 设置环境变量（帮助编译器找到依赖）
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig"  # Apple Silicon
# 或
export PKG_CONFIG_PATH="/usr/local/lib/pkgconfig"     # Intel

# 重新安装
pip install --force-reinstall --no-cache-dir dlib opencv-python
```

### 3. MySQL 连接错误

**问题**：无法连接到 MySQL

**解决方案**：
```bash
# 检查 MySQL 是否运行
brew services list | grep mysql

# 启动 MySQL
brew services start mysql

# 检查端口是否被占用
lsof -i :3306

# 测试连接
mysql -u root -p -h localhost
```

### 4. 端口被占用

**问题**：8000 或 3000 端口已被占用

**解决方案**：
```bash
# 查找占用端口的进程
lsof -i :8000
lsof -i :3000

# 杀死进程（替换 PID 为实际进程ID）
kill -9 <PID>

# 或者修改配置使用其他端口
# 在 config.env 中修改 PORT=8001
```

### 5. 权限问题

**问题**：npm install 或 pip install 权限错误

**解决方案**：
```bash
# 不要使用 sudo 安装 Python 包
# 使用虚拟环境或 --user 标志

# Python 包
pip install --user -r requirements.txt

# npm 包
npm install --legacy-peer-deps
```

### 6. Apple Silicon (M1/M2/M3) 特殊问题

**问题**：某些包不支持 Apple Silicon

**解决方案**：
```bash
# 使用 Rosetta 2 运行（不推荐，性能差）
arch -x86_64 /bin/bash
pip install -r requirements.txt

# 更好的方案：使用原生版本或等待更新
# 大部分包已经支持 Apple Silicon
```

### 7. SQLite3 兼容性问题（Mac Python 3.10）

**问题**：Mac 上 Python 3.10 的 SQLite3 版本过旧，导致 ChromaDB 无法正常工作

**症状**：
- 启动时出现 `sqlite3` 相关错误
- ChromaDB 初始化失败
- 错误信息包含 "SQLite version" 或 "pysqlite3"

**解决方案**：

**方法一：安装 pysqlite3-binary（可选，推荐）**
```bash
# 激活虚拟环境
source venv/bin/activate

# 尝试安装 pysqlite3-binary（如果找不到版本可以跳过）
pip install pysqlite3-binary || echo "⚠️ pysqlite3-binary 安装失败，将使用内置 sqlite3"

# 验证安装（如果安装成功）
python -c "import pysqlite3; print(pysqlite3.sqlite_version)" 2>/dev/null || echo "将使用内置 sqlite3"
```

**注意**：如果 `pysqlite3-binary` 安装失败（找不到匹配版本），这是正常的，代码会自动使用内置的 `sqlite3`，不影响使用。

**方法二：使用项目内置的兼容性模块（已自动处理）**
项目已包含 `backend/utils/sqlite_compat.py` 模块，会自动处理 SQLite3 兼容性问题。
如果仍然遇到问题，可以手动测试：

```bash
# 激活虚拟环境
source venv/bin/activate

# 测试 SQLite3 兼容性
python -c "from backend.utils.sqlite_compat import setup_sqlite3; setup_sqlite3()"
```

**方法三：重新编译 Python（高级）**
如果上述方法都不行，可以重新编译 Python 3.10 并链接到更新的 SQLite3：

```bash
# 安装更新的 SQLite3
brew install sqlite

# 重新安装 Python 3.10（会链接到新的 SQLite3）
brew reinstall python@3.10

# 重新创建虚拟环境
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**验证修复**：
```bash
# 检查 SQLite3 版本
python -c "import sqlite3; print('SQLite版本:', sqlite3.sqlite_version)"

# 应该显示 3.35 或更高版本
```

### 8. ChromaDB 问题

**问题**：ChromaDB 初始化失败

**解决方案**：
```bash
# 确保目录权限正确
mkdir -p chroma_db
chmod 755 chroma_db

# 清理并重新初始化
rm -rf chroma_db/*
python init_rag_knowledge.py

# 如果仍然失败，检查 SQLite3 兼容性（见上面的问题 7）
```

### 9. 依赖冲突

**问题**：包版本冲突

**解决方案**：
```bash
# 使用虚拟环境隔离
python3 -m venv venv
source venv/bin/activate

# 升级 pip 和 setuptools
pip install --upgrade pip setuptools wheel

# 重新安装
pip install -r requirements.txt
```

## 🎯 性能优化

### 1. 使用 Apple Silicon 优化

如果使用 M1/M2/M3 Mac：

```bash
# 使用优化的 NumPy（如果可用）
pip install numpy --upgrade

# 某些包可能支持 Metal 加速
# 检查包的 Apple Silicon 支持情况
```

### 2. 减少内存使用

如果内存有限：

```bash
# 禁用不必要的功能
# 编辑 config.env，设置较小的 MAX_TOKENS

# 不使用 Docker（节省内存）
# 直接运行服务而不是 docker-compose
```

### 3. 使用生产模式

开发完成后：

```bash
# 修改 config.env
DEBUG=false

# 使用 Gunicorn 运行（如果安装）
pip install gunicorn
gunicorn backend.app:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 📝 快速检查清单

在开始之前，确保：

- [ ] Homebrew 已安装
- [ ] Xcode Command Line Tools 已安装
- [ ] Python 3.10+ 已安装
- [ ] MySQL 已安装并运行
- [ ] Node.js 和 npm 已安装
- [ ] 环境变量已配置（config.env）
- [ ] 数据库已创建
- [ ] 虚拟环境已创建并激活
- [ ] Python 依赖已安装
- [ ] 前端依赖已安装
- [ ] RAG 知识库已初始化

## 🔗 相关资源

- [Homebrew 官网](https://brew.sh/)
- [Python 官方文档](https://docs.python.org/3/)
- [MySQL 官方文档](https://dev.mysql.com/doc/)
- [Node.js 官方文档](https://nodejs.org/docs/)

## 💡 提示

1. **使用虚拟环境**：强烈建议使用 Python 虚拟环境，避免污染系统 Python
2. **定期更新**：定期运行 `brew update && brew upgrade` 更新系统包
3. **查看日志**：遇到问题时，查看日志文件 `log/backend.log`
4. **使用 Makefile**：项目提供了便捷的 Makefile 命令，推荐使用
5. **Apple Silicon 优化**：M1/M2/M3 Mac 性能更好，但某些包可能需要原生支持

## 🆘 获取帮助

如果遇到问题：

1. 查看本文档的[常见问题](#常见问题)部分
2. 查看项目主 README.md
3. 检查日志文件
4. 提交 GitHub Issue（包含错误信息和系统信息）

---

**祝你在 MacBook 上顺利运行心语情感陪伴机器人！** 💝

