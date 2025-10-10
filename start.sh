#!/bin/bash

echo "🚀 启动情感聊天机器人系统..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

# 检查Node.js环境
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装Node.js"
    exit 1
fi

# 安装Python依赖
echo "📦 安装Python依赖..."
pip3 install -r requirements.txt

# 安装前端依赖
echo "📦 安装前端依赖..."
cd frontend
npm install
cd ..

# 创建启动脚本
echo "🎯 创建启动脚本..."
cat > start_backend.sh << 'EOF'
#!/bin/bash
cd /home/emotional_chat
python3 run_backend.py
EOF

cat > start_frontend.sh << 'EOF'
#!/bin/bash
cd /home/emotional_chat/frontend
npm start
EOF

chmod +x start_backend.sh start_frontend.sh

echo "✅ 安装完成！"
echo ""
echo "📋 启动说明："
echo "1. 启动后端服务：./start_backend.sh"
echo "2. 启动前端服务：./start_frontend.sh"
echo ""
echo "🌐 访问地址："
echo "- 前端界面：http://localhost:3003"
echo "- 后端API：http://localhost:8008"
echo "- API文档：http://localhost:8008/docs"
echo ""
echo "💡 提示：需要同时启动后端和前端服务才能正常使用"
