"""
SQLite3 兼容性处理模块

解决 Mac Python 3.10 上 SQLite3 不兼容的问题
优先使用 pysqlite3-binary，如果不可用则回退到内置 sqlite3
"""
import sys
import platform
import logging

logger = logging.getLogger(__name__)

def setup_sqlite3():
    """
    设置 SQLite3 兼容性
    
    优先级：
    1. pysqlite3-binary (推荐，支持 ChromaDB)
    2. 内置 sqlite3 (回退方案)
    
    Returns:
        bool: 是否成功设置
    """
    sqlite3_available = False
    pysqlite3_available = False
    
    # 检查 sys.modules 中是否已经有 sqlite3
    # 如果已有，检查它是否是 pysqlite3
    if 'sqlite3' in sys.modules:
        existing_sqlite3 = sys.modules['sqlite3']
        # 检查是否是 pysqlite3（通过模块名判断）
        if hasattr(existing_sqlite3, '__name__') and 'pysqlite3' in str(existing_sqlite3.__name__):
            pysqlite3_available = True
            sqlite3_available = True
            try:
                version = existing_sqlite3.sqlite_version
                logger.info(f"✓ 检测到已加载的 pysqlite3-binary，SQLite 版本: {version}")
                return True
            except AttributeError:
                pass
    
    # 首先尝试导入 pysqlite3-binary
    try:
        import pysqlite3
        # 替换 sys.modules 中的 sqlite3
        sys.modules['sqlite3'] = pysqlite3
        sqlite3_available = True
        pysqlite3_available = True
        
        # 验证版本
        try:
            version = pysqlite3.sqlite_version
            logger.info(f"✓ 使用 pysqlite3-binary，SQLite 版本: {version}")
        except AttributeError:
            logger.warning("pysqlite3 导入成功但无法获取版本信息")
            
    except ImportError:
        # 只在非 Windows 系统上输出警告（Windows 上 pysqlite3-binary 不可用是正常的）
        if platform.system() != 'Windows':
            logger.warning("pysqlite3-binary 不可用，尝试使用内置 sqlite3")
        
        # 回退到内置 sqlite3
        try:
            import sqlite3
            sqlite3_available = True
            
            # 为 ChromaDB 兼容性，设置 pysqlite3 别名
            sys.modules['pysqlite3'] = sqlite3
            
            # 验证版本
            try:
                version = sqlite3.sqlite_version
                logger.info(f"✓ 使用内置 sqlite3，SQLite 版本: {version}")
                
                # 检查版本是否足够新（ChromaDB 需要 SQLite 3.35+）
                version_parts = version.split('.')
                major = int(version_parts[0])
                minor = int(version_parts[1]) if len(version_parts) > 1 else 0
                
                if major < 3 or (major == 3 and minor < 35):
                    logger.warning(
                        f"⚠️ SQLite 版本 {version} 可能过旧，ChromaDB 需要 3.35+。"
                        f"建议安装 pysqlite3-binary: pip install pysqlite3-binary"
                    )
                    
            except (AttributeError, ValueError) as e:
                logger.warning(f"无法获取 SQLite 版本信息: {e}")
                
        except ImportError:
            logger.error("❌ 无法导入 sqlite3，这不应该发生")
            return False
    
    # 最终验证
    try:
        import sqlite3
        # 尝试创建一个测试连接
        conn = sqlite3.connect(':memory:')
        conn.execute('SELECT 1')
        conn.close()
        logger.info("✓ SQLite3 测试连接成功")
        return True
    except Exception as e:
        logger.error(f"❌ SQLite3 测试连接失败: {e}")
        return False

# 延迟执行设置，避免在导入时产生日志
# 只有在显式调用 setup_sqlite3() 时才会执行
# 或者在其他模块导入时通过显式调用触发

# 导出 sqlite3 模块供其他模块使用
# 先尝试导入，如果失败则设置为 None
try:
    import sqlite3
except ImportError:
    sqlite3 = None

__all__ = ['sqlite3', 'setup_sqlite3']

