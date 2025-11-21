.PHONY: help db-init db-upgrade db-downgrade db-check db-current db-history db-reset install run quick-start rag-init

# 获取 Makefile 所在目录作为项目根目录
# 使用 abspath 确保兼容性，适用于 GNU Make 3.81+
# 去掉尾部斜杠
ROOT_DIR := $(patsubst %/,%,$(dir $(abspath $(firstword $(MAKEFILE_LIST)))))

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
	cd $(ROOT_DIR) && pip install -r requirements.txt

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

