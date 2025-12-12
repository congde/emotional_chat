#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLite3 兼容性测试脚本

测试 Mac Python 3.10 上的 SQLite3 兼容性处理
"""
import sys
import os
import platform

# Windows 控制台编码修复
if sys.platform == 'win32':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_basic_sqlite3():
    """测试基本的 SQLite3 功能"""
    print_section("测试 1: 基本 SQLite3 功能")
    
    try:
        import sqlite3
        print(f"✓ 成功导入 sqlite3")
        
        # 获取版本信息
        try:
            version = sqlite3.sqlite_version
            print(f"✓ SQLite 版本: {version}")
            
            # 检查版本是否符合要求（ChromaDB 需要 3.35+）
            version_parts = version.split('.')
            major = int(version_parts[0])
            minor = int(version_parts[1]) if len(version_parts) > 1 else 0
            
            if major > 3 or (major == 3 and minor >= 35):
                print(f"[OK] SQLite 版本符合 ChromaDB 要求 (>= 3.35)")
            else:
                print(f"[WARNING] SQLite 版本 {version} 可能过旧，ChromaDB 需要 3.35+")
                
        except AttributeError:
            print("[WARNING] 无法获取 SQLite 版本信息")
        
        # 测试基本操作
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)')
        cursor.execute('INSERT INTO test (name) VALUES (?)', ('test',))
        cursor.execute('SELECT * FROM test')
        result = cursor.fetchone()
        conn.close()
        
        if result and result[1] == 'test':
            print("✓ SQLite3 基本操作测试通过")
            return True
        else:
            print("❌ SQLite3 基本操作测试失败")
            return False
            
    except Exception as e:
        print(f"❌ SQLite3 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_compat_module():
    """测试兼容性模块"""
    print_section("测试 2: SQLite3 兼容性模块")
    
    try:
        from backend.utils.sqlite_compat import setup_sqlite3, sqlite3
        
        print("✓ 成功导入兼容性模块")
        
        # 执行设置
        result = setup_sqlite3()
        
        if result:
            print("[OK] 兼容性模块设置成功")
        else:
            print("[WARNING] 兼容性模块设置返回 False，但可能仍可使用")
        
        # 验证 sqlite3 是否可用
        if sqlite3 is not None:
            print("✓ sqlite3 模块可用")
            try:
                version = sqlite3.sqlite_version
                print(f"✓ 通过兼容模块获取 SQLite 版本: {version}")
            except AttributeError:
                print("[WARNING] 无法通过兼容模块获取版本信息")
        else:
            print("❌ sqlite3 模块不可用")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ 无法导入兼容性模块: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ 兼容性模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pysqlite3():
    """测试 pysqlite3-binary"""
    print_section("测试 3: pysqlite3-binary 可用性")
    
    try:
        import pysqlite3
        print("✓ pysqlite3-binary 已安装")
        
        try:
            version = pysqlite3.sqlite_version
            print(f"✓ pysqlite3 SQLite 版本: {version}")
            
            # 测试基本操作
            conn = pysqlite3.connect(':memory:')
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            result = cursor.fetchone()
            conn.close()
            
            if result:
                print("✓ pysqlite3 基本操作测试通过")
                return True
            else:
                print("❌ pysqlite3 基本操作测试失败")
                return False
                
        except AttributeError:
            print("⚠️ 无法获取 pysqlite3 版本信息")
            return False
            
    except ImportError:
        print("[INFO] pysqlite3-binary 未安装（这是正常的，将使用内置 sqlite3）")
        return None  # 不是错误，只是未安装

def test_chromadb_compatibility():
    """测试 ChromaDB 兼容性"""
    print_section("测试 4: ChromaDB 兼容性")
    
    try:
        # 先设置 SQLite3 兼容性
        from backend.utils.sqlite_compat import setup_sqlite3
        setup_sqlite3()
        
        import chromadb
        print("✓ 成功导入 chromadb")
        
        # 尝试创建客户端（使用内存模式）
        try:
            client = chromadb.Client()
            print("✓ 成功创建 ChromaDB 客户端")
            
            # 尝试创建集合
            collection = client.create_collection("test_collection")
            print("✓ 成功创建 ChromaDB 集合")
            
            # 尝试添加文档
            collection.add(
                documents=["测试文档"],
                ids=["test1"]
            )
            print("✓ 成功添加文档到 ChromaDB")
            
            # 尝试查询
            results = collection.query(
                query_texts=["测试"],
                n_results=1
            )
            print("✓ 成功查询 ChromaDB")
            
            print("✓ ChromaDB 兼容性测试通过")
            return True
            
        except Exception as e:
            print(f"[WARNING] ChromaDB 操作失败: {e}")
            print("   这可能是由于 SQLite3 版本过旧导致的")
            import traceback
            traceback.print_exc()
            return False
            
    except ImportError:
        print("[INFO] chromadb 未安装，跳过此测试")
        return None
    except Exception as e:
        print(f"❌ ChromaDB 兼容性测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_system_info():
    """显示系统信息"""
    print_section("系统信息")
    
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"架构: {platform.machine()}")
    print(f"Python 版本: {sys.version}")
    print(f"Python 可执行文件: {sys.executable}")
    
    # 检查是否为 Mac
    if platform.system() == "Darwin":
        print(f"✓ 检测到 macOS")
        mac_version = platform.mac_ver()[0]
        print(f"  macOS 版本: {mac_version}")
    
    # 检查 Python 版本
    python_version = sys.version_info
    print(f"Python 版本详情: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major == 3 and python_version.minor == 10:
        print("[WARNING] 检测到 Python 3.10，可能存在 SQLite3 兼容性问题")

def main():
    """主测试函数"""
    print("\n" + "=" * 70)
    print("  SQLite3 兼容性测试")
    print("=" * 70)
    
    # 显示系统信息
    test_system_info()
    
    # 运行测试
    results = []
    
    # 测试 1: 基本 SQLite3
    results.append(("基本 SQLite3", test_basic_sqlite3()))
    
    # 测试 2: 兼容性模块
    results.append(("兼容性模块", test_compat_module()))
    
    # 测试 3: pysqlite3
    pysqlite3_result = test_pysqlite3()
    if pysqlite3_result is not None:
        results.append(("pysqlite3-binary", pysqlite3_result))
    
    # 测试 4: ChromaDB
    chromadb_result = test_chromadb_compatibility()
    if chromadb_result is not None:
        results.append(("ChromaDB 兼容性", chromadb_result))
    
    # 汇总结果
    print_section("测试结果汇总")
    
    all_passed = True
    for test_name, result in results:
        status = "✓ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result is False:
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("[SUCCESS] 所有测试通过！SQLite3 兼容性正常")
    else:
        print("[WARNING] 部分测试失败，请检查上面的错误信息")
        print("\n建议:")
        print("1. 如果 SQLite3 版本过旧，运行: pip install pysqlite3-binary")
        print("2. 如果 ChromaDB 测试失败，检查 SQLite3 版本是否 >= 3.35")
        print("3. 查看详细错误信息并参考 docs/MACBOOK_SETUP.md")
    print("=" * 70 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

