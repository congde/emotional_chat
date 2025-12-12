#!/bin/bash

# 停止旧进程
pkill -f "python3.*run_backend.py" 2>/dev/null
pkill -f "python3.10.*run_backend.py" 2>/dev/null
pkill -f "react-scripts start" 2>/dev/null

# 等待进程完全停止
sleep 3

# 启动后端（使用 Python 3.10）
cd /home/workSpace/emotional_chat
nohup python3.10 run_backend.py > log/backend.log 2>&1 &
echo "后端启动中..."

# 等待后端启动
sleep 5

# 启动前端
cd /home/workSpace/emotional_chat/frontend
nohup npm start > ../log/frontend.log 2>&1 &
echo "前端启动中..."

# 等待服务完全启动
sleep 10

# 检查服务状态
echo ""
echo "===== 服务状态 ====="
ps aux | grep -E "run_backend|react-scripts" | grep -v grep
echo ""
echo "===== 端口监听 ====="
ss -tlnp | grep -E ":3000|:8000" 2>/dev/null || netstat -tlnp | grep -E ":3000|:8000" 2>/dev/null
echo ""
echo "服务启动完成！"
echo "前端地址: http://localhost:3000"
echo "后端地址: http://localhost:8000"

