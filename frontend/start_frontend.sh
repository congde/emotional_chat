#!/bin/bash
# 前端启动脚本

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 设置默认环境变量（如果未设置）
export REACT_APP_API_URL=${REACT_APP_API_URL:-http://localhost:8000}
export PORT=${PORT:-3000}
export HOST=${HOST:-0.0.0.0}

# 显示配置信息
echo "=========================================="
echo "前端服务启动配置"
echo "=========================================="
echo "API地址: $REACT_APP_API_URL"
echo "端口: $PORT"
echo "主机: $HOST"
echo "工作目录: $SCRIPT_DIR"
echo "=========================================="
echo ""

# 检查 node_modules 是否存在
if [ ! -d "node_modules" ]; then
    echo "⚠️  未找到 node_modules，正在安装依赖..."
    npm install
fi

# 启动前端服务
echo "🚀 启动前端服务..."
nohup npm start > frontend.log 2>&1 &
FRONTEND_PID=$!

# 保存 PID
echo $FRONTEND_PID > frontend.pid

echo "✅ 前端服务已启动"
echo "PID: $FRONTEND_PID"
echo "日志文件: $SCRIPT_DIR/frontend.log"
echo "访问地址: http://$HOST:$PORT"
echo ""
echo "查看日志: tail -f $SCRIPT_DIR/frontend.log"
echo "停止服务: kill $FRONTEND_PID 或 ./stop_frontend.sh"

