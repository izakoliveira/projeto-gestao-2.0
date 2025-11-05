# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['instalador_sistema.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('projeto_arquivos', 'projeto_arquivos'),
        ('sgp_icon.ico', '.'),  # Incluir ícone
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'threading',
        'webbrowser',
        'urllib.request',
        'zipfile',
        'tempfile',
        'pathlib',
        'subprocess',
        'shutil',
        'json',
    ],
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
    name='Instalador_Sistema_Gestao',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Janela gráfica (sem console)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='sgp_icon.ico',  # Ícone do instalador
)
