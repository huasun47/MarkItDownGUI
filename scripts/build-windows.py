#!/usr/bin/env python3
"""
Windows 构建脚本 - 使用 PyInstaller 打包 MarkItDown GUI
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """运行命令并显示输出"""
    print(f"运行命令: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    
    if result.stdout:
        print(f"输出:\n{result.stdout}")
    if result.stderr:
        print(f"错误:\n{result.stderr}")
    
    if result.returncode != 0:
        print(f"命令失败，返回码: {result.returncode}")
        return False
    
    return True

def main():
    """主构建函数"""
    project_root = Path(__file__).parent.parent
    scripts_dir = project_root / "scripts"
    dist_dir = project_root / "dist"
    
    print(f"项目根目录: {project_root}")
    print(f"脚本目录: {scripts_dir}")
    print(f"输出目录: {dist_dir}")
    
    # 检查 PyInstaller 是否安装
    print("检查 PyInstaller...")
    if not run_command("pyinstaller --version"):
        print("安装 PyInstaller...")
        if not run_command("pip install pyinstaller"):
            print("PyInstaller 安装失败")
            return False
    
    # 清理之前的构建
    print("清理之前的构建...")
    build_dir = project_root / "build"
    if build_dir.exists():
        shutil.rmtree(build_dir)
        print("已删除 build 目录")
    
    # 清理 dist 目录中的内容（保留目录）
    if dist_dir.exists():
        for item in dist_dir.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        print("已清理 dist 目录")
    
    # 运行 PyInstaller
    spec_file = scripts_dir / "MarkItDownGUI-windows.spec"
    if not spec_file.exists():
        print(f"找不到 spec 文件: {spec_file}")
        return False
    
    print("开始 PyInstaller 打包...")
    cmd = f'pyinstaller "{spec_file}"'
    
    if not run_command(cmd, cwd=project_root):
        print("PyInstaller 打包失败")
        return False
    
    # 检查输出
    exe_file = dist_dir / "MarkItDownGUI.exe"
    if exe_file.exists():
        print(f"✅ 构建成功! 可执行文件位于: {exe_file}")
        print(f"文件大小: {exe_file.stat().st_size / (1024*1024):.1f} MB")
        
        # 显示 dist 目录内容
        print("\ndist 目录内容:")
        for item in dist_dir.iterdir():
            if item.is_file():
                size = item.stat().st_size / (1024*1024)
                print(f"  📄 {item.name} ({size:.1f} MB)")
            else:
                print(f"  📁 {item.name}/")
        
        return True
    else:
        print("❌ 构建失败，找不到可执行文件")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
