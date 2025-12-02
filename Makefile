.PHONY: help db-init db-upgrade db-downgrade db-check db-current db-history db-reset install install-uv run quick-start rag-init rag-test rag-demo uv-sync uv-lock

# 获取 Makefile 所在目录作为项目根目录
# 使用 abspath 确保兼容性，适用于 GNU Make 3.81+
# 去掉尾部斜杠
ROOT_DIR := $(patsubst %/,%,$(dir $(abspath $(firstword $(MAKEFILE_LIST)))))

# 检测是否安装了 uv
UV := $(shell command -v uv 2> /dev/null)

help:
	@echo "可用的命令:"
	@echo ""
	@echo "基础命令:"
	@echo "  make install      - 安装依赖（使用 pip）"
	@echo "  make install-uv   - 安装依赖（使用 uv，推荐，更快）"
	@echo "  make run          - 运行后端服务（自动构建知识库和RAG）"
	@echo "  make quick-start  - 快速启动（推荐，可选）"
	@echo ""
	@echo "uv 命令（推荐）:"
	@echo "  make uv-sync      - 同步依赖（从 pyproject.toml 安装）"
	@echo "  make uv-lock      - 生成 uv.lock 锁定文件"
	@echo ""
	@echo "数据库命令:"
	@echo "  make db-init      - 初始化数据库"
	@echo "  make db-upgrade   - 升级数据库到最新版本"
	@echo "  make db-downgrade - 降级数据库一个版本"
	@echo "  make db-check     - 检查数据库连接"
	@echo "  make db-current   - 查看当前数据库版本"
	@echo "  make db-history   - 查看迁移历史"
	@echo "  make db-reset     - 重置数据库（危险！）"
	@echo ""
	@echo "RAG知识库命令:"
	@echo "  make rag-init     - 初始化RAG知识库"
	@echo "  make rag-test     - 测试RAG系统"
	@echo "  make rag-demo     - 演示RAG效果"

# 传统 pip 安装方式（兼容性保留）
install:
	cd $(ROOT_DIR) && pip install -r requirements.txt

# uv 安装方式（推荐，更快）
install-uv:
	@if [ -z "$(UV)" ]; then \
		echo "⚠️  uv 未安装，正在安装..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		echo "✅ uv 安装完成，请重新运行 make install-uv"; \
	else \
		echo "✅ 使用 uv 安装依赖..."; \
		cd $(ROOT_DIR) && uv sync; \
	fi

# uv 同步依赖（从 pyproject.toml）
uv-sync:
	@if [ -z "$(UV)" ]; then \
		echo "❌ 错误: uv 未安装"; \
		echo "安装方法: curl -LsSf https://astral.sh/uv/install.sh | sh"; \
		exit 1; \
	fi
	cd $(ROOT_DIR) && uv sync

# uv 生成锁定文件
uv-lock:
	@if [ -z "$(UV)" ]; then \
		echo "❌ 错误: uv 未安装"; \
		echo "安装方法: curl -LsSf https://astral.sh/uv/install.sh | sh"; \
		exit 1; \
	fi
	cd $(ROOT_DIR) && uv lock

db-init:
	cd $(ROOT_DIR) && python db_manager.py init

db-upgrade:
	cd $(ROOT_DIR) && python db_manager.py upgrade

db-downgrade:
	cd $(ROOT_DIR) && python db_manager.py downgrade

db-check:
	cd $(ROOT_DIR) && python db_manager.py check

db-current:
	cd $(ROOT_DIR) && python db_manager.py current

db-history:
	cd $(ROOT_DIR) && python db_manager.py history

db-reset:
	cd $(ROOT_DIR) && python db_manager.py reset

run:
	cd $(ROOT_DIR) && python run_backend.py

quick-start:
	cd $(ROOT_DIR) && python quick_start.py

rag-init:
	cd $(ROOT_DIR) && python init_rag_knowledge.py

rag-test:
	@echo "测试RAG系统..."
	@echo "检查RAG API端点: http://localhost:8000/api/rag/test"
	@curl -s http://localhost:8000/api/rag/test || echo "⚠️  请确保后端服务正在运行 (make run)"

rag-demo:
	@echo "演示RAG效果对比..."
	@echo "测试问题: 失眠怎么办？"
	@curl -s -X POST http://localhost:8000/api/rag/ask \
		-H "Content-Type: application/json" \
		-d '{"question": "失眠怎么办？"}' || echo "⚠️  请确保后端服务正在运行 (make run)"

