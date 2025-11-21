.PHONY: help db-init db-upgrade db-downgrade db-check db-current db-history db-reset install run quick-start rag-init

help:
	@echo "可用的命令:"
	@echo ""
	@echo "基础命令:"
	@echo "  make install      - 安装依赖"
	@echo "  make run          - 运行后端服务（自动构建知识库和RAG）"
	@echo "  make quick-start  - 快速启动（推荐，可选）"
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

install:
	pip install -r requirements.txt

db-init:
	python db_manager.py init

db-upgrade:
	python db_manager.py upgrade

db-downgrade:
	python db_manager.py downgrade

db-check:
	python db_manager.py check

db-current:
	python db_manager.py current

db-history:
	python db_manager.py history

db-reset:
	python db_manager.py reset

run:
	python run_backend.py

quick-start:
	python quick_start.py

rag-init:
	python init_rag_knowledge.py

