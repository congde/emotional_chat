#!/bin/bash
# 前端停止脚本

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 从 PID 文件读取进程 ID
if [ -f "frontend.pid" ]; then
    PID=$(cat frontend.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "停止前端服务 (PID: $PID)..."
        kill $PID
        rm frontend.pid
        echo "✅ 前端服务已停止"
    else
        echo "⚠️  进程 $PID 不存在，清理 PID 文件"
        rm frontend.pid
    fi
else
    # 如果没有 PID 文件，尝试通过进程名查找
    echo "未找到 PID 文件，尝试通过进程名查找..."
    PIDS=$(pgrep -f "react-scripts start")
    if [ -n "$PIDS" ]; then
        echo "找到前端进程: $PIDS"
        for PID in $PIDS; do
            kill $PID
            echo "已停止进程 $PID"
        done
        echo "✅ 前端服务已停止"
    else
        echo "⚠️  未找到运行中的前端服务"
    fi
fi

