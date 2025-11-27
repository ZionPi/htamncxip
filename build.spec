# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# 1. 自动收集复杂库的所有依赖文件 (PaddleOCR, RapidLatexOCR, PyQt6)
# 这步至关重要，否则打包出来的程序会报 ModuleNotFound
datas = []
binaries = []
hiddenimports = []

# 收集 paddleocr
tmp_ret = collect_all('paddleocr')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# 收集 rapid_latex_ocr
tmp_ret = collect_all('rapid_latex_ocr')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# 收集常用依赖
hiddenimports += ['PyQt6', 'PIL', 'cv2', 'numpy', 'keyboard', 'pyclipper', 'shapely', 'skimage']

a = Analysis(
    ['main.py'],             # 程序入口
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='htamncxip',        # 生成的文件名
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,           # False = 不显示黑窗口 (GUI模式)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# MAC OS 专属配置
app = BUNDLE(
    exe,
    name='htamncxip.app',
    icon=None,
    bundle_identifier='com.zp.htamncxip',
)