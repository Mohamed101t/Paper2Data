from pathlib import Path
import sys

from PyInstaller.utils.hooks import collect_submodules


ROOT = Path(SPECPATH).parent
TRANSLATIONS = ROOT / "presentation" / "translations"
RESOURCES = ROOT / "presentation" / "resources"
ICON = RESOURCES / "app_icon.ico"
VERSION_FILE = ROOT / "release" / "version_info.txt"


datas = []
for code in ("ar", "fr", "ru", "zh"):
    qm_file = TRANSLATIONS / f"paper2data_{code}.qm"
    if not qm_file.is_file():
        raise FileNotFoundError(
            f"Missing {qm_file}. Run scripts/build_translations.py before PyInstaller."
        )
    datas.append((str(qm_file), "presentation/translations"))

if RESOURCES.is_dir():
    datas.append((str(RESOURCES), "presentation/resources"))


def find_runtime_dll(name: str) -> Path:
    """Find Conda/Python runtime DLLs that PyInstaller may not resolve by PATH."""
    search_roots = (
        Path(sys.prefix) / "Library" / "bin",
        Path(sys.prefix) / "DLLs",
        Path(sys.prefix),
    )

    wanted = name.lower()
    for search_root in search_roots:
        if not search_root.is_dir():
            continue

        direct = search_root / name
        if direct.is_file():
            return direct

        for candidate in search_root.glob("*.dll"):
            if candidate.name.lower() == wanted:
                return candidate

    raise FileNotFoundError(
        f"Required runtime DLL '{name}' was not found under Python environment {sys.prefix}"
    )


# Conda keeps these shared dependencies under Library/bin. When Python is
# launched by absolute path rather than `conda activate`, that directory is
# not necessarily on PATH during PyInstaller dependency analysis.
REQUIRED_RUNTIME_DLLS = (
    "liblzma.dll",
    "LIBBZ2.dll",
    "libmpdec-4.dll",
    "ffi.dll",
    "libexpat.dll",
    "sqlite3.dll",
)

binaries = [(str(find_runtime_dll(name)), ".") for name in REQUIRED_RUNTIME_DLLS]
hiddenimports = collect_submodules("openpyxl")


a = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "pandas", "matplotlib", "IPython", "tkinter"],
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Paper2Data",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ICON) if ICON.is_file() else None,
    version=str(VERSION_FILE),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="Paper2Data",
)
