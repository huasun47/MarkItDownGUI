# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

def get_magika_models():
    """获取 magika 模型文件和配置文件路径"""
    try:
        import magika
        magika_path = Path(magika.__file__).parent
        
        model_files = []
        
        # 包含整个 magika 目录以确保所有文件都被包含
        if magika_path.exists():
            for file_path in magika_path.rglob('*'):
                if file_path.is_file():
                    rel_path = file_path.relative_to(magika_path)
                    dest_path = str(Path('magika') / rel_path.parent)
                    model_files.append((str(file_path), dest_path))
        
        return model_files
    except ImportError:
        pass
    
    return []

# 获取项目根目录
project_root = Path(SPECPATH).parent
markitdown_path = project_root / "markitdown"

block_cipher = None

a = Analysis(
    [str(project_root / 'gui_app.py')],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        # 包含 assets 目录
        (str(project_root / 'assets'), 'assets'),
        # 包含 markitdown 包
        (str(markitdown_path), 'markitdown'),
        # 包含 magika 模型文件 - 关键修复
        # 获取 magika 模型目录
    ] + get_magika_models(),
    hiddenimports=[
        # PyQt 相关
        'PyQt6.QtCore',
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets',
        'PyQt6.sip',
        # PyQt5 作为备选
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PyQt5.sip',
        # MarkItDown 相关模块
        'markitdown',
        'markitdown._base_converter',
        'markitdown.converters',
        'markitdown.converters._audio_converter',
        'markitdown.converters._bing_serp_converter',
        'markitdown.converters._csv_converter',
        'markitdown.converters._docx_converter',
        'markitdown.converters._epub_converter',
        'markitdown.converters._excel_converter',
        'markitdown.converters._html_converter',
        'markitdown.converters._image_converter',
        'markitdown.converters._json_converter',
        'markitdown.converters._markdown_converter',
        'markitdown.converters._pdf_converter',
        'markitdown.converters._pptx_converter',
        'markitdown.converters._text_converter',
        'markitdown.converters._xml_converter',
        'markitdown.converters._youtube_converter',
        'markitdown.converters._zip_converter',
        'markitdown.converter_utils',
        'markitdown.converter_utils.docx',
        # 第三方库
        'requests',
        'beautifulsoup4',
        'markdownify',
        'magika',
        'charset_normalizer',
        'defusedxml',
        'python_pptx',
        'python_docx',
        'mammoth',
        'pandas',
        'openpyxl',
        'xlrd',
        'lxml',
        'pdfminer',
        'pdfminer.six',
        'olefile',
        'pydub',
        'imageio_ffmpeg',
        'speech_recognition',
        'youtube_transcript_api',
        # 音频处理
        'ffmpeg',
        # 数据处理
        'numpy',
        'PIL',
        'PIL.Image',
        # 网络相关
        'urllib.parse',
        'urllib.request',
        'urllib.error',
        'http.client',
        'ssl',
        # 其他可能需要的模块
        'json',
        'csv',
        'xml.etree.ElementTree',
        'zipfile',
        'io',
        'base64',
        'hashlib',
        'datetime',
        'time',
        'os',
        'sys',
        'pathlib',
        're',
        'typing',
        'collections',
        'itertools',
        'functools',
        'decimal',
        'fractions',
        'statistics',
        'string',
        'textwrap',
        'unicodedata',
        'codecs',
        'encodings',
        'encodings.utf_8',
        'encodings.cp1252',
        'encodings.latin1',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[
        str(project_root / 'scripts' / 'pyi_rth_magika_fix.py')
    ],
    excludes=[
        # 排除不需要的模块以减小体积
        'tkinter',
        'matplotlib',
        'scipy',
        'notebook',
        'jupyter',
        'IPython',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MarkItDownGUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 设置为 False 以隐藏控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_root / 'assets' / 'exec_logo.png'),  # 应用图标
    version='version_info.txt' if os.path.exists('version_info.txt') else None,
)
