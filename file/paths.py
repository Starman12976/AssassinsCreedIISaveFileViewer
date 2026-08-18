from pathlib import Path
import sys

def resourceDir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).resolve().parent.parent

def userDataDir() -> Path:
    if sys.platform == "win32":
        import os
        base = Path(os.environ.get("APPDATA", Path.home()))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home() / ".local" / "share"
    folder = base / "AC2SaveFileViewer"
    folder.mkdir(parents=True, exist_ok=True)
    return folder

def definitionsPaths() -> list[Path]:
    return [resourceDir() / "data" / "definitions.json",
            userDataDir() / "definitions.json"]
