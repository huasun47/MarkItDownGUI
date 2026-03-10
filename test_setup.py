#!/usr/bin/env python3
"""
测试脚本 - 验证MarkItDown GUI的所有组件是否正常工作
"""
import sys
import os

print("=== MarkItDown GUI 测试 ===")
print(f"Python 版本: {sys.version}")
print(f"当前工作目录: {os.getcwd()}")

# 测试PyQt导入
print("\n1. 测试PyQt导入...")
try:
    if 'gui_app' in sys.modules:
        import gui_app
        PYQT_VERSION = gui_app.PYQT_VERSION
    else:
        # 直接测试
        try:
            from PyQt6.QtWidgets import QApplication
            PYQT_VERSION = 6
        except ImportError:
            from PyQt5.QtWidgets import QApplication
            PYQT_VERSION = 5
    
    print(f"✓ PyQt{PYQT_VERSION} 导入成功")
except ImportError as e:
    print(f"✗ PyQt导入失败: {e}")
    sys.exit(1)

# 测试markitdown导入
print("\n2. 测试MarkItDown导入...")
try:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "markitdown"))
    from markitdown import MarkItDown
    print("✓ MarkItDown 导入成功")
except ImportError as e:
    print(f"✗ MarkItDown导入失败: {e}")

# 测试关键依赖
print("\n3. 测试关键依赖...")
dependencies = [
    "beautifulsoup4",
    "requests", 
    "markdownify",
    "pandas",
    "lxml"
]

for dep in dependencies:
    try:
        if dep == "beautifulsoup4":
            import bs4
        else:
            __import__(dep.replace('-', '_'))
        print(f"✓ {dep} 可用")
    except ImportError:
        print(f"✗ {dep} 不可用")

# 测试GUI应用初始化（不显示窗口）
print("\n4. 测试GUI应用初始化...")
try:
    if PYQT_VERSION == 6:
        from PyQt6.QtWidgets import QApplication
    else:
        from PyQt5.QtWidgets import QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # 测试导入主窗口类
    import gui_app
    window = gui_app.MainWindow()
    print("✓ GUI应用初始化成功")
    
    # 清理
    window.close()
    app.quit()
except Exception as e:
    print(f"✗ GUI应用初始化失败: {e}")

print("\n=== 测试完成 ===")
print("如果所有测试都通过，你可以运行 'uv run python gui_app.py' 启动应用程序")
