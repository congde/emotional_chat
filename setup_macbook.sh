#!/bin/bash
# MacBook 快速配置脚本
# 用于在 macOS 上快速配置和安装项目依赖

set -e  # 遇到错误立即退出

# 获取脚本所在目录（项目根目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 检查是否为 macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "此脚本仅适用于 macOS 系统"
    exit 1
fi

print_info "开始 MacBook 配置流程..."

# 检测系统架构（全局使用）
ARCH=$(uname -m)
export ARCH

# 1. 检查并安装 Homebrew
print_info "步骤 1/8: 检查 Homebrew..."
if ! command_exists brew; then
    print_warning "Homebrew 未安装，正在安装..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # 添加 Homebrew 到 PATH
    if [[ "$ARCH" == "arm64" ]]; then
        # Apple Silicon
        BREW_PATH="/opt/homebrew/bin/brew"
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    else
        # Intel Mac
        BREW_PATH="/usr/local/bin/brew"
        if [ -f "$BREW_PATH" ]; then
            eval "$($BREW_PATH shellenv)"
        fi
    fi
    
    # 验证 brew 现在可用
    if ! command_exists brew; then
        print_error "Homebrew 安装后无法使用，请手动运行: eval \"\$($BREW_PATH shellenv)\""
        exit 1
    fi
    
    print_success "Homebrew 安装完成"
else
    print_success "Homebrew 已安装: $(brew --version | head -n 1)"
fi

# 2. 检查并安装 Xcode Command Line Tools
print_info "步骤 2/8: 检查 Xcode Command Line Tools..."
if ! xcode-select -p &>/dev/null; then
    print_warning "Xcode Command Line Tools 未安装，正在安装..."
    xcode-select --install
    print_warning "请在弹出的窗口中完成安装，然后按任意键继续..."
    read -n 1 -s
else
    print_success "Xcode Command Line Tools 已安装"
fi

# 3. 检查并安装 Python 3.10+
print_info "步骤 3/8: 检查 Python 版本..."
NEED_INSTALL_PYTHON=false

if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f1)
    PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
        print_warning "Python 版本过低 ($PYTHON_VERSION)，需要 3.10+"
        NEED_INSTALL_PYTHON=true
    else
        print_success "Python $PYTHON_VERSION 已安装"
    fi
else
    print_warning "Python 3 未安装"
    NEED_INSTALL_PYTHON=true
fi

if [ "$NEED_INSTALL_PYTHON" = true ]; then
    print_info "正在安装 Python 3.10..."
    brew install python@3.10 || {
        print_error "Python 安装失败"
        exit 1
    }
    
    # 重新加载 PATH 以使用新安装的 Python
    if [[ "$ARCH" == "arm64" ]]; then
        export PATH="/opt/homebrew/bin:$PATH"
    else
        export PATH="/usr/local/bin:$PATH"
    fi
fi

# 验证并设置 Python 命令
PYTHON3_CMD=$(command -v python3 || command -v python3.10 || command -v python3.11)
if [ -z "$PYTHON3_CMD" ]; then
    print_error "无法找到 Python 3"
    exit 1
fi
print_success "使用 Python: $($PYTHON3_CMD --version)"

# 导出 Python 命令供后续使用
export PYTHON3_CMD

# 4. 安装系统依赖
print_info "步骤 4/8: 安装系统依赖..."
print_info "安装编译工具和库..."

# 核心编译工具
brew install cmake pkg-config libffi openssl || true

# 图像处理依赖
brew install jpeg libpng libtiff freetype || true

# 音频处理依赖（可选）
print_info "安装音频处理依赖（可选）..."
brew install portaudio ffmpeg || print_warning "某些音频依赖安装失败，多模态功能可能受限"

print_success "系统依赖安装完成"

# 5. 检查并安装 MySQL
print_info "步骤 5/8: 检查 MySQL..."
if ! command_exists mysql; then
    print_warning "MySQL 未安装，正在安装..."
    brew install mysql
    print_info "MySQL 安装完成"
else
    print_success "MySQL 已安装: $(mysql --version | cut -d' ' -f1,2,3)"
fi

# 启动 MySQL 服务
print_info "启动 MySQL 服务..."
if brew services list 2>/dev/null | grep -q "^mysql.*started"; then
    print_success "MySQL 服务已在运行"
