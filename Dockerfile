# 多阶段构建
FROM python:3.9-slim as builder

# 构建参数：APT镜像源（可选：aliyun, tsinghua, ustc, 或留空使用官方源）
ARG APT_MIRROR=aliyun
# 构建参数：PIP镜像源（可选：aliyun, tsinghua, douban, 或留空使用官方源）
ARG PIP_MIRROR=aliyun

# 设置工作目录
WORKDIR /app

# 配置APT镜像源加速（针对中国大陆网络环境）
RUN if [ "$APT_MIRROR" = "aliyun" ]; then \
        echo "使用阿里云镜像源" && \
        sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
        sed -i 's|http://deb.debian.org|http://mirrors.aliyun.com|g' /etc/apt/sources.list 2>/dev/null || \
        (echo "deb http://mirrors.aliyun.com/debian/ bullseye main" > /etc/apt/sources.list && \
         echo "deb http://mirrors.aliyun.com/debian-security/ bullseye-security main" >> /etc/apt/sources.list && \
         echo "deb http://mirrors.aliyun.com/debian/ bullseye-updates main" >> /etc/apt/sources.list); \
    elif [ "$APT_MIRROR" = "tsinghua" ]; then \
        echo "使用清华大学镜像源" && \
        sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
        sed -i 's|http://deb.debian.org|http://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list 2>/dev/null || \
        (echo "deb http://mirrors.tuna.tsinghua.edu.cn/debian/ bullseye main" > /etc/apt/sources.list && \
         echo "deb http://mirrors.tuna.tsinghua.edu.cn/debian-security/ bullseye-security main" >> /etc/apt/sources.list && \
         echo "deb http://mirrors.tuna.tsinghua.edu.cn/debian/ bullseye-updates main" >> /etc/apt/sources.list); \
    elif [ "$APT_MIRROR" = "ustc" ]; then \
        echo "使用中科大镜像源" && \
        sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
        sed -i 's|http://deb.debian.org|http://mirrors.ustc.edu.cn|g' /etc/apt/sources.list 2>/dev/null || \
        (echo "deb http://mirrors.ustc.edu.cn/debian/ bullseye main" > /etc/apt/sources.list && \
         echo "deb http://mirrors.ustc.edu.cn/debian-security/ bullseye-security main" >> /etc/apt/sources.list && \
         echo "deb http://mirrors.ustc.edu.cn/debian/ bullseye-updates main" >> /etc/apt/sources.list); \
    else \
        echo "使用官方镜像源"; \
    fi

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    cmake \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 配置PIP镜像源加速（针对中国大陆网络环境）
RUN if [ "$PIP_MIRROR" = "aliyun" ]; then \
        pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
        pip config set install.trusted-host mirrors.aliyun.com; \
    elif [ "$PIP_MIRROR" = "tsinghua" ]; then \
        pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/ && \
        pip config set install.trusted-host pypi.tuna.tsinghua.edu.cn; \
    elif [ "$PIP_MIRROR" = "douban" ]; then \
        pip config set global.index-url https://pypi.douban.com/simple/ && \
        pip config set install.trusted-host pypi.douban.com; \
    else \
        echo "使用官方PyPI源"; \
    fi

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir --user -r requirements.txt

# 生产阶段
FROM python:3.9-slim

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 创建非root用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 设置工作目录
WORKDIR /app

# 从builder阶段复制Python包
COPY --from=builder /root/.local /home/appuser/.local

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p /app/logs /app/chroma_db /app/uploads && \
    chown -R appuser:appuser /app

# 切换到非root用户
USER appuser

# 添加用户本地bin到PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["python", "run_backend.py"]
