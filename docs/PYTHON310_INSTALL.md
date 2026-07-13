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

## 推荐：使用虚拟环境

**强烈建议使用虚拟环境**来避免依赖冲突和污染系统 Python 环境。

### Ubuntu/Linux 系统

```bash
# 1. 确保已安装 Python 3.10+
python3.10 --version

# 2. 安装虚拟环境工具（如果未安装）
sudo apt-get update
sudo apt-get install -y python3.10-venv python3.10-pip

# 3. 使用 Python 3.10 创建虚拟环境
python3.10 -m venv venv

# 4. 激活虚拟环境
source venv/bin/activate

# 5. 升级 pip
pip install --upgrade pip

# 6. 安装依赖（使用约束文件避免冲突）
pip install -r requirements.txt -c constraints.txt

# 或者如果遇到冲突，可以分步安装：
# pip install protobuf>=4.21.6
# pip install langchain>=0.3.15 langchain-core>=0.3.15
# pip install -r requirements.txt
```

### Windows 系统

```powershell
# 1. 确保已安装 Python 3.10+
python --version

# 2. 使用 Python 3.10 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
.\venv\Scripts\Activate.ps1
# 或者使用 cmd: venv\Scripts\activate.bat

# 4. 升级 pip
python -m pip install --upgrade pip

# 5. 安装依赖
pip install -r requirements.txt -c constraints.txt
```

### macOS 系统

```bash
# 1. 使用 Python 3.10 创建虚拟环境
python3.10 -m venv venv310

# 2. 激活虚拟环境
source venv310/bin/activate

# 3. 升级 pip
pip install --upgrade pip

# 4. 安装依赖
pip install -r requirements-py310.txt -i https://pypi.org/simple
```

## 使用 Python 3.10 安装依赖

```bash
# 使用 Python 3.10 和官方 PyPI 源
python3.10 -m pip install -r requirements-py310.txt -i https://pypi.org/simple

# 或者使用国内镜像（如果可用）
python3.10 -m pip install -r requirements-py310.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 依赖冲突解决方案

如果安装时遇到以下错误：

### 错误 1: protobuf 版本冲突
```
grpcio-status 1.51.1 requires protobuf>=4.21.6, but you have protobuf 3.20.3
```

**解决方案：**
```bash
# 先升级 protobuf
pip install --upgrade protobuf>=4.21.6

# 然后重新安装依赖
pip install -r requirements.txt
```

### 错误 2: langchain-core 版本冲突
```
langchain-huggingface 0.1.2 requires langchain-core<0.4.0,>=0.3.15, but you have langchain-core 0.2.43
```

**解决方案：**
```bash
# 先升级 langchain 和 langchain-core
pip install --upgrade langchain>=0.3.15 langchain-core>=0.3.15

# 然后重新安装依赖
pip install -r requirements.txt
```

### 错误 3: pydantic-settings 冲突
```
pydantic-settings 2.6.1 requires pydantic>=2.7.0, but you have pydantic 1.10.24
```

**解决方案：**
```bash
# 如果不需要 pydantic-settings，卸载它
pip uninstall pydantic-settings -y

# 如果某个包依赖 pydantic-settings，需要检查是哪个包引入的
pip show pydantic-settings

# 然后决定是否卸载引入它的包，或者升级到 Pydantic v2（需要修改代码）
```

## 完整安装步骤（Ubuntu 20.04）

```bash
# 1. 创建虚拟环境
python3.10 -m venv venv
source venv/bin/activate

# 2. 升级 pip
pip install --upgrade pip setuptools wheel

# 3. 先安装关键依赖（解决冲突）
pip install protobuf>=4.21.6
pip install langchain>=0.3.15 langchain-core>=0.3.15
pip install pydantic>=1.9.2,<2.0.0

# 4. 安装其他依赖
pip install -r requirements.txt

# 5. 如果安装了 pydantic-settings，卸载它（代码使用 Pydantic v1）
pip uninstall pydantic-settings -y 2>/dev/null || true

# 6. 验证安装
pip check
python test_dependencies.py
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

运行测试脚本验证依赖是否正确安装：

```bash
python test_dependencies.py
python test_dependencies_fix.py
```

## 常见问题

### Q: 为什么必须使用虚拟环境？
A: 虚拟环境可以：
- 隔离项目依赖，避免与系统 Python 包冲突
- 确保依赖版本一致性
- 方便项目部署和迁移

### Q: 如果不想使用虚拟环境怎么办？
A: 可以全局安装，但需要：
- 确保系统 Python 版本 >= 3.10
- 手动解决所有依赖冲突
- 承担污染系统环境的风险

### Q: langchain 0.3.x 与 Pydantic v1 兼容吗？
A: langchain 0.3.x 理论上需要 Pydantic v2，但某些版本可能仍支持 v1。
如果遇到兼容性问题，需要：
1. 升级到 Pydantic v2
2. 修改代码中的 `@validator` 为 `@field_validator`
3. 更新其他 Pydantic v1 API

### Q: 如何检查依赖冲突？
A: 运行以下命令：
```bash
pip check
```

### Q: M 系列处理器需要注意什么？
A: 确保使用原生 ARM64 版本的 Python，不要使用 Rosetta 2 转译的版本。

## 卸载

如果需要卸载所有依赖：

```bash
# 在虚拟环境中
pip freeze > installed_packages.txt
pip uninstall -r installed_packages.txt -y

# 或者直接删除虚拟环境
deactivate  # 退出虚拟环境
rm -rf venv  # 删除虚拟环境目录（Linux/Mac）
# 或 Windows: rmdir /s venv
```

## 注意事项

1. **M 系列处理器**: 确保使用原生 ARM64 版本的 Python，不要使用 Rosetta 2 转译的版本
2. **依赖冲突**: 如果遇到依赖冲突，建议使用虚拟环境隔离
3. **系统 Python**: 不要替换系统默认的 Python，使用虚拟环境或 pyenv
