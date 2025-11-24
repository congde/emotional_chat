#!/bin/bash
# 安装编译 dlib 所需的系统依赖
# 适用于 Alibaba Cloud Linux / CentOS
# Python 3.10 版本

echo "正在安装系统依赖..."

# 安装 Python 3.10 开发头文件（解决 Python.h 缺失问题）
yum install -y python310-devel || yum install -y python3-devel

# 安装编译工具
yum install -y cmake gcc gcc-c++ make

# 安装其他可能需要的依赖
yum install -y pkgconfig

echo "系统依赖安装完成！"
echo "现在可以运行: python3.10 -m pip install --user -r requirements.txt"

