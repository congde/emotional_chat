#!/bin/bash
# 心语AI 一键启动脚本

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# 设置环境变量（可根据实际情况修改）
export REACT_APP_API_URL=${REACT_APP_API_URL:-http://localhost:8000}
export PORT=${PORT:-3000}
export HOST=${HOST:-0.0.0.0}

echo "=========================================="
echo "心语AI 服务启动"
echo "=========================================="
echo "前端API地址: $REACT_APP_API_URL"
echo "前端端口: $PORT"
echo "=========================================="
echo ""

# 启动后端 (端口8000)
echo "🚀 启动后端服务..."
cd "$SCRIPT_DIR"
nohup /usr/local/bin/python3.10 run_backend.py > backend.log 2>&1 &
BACKEND_PID=$!
echo "后端启动中... PID: $BACKEND_PID"
echo $BACKEND_PID > backend.pid

# 等待后端启动
sleep 3

# 启动前端 (端口3000)
echo "🚀 启动前端服务..."
cd "$SCRIPT_DIR/frontend"

# 检查 node_modules
if [ ! -d "node_modules" ]; then
    echo "⚠️  未找到 node_modules，正在安装依赖..."
    npm install
fi

# 设置前端环境变量并启动
export PORT=$PORT
export HOST=$HOST
nohup npm start > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "前端启动中... PID: $FRONTEND_PID"
echo $FRONTEND_PID > frontend.pid

echo ""
echo "✅ 服务启动完成"
echo "=========================================="
echo "前端访问: http://$HOST:$PORT"
echo "后端API: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo "=========================================="
echo ""
echo "查看后端日志: tail -f $SCRIPT_DIR/backend.log"
echo "查看前端日志: tail -f $SCRIPT_DIR/frontend/frontend.log"
echo ""
echo "停止服务:"
echo "  后端: kill $BACKEND_PID"
echo "  前端: kill $FRONTEND_PID"
echo "  或使用: ./scripts/restart_services.sh"
