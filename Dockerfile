# 多阶段构建
FROM python:3.9-slim as builder

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    cmake \
    && rm -rf /var/lib/apt/lists/*

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
