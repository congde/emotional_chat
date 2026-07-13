#!/usr/bin/env python3
"""Start the backend and frontend development servers together."""

from __future__ import annotations

import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
IS_WINDOWS = os.name == "nt"


def _command_exists(command: str) -> bool:
    return shutil.which(command) is not None


def _start(command: list[str], cwd: Path, env: dict[str, str]) -> subprocess.Popen:
    kwargs: dict = {"cwd": cwd, "env": env}
    if IS_WINDOWS:
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True
    return subprocess.Popen(command, **kwargs)


def _stop(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return

    if IS_WINDOWS:
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    else:
        os.killpg(process.pid, signal.SIGTERM)


def main() -> int:
    npm = "npm.cmd" if IS_WINDOWS else "npm"
    if not _command_exists(npm):
        print("错误：未找到 npm，请先安装 Node.js。", file=sys.stderr)
        return 1
    if not (FRONTEND_DIR / "package.json").is_file():
        print("错误：未找到 frontend/package.json。", file=sys.stderr)
        return 1

    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PROJECT_ROOT", str(PROJECT_ROOT))
    env.setdefault("LANGCHAIN_TRACING_V2", "false")

    processes: list[tuple[str, subprocess.Popen]] = []
    try:
        print("启动后端：http://localhost:8000")
        backend = _start([sys.executable, "run_backend.py"], PROJECT_ROOT, env)
        processes.append(("后端", backend))

        print("启动前端：http://localhost:3000")
        frontend = _start([npm, "start"], FRONTEND_DIR, env)
        processes.append(("前端", frontend))

        print("前后端已启动，按 Ctrl+C 同时停止。")
        while True:
            for name, process in processes:
                return_code = process.poll()
                if return_code is not None:
                    print(f"{name}进程已退出（退出码 {return_code}）。", file=sys.stderr)
                    return return_code or 1
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n正在停止前后端服务……")
        return 0
    finally:
        for _, process in reversed(processes):
            _stop(process)


if __name__ == "__main__":
    raise SystemExit(main())
