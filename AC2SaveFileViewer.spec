import os

iconPath = os.path.join("data", "icon.ico")
appIcon = iconPath if os.path.exists(iconPath) else None

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[("data/definitions.json", "data")],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        "tkinter", "matplotlib", "numpy",
        "PyQt6.QtWebEngineCore", "PyQt6.QtWebEngineWidgets", "PyQt6.QtQml",
        "PyQt6.QtQuick", "PyQt6.QtMultimedia", "PyQt6.Qt3DCore",
        "PyQt6.QtBluetooth", "PyQt6.QtNetworkAuth", "PyQt6.QtPositioning",
        "PyQt6.QtSensors", "PyQt6.QtSerialPort", "PyQt6.QtSql", "PyQt6.QtTest",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="AC2SaveFileViewer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=appIcon,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="AC2SaveFileViewer",
)
