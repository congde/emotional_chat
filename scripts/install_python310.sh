#!/bin/bash
# Python 3.10 安装脚本 - 适用于 Alibaba Cloud Linux 3

set -e

echo "=========================================="
echo "Python 3.10 安装脚本"
echo "适用于 Alibaba Cloud Linux 3"
echo "=========================================="

# 检查是否已安装
if command -v python3.10 &> /dev/null; then
    echo "Python 3.10 已安装: $(python3.10 --version)"
    exit 0
fi

# 安装编译依赖
echo "步骤 1: 安装编译依赖..."
yum groupinstall -y "Development Tools" || true
yum install -y openssl-devel bzip2-devel libffi-devel zlib-devel readline-devel sqlite-devel xz-devel gdbm-devel tk-devel || true

# 下载 Python 3.10.12
echo "步骤 2: 下载 Python 3.10.12..."
cd /tmp
PYTHON_VERSION="3.10.12"
PYTHON_TAR="Python-${PYTHON_VERSION}.tgz"
PYTHON_DIR="Python-${PYTHON_VERSION}"

if [ ! -f "$PYTHON_TAR" ]; then
    wget https://www.python.org/ftp/python/${PYTHON_VERSION}/${PYTHON_TAR} || {
        echo "下载失败，尝试使用镜像源..."
        wget https://mirrors.huaweicloud.com/python/${PYTHON_VERSION}/${PYTHON_TAR} || {
            echo "下载失败，请检查网络连接"
            exit 1
        }
    }
fi

# 解压
if [ ! -d "$PYTHON_DIR" ]; then
    tar xzf "$PYTHON_TAR"
fi

# 编译安装
echo "步骤 3: 编译 Python 3.10.12（这可能需要几分钟）..."
cd "$PYTHON_DIR"
./configure --enable-optimizations --prefix=/usr/local/python3.10 --with-ssl

# 获取 CPU 核心数
CORES=$(nproc)
echo "使用 $CORES 个核心进行编译..."

make -j${CORES} || make

echo "步骤 4: 安装 Python 3.10..."
make altinstall

# 创建软链接
echo "步骤 5: 创建软链接..."
ln -sf /usr/local/python3.10/bin/python3.10 /usr/local/bin/python3.10
ln -sf /usr/local/python3.10/bin/pip3.10 /usr/local/bin/pip3.10

# 验证安装
echo "步骤 6: 验证安装..."
if command -v python3.10 &> /dev/null; then
    echo "✓ Python 3.10 安装成功!"
    python3.10 --version
    echo ""
    echo "Python 3.10 路径: $(which python3.10)"
    echo "pip3.10 路径: $(which pip3.10)"
    echo ""
    echo "现在可以使用以下命令安装依赖:"
    echo "  pip3.10 install -r requirements-py310.txt -i https://pypi.org/simple"
else
    echo "✗ 安装失败，请检查错误信息"
    exit 1
fi


