#!/bin/bash
# 心语AI 一键启动脚本

# 启动后端 (端口8000)
cd /home/workSpace/emotional_chat
nohup /usr/local/bin/python3.10 run_backend.py > backend.log 2>&1 &
echo "后端启动中... PID: $!"

# 启动前端 (端口3000)
cd /home/workSpace/emotional_chat/frontend
nohup npm start > frontend.log 2>&1 &
echo "前端启动中... PID: $!"

echo ""
echo "✅ 服务启动完成"
echo "前端访问: http://8.130.162.82:3000"
echo "后端API: http://8.130.162.82:8000"
echo "API文档: http://8.130.162.82:8000/docs"
