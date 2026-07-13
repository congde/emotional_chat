#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/log"

export REACT_APP_API_URL="${REACT_APP_API_URL:-http://localhost:8000}"
export PORT="${PORT:-3000}"
export HOST="${HOST:-0.0.0.0}"

mkdir -p "$LOG_DIR"

echo "=========================================="
echo "心语 AI 服务启动"
echo "前端 API 地址: $REACT_APP_API_URL"
echo "前端端口: $PORT"
echo "=========================================="

cd "$PROJECT_ROOT"
echo "启动后端服务..."
nohup /usr/local/bin/python3.10 run_backend.py > "$LOG_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo "$BACKEND_PID" > "$LOG_DIR/backend.pid"
echo "后端启动中，PID: $BACKEND_PID"

sleep 3

cd "$PROJECT_ROOT/frontend"
if [ ! -d node_modules ]; then
    echo "未找到 node_modules，正在安装依赖..."
    npm install
fi

echo "启动前端服务..."
nohup npm start > "$LOG_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo "$FRONTEND_PID" > "$LOG_DIR/frontend.pid"
echo "前端启动中，PID: $FRONTEND_PID"

echo "=========================================="
echo "前端: http://$HOST:$PORT"
echo "后端: http://localhost:8000"
echo "API 文档: http://localhost:8000/docs"
echo "后端日志: $LOG_DIR/backend.log"
echo "前端日志: $LOG_DIR/frontend.log"
echo "=========================================="
