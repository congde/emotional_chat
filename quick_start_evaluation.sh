#!/bin/bash
# 快速启动评估系统

echo "========================================"
echo "  自动化评估系统 - 快速启动脚本"
echo "========================================"
echo ""

# 1. 检查Python环境
echo "1. 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "✗ 未找到Python3，请先安装Python"
    exit 1
fi
echo "✓ Python环境正常"
echo ""

# 2. 升级数据库（添加评估表）
echo "2. 升级数据库..."
if [ -f "db_manager.py" ]; then
    python3 db_manager.py upgrade
    if [ $? -eq 0 ]; then
        echo "✓ 数据库升级成功"
    else
        echo "⚠ 数据库升级失败，请手动检查"
    fi
else
    echo "⚠ 未找到db_manager.py，跳过数据库升级"
fi
echo ""

# 3. 检查配置
echo "3. 检查配置..."
if [ -f "config.env" ]; then
    if grep -q "DASHSCOPE_API_KEY" config.env || grep -q "OPENAI_API_KEY" config.env; then
        echo "✓ API密钥已配置"
    else
        echo "⚠ 未找到API密钥，评估功能可能不可用"
        echo "  请在config.env中配置DASHSCOPE_API_KEY或OPENAI_API_KEY"
    fi
else
    echo "⚠ 未找到config.env，请根据env_example.txt创建配置文件"
fi
echo ""

# 4. 启动后端（如果未运行）
echo "4. 检查后端服务..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ 后端服务已在运行"
else
    echo "启动后端服务..."
    echo "请在另一个终端运行: python3 run_backend.py"
    echo ""
    read -p "按Enter继续（确保后端已启动）..." 
fi
echo ""

# 5. 运行测试
echo "5. 运行评估系统测试..."
echo ""
python3 test_evaluation.py

echo ""
echo "========================================"
echo "  快速启动完成"
echo "========================================"
echo ""
echo "📚 接下来可以："
echo "  1. 访问 http://localhost:8000/docs 查看API文档"
echo "  2. 阅读 docs/evaluation_system_guide.md 了解详细用法"
echo "  3. 使用 test_evaluation.py 进行更多测试"
echo ""

