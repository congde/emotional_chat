# Python 3.10 安装指南

## 为什么需要 Python 3.10？

- **M 系列处理器支持**: Python 3.10+ 对 Apple Silicon (ARM64) 有更好的原生支持
- **更新的依赖包**: 可以使用 Pydantic v2, FastAPI 0.115+, NumPy 1.26+ 等最新版本
- **性能优化**: 新版本包含 ARM64 优化，性能更好

## 安装方法

### macOS (M 系列处理器)

```bash
# 使用 Homebrew
brew install python@3.10

# 验证安装
python3.10 --version

# 使用 Python 3.10 安装依赖
python3.10 -m pip install -r requirements-py310.txt -i https://pypi.org/simple
```

### Linux (CentOS/Alibaba Linux)

#### 方法 1: 从源码编译（推荐）

```bash
# 安装编译依赖
yum groupinstall -y "Development Tools"
yum install -y openssl-devel bzip2-devel libffi-devel zlib-devel readline-devel sqlite-devel

# 下载 Python 3.10
cd /tmp
wget https://www.python.org/ftp/python/3.10.12/Python-3.10.12.tgz
tar xzf Python-3.10.12.tgz
cd Python-3.10.12

# 编译安装
./configure --enable-optimizations --prefix=/usr/local/python3.10
make -j$(nproc)
make altinstall

# 创建软链接
ln -s /usr/local/python3.10/bin/python3.10 /usr/local/bin/python3.10
ln -s /usr/local/python3.10/bin/pip3.10 /usr/local/bin/pip3.10

# 验证
python3.10 --version
```

#### 方法 2: 使用 pyenv（推荐用于开发环境）

```bash
# 安装 pyenv
curl https://pyenv.run | bash

# 添加到 PATH
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc

# 安装 Python 3.10
pyenv install 3.10.12
pyenv global 3.10.12

# 验证
python --version
```

### Ubuntu/Debian

```bash
# 添加 deadsnakes PPA
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update

# 安装 Python 3.10
sudo apt install python3.10 python3.10-venv python3.10-dev

# 验证
python3.10 --version
```

## 使用 Python 3.10 安装依赖

```bash
# 使用 Python 3.10 和官方 PyPI 源
python3.10 -m pip install -r requirements-py310.txt -i https://pypi.org/simple

# 或者使用国内镜像（如果可用）
python3.10 -m pip install -r requirements-py310.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 创建虚拟环境（推荐）

```bash
# 使用 Python 3.10 创建虚拟环境
python3.10 -m venv venv310

# 激活虚拟环境
source venv310/bin/activate  # Linux/macOS
# 或
venv310\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements-py310.txt -i https://pypi.org/simple
```

## 验证安装

```bash
# 检查 Python 版本
python --version  # 应该显示 Python 3.10.x

# 检查关键包版本
python -c "import numpy; print(f'NumPy: {numpy.__version__}')"
python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"
python -c "import pydantic; print(f'Pydantic: {pydantic.__version__}')"
```

## 注意事项

1. **M 系列处理器**: 确保使用原生 ARM64 版本的 Python，不要使用 Rosetta 2 转译的版本
2. **依赖冲突**: 如果遇到依赖冲突，建议使用虚拟环境隔离
3. **系统 Python**: 不要替换系统默认的 Python，使用虚拟环境或 pyenv

