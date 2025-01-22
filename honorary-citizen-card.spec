# -*- mode: python ; coding: utf-8 -*-
import sys
import os
import glob
from PyInstaller.utils.hooks import collect_all, collect_submodules, collect_data_files

block_cipher = None

# Get base directory and src paths
BASE_DIR = os.path.abspath('.')
SRC_DIR = os.path.join(BASE_DIR, 'src')
RESOURCES_DIR = os.path.join(BASE_DIR, 'resources')
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Add src to path
sys.path.append(SRC_DIR)

# PyQt6 관련 데이터/바이너리 수집
pyqt6_data = collect_data_files('PyQt6')

# 데이터 파일 설정 (resources 제외)
datas = [
    (os.path.join(SRC_DIR, 'app.py'), '.'),
    (os.path.join(SRC_DIR, 'config.py'), '.'),
    (os.path.join(SRC_DIR, 'main.py'), '.'),
    (os.path.join(SRC_DIR, 'screens', '*.py'), 'screens'),
    (os.path.join(SRC_DIR, 'utils', '*.py'), 'utils'),
]

if os.path.exists(RESOURCES_DIR):
    # PNG files
    png_files = glob.glob(os.path.join(RESOURCES_DIR, '*.png'))
    for png_file in png_files:
        datas.append((png_file, 'resources'))
    
    # Style files
    styles_dir = os.path.join(RESOURCES_DIR, 'styles')
    if os.path.exists(styles_dir):
        qss_files = glob.glob(os.path.join(styles_dir, '*.qss'))
        for qss_file in qss_files:
            datas.append((qss_file, 'resources/styles'))
    
    # Test image
    test_img = os.path.join(RESOURCES_DIR, 'test_img.jpg')
    if os.path.exists(test_img):
        datas.append((test_img, 'resources'))


# Add data directory if it exists
if os.path.exists(DATA_DIR):
    datas.append((DATA_DIR, 'data'))

# Add PyQt6 data
datas.extend(pyqt6_data)

# Hidden imports
hidden_imports = [
    'PIL',
    'PIL._tkinter_finder',
    'PIL.Image',
    'PIL.ImageTk',
    'cv2',
    'numpy',
    'PyQt6',
    'PyQt6.QtWidgets',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.sip',
    'openpyxl',
    'pandas',
    'pandas.io.excel._base',
    'pandas.io.excel._openpyxl'
]

# OpenCV 바이너리 수집
binaries = []
try:
    import cv2
    cv2_path = os.path.dirname(cv2.__file__)
    cv2_dlls = [(os.path.join(cv2_path, file), '.') 
                for file in os.listdir(cv2_path) 
                if file.endswith(('.pyd', '.dll', '.so'))]
    binaries.extend(cv2_dlls)
except Exception as e:
    print(f"Error collecting OpenCV binaries: {e}")

try:
    from PyQt6 import QtCore
    from PyQt6.QtCore import QLibraryInfo
    import sys
    
    if getattr(sys, 'frozen', False):
        qt_plugin_path = os.path.join(sys._MEIPASS, "PyQt6/Qt6/plugins")
        QApplication.addLibraryPath(qt_plugin_path)
    
    qt_base_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.PluginsPath)
    
    # Platform plugin (중요: 이 부분이 핵심)
    binaries.append((os.path.join(qt_base_path, 'platforms/qwindows.dll'), 'platforms'))
    
    # Style plugins
    styles_dir = os.path.join(qt_base_path, 'styles')
    if os.path.exists(styles_dir):
        for style_file in glob.glob(os.path.join(styles_dir, '*.dll')):
            binaries.append((style_file, 'styles'))
    
    # Image format plugins
    imageformats_dir = os.path.join(qt_base_path, 'imageformats')
    if os.path.exists(imageformats_dir):
        for image_file in glob.glob(os.path.join(imageformats_dir, '*.dll')):
            binaries.append((image_file, 'imageformats'))
            
    # Platform Themes
    platformthemes_dir = os.path.join(qt_base_path, 'platformthemes')
    if os.path.exists(platformthemes_dir):
        for theme_file in glob.glob(os.path.join(platformthemes_dir, '*.dll')):
            binaries.append((theme_file, 'platformthemes'))
    
except Exception as e:
    print(f"Error collecting PyQt6 plugins: {e}")

# Main Analysis
a = Analysis(
    [os.path.join(SRC_DIR, 'main.py')],
    pathex=[BASE_DIR, SRC_DIR],
    binaries=binaries,
    datas=datas,  # resources 제외한 데이터
    hiddenimports=hidden_imports,
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
    [],
    exclude_binaries=True,
    name='honorary_citizen_card',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(RESOURCES_DIR, 'app_icon.ico') if os.path.exists(os.path.join(RESOURCES_DIR, 'app_icon.ico')) else None
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='honorary_citizen_card'
)