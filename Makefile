.PHONY: help db-init db-upgrade db-downgrade db-check db-current db-history db-reset install run

help:
	@echo "可用的命令:"
	@echo "  make install      - 安装依赖"
	@echo "  make db-init      - 初始化数据库"
	@echo "  make db-upgrade   - 升级数据库到最新版本"
	@echo "  make db-downgrade - 降级数据库一个版本"
	@echo "  make db-check     - 检查数据库连接"
	@echo "  make db-current   - 查看当前数据库版本"
	@echo "  make db-history   - 查看迁移历史"
	@echo "  make db-reset     - 重置数据库（危险！）"
	@echo "  make run          - 运行后端服务"

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

