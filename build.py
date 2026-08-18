from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

from file.version import __version__

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
BUILD = ROOT / "build"
APP = "AC2SaveFileViewer"

def run(*args: str) -> int:
    print("+", " ".join(args))
    return subprocess.call(args)

def main() -> int:
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller is not installed")
        return 1

    iconPath = ROOT / "data" / "icon.ico"
    if not iconPath.exists():
        print(f"note: {iconPath.relative_to(ROOT)} not found - building without an "
              f"icon (add one there to embed it)")

    for folder in (DIST, BUILD):
        if folder.exists():
            shutil.rmtree(folder)

    code = run(sys.executable, "-m", "PyInstaller", "--noconfirm", f"{APP}.spec")
    if code != 0:
        print(f"\nPyInstaller failed (exit {code}). The real error is in the output"
              f" above - look for a line starting with ERROR.")
        return code

    payload = DIST / APP
    if not payload.is_dir():
        print(f"expected {payload} to exist after the build")
        return 1

    for extra in ("readme.md", "README.md", "license", "LICENSE"):
        source = ROOT / extra
        if source.exists():
            shutil.copy2(source, payload / extra)

    platform = "windows" if sys.platform == "win32" else sys.platform
    archive = DIST / f"{APP}-{__version__}-{platform}.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(payload.rglob("*")):
            if path.is_file():
                bundle.write(path, Path(APP) / path.relative_to(payload))

    size = archive.stat().st_size
    print(f"\nBuilt {archive.name}  ({size:,} bytes)")
    binary = f"{APP}.exe" if sys.platform == "win32" else APP
    print(f"Unzip it and run {APP}/{binary}")
    return 0

if __name__ == "__main__":
    sys.exit(main())