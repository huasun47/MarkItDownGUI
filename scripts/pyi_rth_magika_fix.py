"""
PyInstaller 运行时钩子 - 修复 magika 路径问题
"""

import sys
import os
from pathlib import Path

def fix_magika_paths():
    """修复 magika 在打包环境中的路径问题"""
    
    if not getattr(sys, 'frozen', False):
        return  # 只在打包环境中运行
    
    # 获取 PyInstaller 临时目录
    meipass = sys._MEIPASS
    
    # 修复 magika 模块中的路径
    try:
        import magika
        
        # 获取 magika 模块路径
        magika_module_path = Path(magika.__file__).parent
        
        # 在打包环境中，magika 应该位于 meipass/magika
        packaged_magika_path = Path(meipass) / 'magika'
        
        if packaged_magika_path.exists():
            # 修复 magika 模块中的路径引用
            original_init_file = magika_module_path / '__init__.py'
            
            # 创建路径修复函数
            def get_packaged_path(original_path):
                """将原始路径转换为打包后的路径"""
                try:
                    # 如果原始路径是 magika 模块下的相对路径
                    if str(magika_module_path) in str(original_path):
                        rel_path = Path(original_path).relative_to(magika_module_path)
                        return str(packaged_magika_path / rel_path)
                except:
                    pass
                return original_path
            
            # 修补 magika 的路径查找
            if hasattr(magika, 'Magika'):
                original_init = magika.Magika.__init__
                
                def patched_init(self, *args, **kwargs):
                    # 在初始化前修复路径
                    if 'model_path' in kwargs:
                        kwargs['model_path'] = get_packaged_path(kwargs['model_path'])
                    
                    # 调用原始初始化
                    original_init(self, *args, **kwargs)
                    
                    # 修复内部路径
                    if hasattr(self, '_model_path'):
                        self._model_path = get_packaged_path(self._model_path)
                
                magika.Magika.__init__ = patched_init
            
            print("✅ Magika 路径修复完成")
            
    except ImportError:
        print("⚠️ Magika 模块未找到")
    except Exception as e:
        print(f"❌ Magika 路径修复失败: {e}")

# 执行修复
fix_magika_paths()
