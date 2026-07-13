#!/usr/bin/env python3
"""
数据库管理工具
封装Alembic命令，提供便捷的数据库迁移管理
"""

import sys
import os
import subprocess
from pathlib import Path

if os.name == "nt" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from config import Config
from backend.database import engine, Base


def run_alembic_command(command: str, *args):
    """
    运行alembic命令
    
    Args:
        command: alembic命令（如 upgrade, downgrade等）
        *args: 额外的参数
    """
    try:
        # 构建完整的alembic命令
        cmd = [sys.executable, "-m", "alembic", command] + list(args)
        
        print(f"🔧 执行命令: {' '.join(cmd)}")
        print("-" * 60)
        
        # 运行命令
        # 使用兼容Python 3.6的方式
        result = subprocess.run(
            cmd,
            cwd=project_root
        )
        
        if result.returncode != 0:
            print(f"❌ 命令执行失败，退出码: {result.returncode}")
            return False
        
        print("-" * 60)
        print("✅ 命令执行成功")
        return True
        
    except FileNotFoundError:
        print("❌ 错误: 找不到alembic命令")
        print("💡 请确保已安装alembic: pip install alembic")
        return False
    except Exception as e:
        print(f"❌ 执行命令时出错: {e}")
        return False


def check_database_connection():
    """检查数据库连接"""
    try:
        print("🔍 检查数据库连接...")
        print(f"   数据库: {Config.MYSQL_DATABASE}")
        print(f"   主机: {Config.MYSQL_HOST}:{Config.MYSQL_PORT}")
        print(f"   用户: {Config.MYSQL_USER}")
        
        # 尝试连接数据库
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        print("✅ 数据库连接成功")
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        print("\n💡 故障排查建议:")
        print("  1. 检查MySQL服务是否运行")
        print("  2. 检查config.env中的数据库配置")
        print("  3. 确保数据库已创建")
        print("  4. 检查用户权限")
        return False


def init():
    """初始化数据库（创建所有表）"""
    print("\n" + "=" * 60)
    print("📦 初始化数据库")
    print("=" * 60 + "\n")
    
    # 先检查数据库连接
    if not check_database_connection():
        return False
    
    # 检查是否需要创建数据库
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            # 尝试查询，如果表不存在会报错
            conn.execute(text("SELECT 1 FROM users LIMIT 1"))
        print("ℹ️  数据库表已存在，将执行升级操作")
    except Exception:
        print("ℹ️  数据库表不存在，将创建所有表")
    
    # 运行alembic upgrade head来初始化
    return run_alembic_command("upgrade", "head")


def upgrade(revision: str = "head"):
    """升级数据库到指定版本"""
    print("\n" + "=" * 60)
    print(f"⬆️  升级数据库到版本: {revision}")
    print("=" * 60 + "\n")
    
    if not check_database_connection():
        return False
    
    return run_alembic_command("upgrade", revision)


def downgrade(revision: str = "-1"):
    """降级数据库一个版本"""
    print("\n" + "=" * 60)
    print(f"⬇️  降级数据库版本: {revision}")
    print("=" * 60 + "\n")
    
    if not check_database_connection():
        return False
    
    return run_alembic_command("downgrade", revision)


def check():
    """检查数据库连接和状态"""
    print("\n" + "=" * 60)
    print("🔍 检查数据库状态")
    print("=" * 60 + "\n")
    
    success = check_database_connection()
    
    if success:
        # 检查当前版本
        print("\n📊 查看当前数据库版本...")
        run_alembic_command("current")
    
    return success


def current():
    """查看当前数据库版本"""
    print("\n" + "=" * 60)
    print("📊 当前数据库版本")
    print("=" * 60 + "\n")
    
    if not check_database_connection():
        return False
    
    return run_alembic_command("current")


def history():
    """查看迁移历史"""
    print("\n" + "=" * 60)
    print("📜 数据库迁移历史")
    print("=" * 60 + "\n")
    
    return run_alembic_command("history")


def reset():
    """重置数据库（危险操作！）"""
    print("\n" + "=" * 60)
    print("⚠️  重置数据库")
    print("=" * 60 + "\n")
    print("⚠️  警告: 此操作将删除所有数据！")
    
    # 确认操作
    confirm = input("请输入 'yes' 确认重置数据库: ")
    if confirm.lower() != 'yes':
        print("❌ 操作已取消")
        return False
    
    if not check_database_connection():
        return False
    
    # 先降级到base
    print("\n⬇️  降级到初始版本...")
    if not run_alembic_command("downgrade", "base"):
        return False
    
    # 再升级到head
    print("\n⬆️  重新创建所有表...")
    return run_alembic_command("upgrade", "head")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python scripts/db_manager.py <command> [args...]")
        print("\n可用命令:")
        print("  init       - 初始化数据库（创建所有表）")
        print("  upgrade    - 升级数据库到最新版本")
        print("  downgrade  - 降级数据库一个版本")
        print("  check      - 检查数据库连接和状态")
        print("  current    - 查看当前数据库版本")
        print("  history    - 查看迁移历史")
        print("  reset      - 重置数据库（危险！）")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    
    success = False
    
    if command == "init":
        success = init()
    elif command == "upgrade":
        revision = args[0] if args else "head"
        success = upgrade(revision)
    elif command == "downgrade":
        revision = args[0] if args else "-1"
        success = downgrade(revision)
    elif command == "check":
        success = check()
    elif command == "current":
        success = current()
    elif command == "history":
        success = history()
    elif command == "reset":
        success = reset()
    else:
        print(f"❌ 未知命令: {command}")
        print("使用 'python scripts/db_manager.py' 查看帮助")
        sys.exit(1)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

