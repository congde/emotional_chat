# 项目脚本

这里存放不属于应用运行时源码的一次性工具、维护命令和兼容入口。

## 常用脚本

- `db_manager.py`：数据库迁移管理。
- `init_rag_knowledge.py`：初始化 RAG 知识库。
- `quick_start.py`：旧版全量初始化入口。
- `run_backend.ps1`：仅启动后端的 PowerShell 包装脚本。
- `start_services.sh` / `restart_services.sh`：Linux 运维脚本。
- `setup_macbook.sh`：macOS 环境初始化。
- `demo_agent.py`：Agent 演示。
- `simple_backend.py`：旧 Python 环境的兼容后端。
- `test_rag_eval.py`：RAG 手工评估脚本。

所有命令都应从项目根目录执行，例如：

```bash
python scripts/db_manager.py current
python scripts/init_rag_knowledge.py
```

## 示例脚本

演示代码统一位于 `scripts/examples/`。请从项目根目录运行，例如：

```bash
python scripts/examples/intent_recognition_demo.py
```