else
    print_info "启动 MySQL 服务..."
    brew services start mysql || {
        print_warning "MySQL 服务启动失败，可能需要手动启动: brew services start mysql"
    }
    print_info "等待 MySQL 启动（可能需要 10-30 秒）..."
    sleep 5
    
    # 检查 MySQL 是否真的启动了
    if ! brew services list 2>/dev/null | grep -q "^mysql.*started"; then
        print_warning "MySQL 可能尚未完全启动，请稍后手动检查: brew services list"
    fi
fi

# 6. 检查并安装 Node.js
print_info "步骤 6/8: 检查 Node.js..."
if ! command_exists node; then
    print_warning "Node.js 未安装，正在安装..."
    brew install node
else
    print_success "Node.js 已安装: $(node --version)"
fi

# 7. 创建虚拟环境（如果不存在）
print_info "步骤 7/8: 设置 Python 虚拟环境..."
if [ ! -d "venv" ]; then
    print_info "创建虚拟环境..."
    $PYTHON3_CMD -m venv venv || {
        print_error "虚拟环境创建失败"
        exit 1
    }
    print_success "虚拟环境创建完成"
else
    print_success "虚拟环境已存在"
fi

# 激活虚拟环境
print_info "激活虚拟环境..."
source venv/bin/activate || {
    print_error "无法激活虚拟环境"
    exit 1
}

# 升级 pip
print_info "升级 pip..."
pip install --upgrade pip setuptools wheel || {
    print_warning "pip 升级失败，但可以继续"
}

# Mac Python 3.10 SQLite3 兼容性修复
print_info "检查并修复 SQLite3 兼容性问题..."
if python3 -c "import sqlite3; v=sqlite3.sqlite_version.split('.'); exit(0 if int(v[0])>3 or (int(v[0])==3 and int(v[1])>=35) else 1)" 2>/dev/null; then
    print_success "SQLite3 版本符合要求"
else
    print_warning "SQLite3 版本可能过旧，安装 pysqlite3-binary..."
    pip install pysqlite3-binary || {
        print_warning "pysqlite3-binary 安装失败，将使用内置 sqlite3（可能影响 ChromaDB）"
    }
fi

# 8. 配置环境变量
print_info "步骤 8/8: 配置环境变量..."
if [ ! -f "config.env" ]; then
    if [ -f "config.env.example" ]; then
        cp config.env.example config.env
        print_success "已创建 config.env 文件"
        print_warning "请编辑 config.env 文件，配置 API 密钥和数据库密码"
        print_info "可以使用以下命令编辑："
        print_info "  nano config.env"
        print_info "  或"
        print_info "  code config.env  # 如果安装了 VS Code"
    else
        print_warning "config.env.example 文件不存在，请手动创建 config.env"
    fi
else
    print_success "config.env 文件已存在"
fi

# 完成
print_success "=========================================="
print_success "基础环境配置完成！"
print_success "=========================================="
echo ""
print_info "下一步操作："
echo ""
echo "1. 配置环境变量："
echo "   ${YELLOW}nano config.env${NC}"
echo "   需要配置："
echo "   - LLM_API_KEY (阿里云通义千问 API 密钥)"
echo "   - MYSQL_PASSWORD (MySQL root 密码)"
echo ""
echo "2. 创建数据库："
echo "   ${YELLOW}mysql -u root -p -e \"CREATE DATABASE emotional_chat CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;\"${NC}"
echo ""
echo "3. 安装 Python 依赖："
echo "   ${YELLOW}source venv/bin/activate${NC}"
echo "   ${YELLOW}make install${NC} 或 ${YELLOW}pip install -r requirements.txt${NC}"
echo ""
echo "4. 初始化数据库："
echo "   ${YELLOW}make db-upgrade${NC}"
echo ""
echo "5. 初始化 RAG 知识库："
echo "   ${YELLOW}make rag-init${NC}"
echo ""
echo "6. 安装前端依赖："
echo "   ${YELLOW}cd frontend && npm install${NC}"
echo ""
echo "7. 启动服务："
echo "   ${YELLOW}make run${NC}  # 后端（终端1）"
echo "   ${YELLOW}cd frontend && npm start${NC}  # 前端（终端2）"
echo ""
print_info "详细配置指南请查看: ${BLUE}docs/MACBOOK_SETUP.md${NC}"
echo ""
print_warning "注意：虚拟环境仅在当前脚本执行期间激活"
print_info "脚本结束后，需要手动激活虚拟环境: ${YELLOW}source venv/bin/activate${NC}"
echo ""
