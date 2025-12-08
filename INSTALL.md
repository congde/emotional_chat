# 安装指南

## 推荐：使用虚拟环境

**强烈建议使用虚拟环境**来避免依赖冲突和污染系统 Python 环境。

### Ubuntu/Linux 系统

```bash
# 1. 确保已安装 Python 3.10+
python3 --version

# 2. 安装虚拟环境工具（如果未安装）
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip

# 3. 创建虚拟环境
python3 -m venv venv

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

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
.\venv\Scripts\Activate.ps1
# 或者使用 cmd: venv\Scripts\activate.bat

# 4. 升级 pip
python -m pip install --upgrade pip

# 5. 安装依赖
pip install -r requirements.txt -c constraints.txt
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
python3 -m venv venv
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
