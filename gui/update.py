from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.request

from PyQt6.QtCore import QObject, QThread, pyqtSignal

from file.paths import userDataDir
from file.version import __version__, GITHUB_OWNER, GITHUB_REPO

RELEASES_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
DEFINITIONS_URL = (f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}"
                   f"/master/data/definitions.json")
TIMEOUT = 8

def parseVersion(text: str) -> tuple:
    cleaned = text.strip().lstrip("vV").split("-")[0].split("+")[0]
    parts = []

    for piece in cleaned.split("."):
        try:
            parts.append(int(piece))
        except ValueError:
            parts.append(0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])

def isNewer(latest: str, current: str = __version__) -> bool:
    return parseVersion(latest) > parseVersion(current)

def _fetch(url: str) -> bytes:
    request = urllib.request.Request(
        url, headers={"Accept": "application/vnd.github+json",
                      "User-Agent": f"AC2SaveFileViewer/{__version__}"})
    context = ssl.create_default_context()
    with urllib.request.urlopen(request, timeout=TIMEOUT, context=context) as response:
        return response.read()

class UpdateWorker(QObject):
    finished = pyqtSignal()
    updateFound = pyqtSignal(str, str, str)
    upToDate = pyqtSignal()
    definitionsUpdated = pyqtSignal(int)
    failed = pyqtSignal(str)

    def __init__(self, includeDefinitions: bool = True):
        super().__init__()
        self.includeDefinitions = includeDefinitions

    def run(self) -> None:
        try:
            release = json.loads(_fetch(RELEASES_URL).decode("utf-8"))
            tag = str(release.get("tag_name", ""))
            if tag and isNewer(tag):
                self.updateFound.emit(tag,
                                      release.get("html_url", ""),
                                      (release.get("body") or "").strip())
            else:
                self.upToDate.emit()
        except (urllib.error.URLError, json.JSONDecodeError, OSError, ValueError) as error:
            self.failed.emit(str(error))
            self.finished.emit()
            return

        if self.includeDefinitions:
            try:
                raw = _fetch(DEFINITIONS_URL)
                blob = json.loads(raw.decode("utf-8"))     # validate before writing
                target = userDataDir() / "definitions.json"
                existing = -1
                if target.exists():
                    try:
                        existing = json.loads(target.read_text("utf-8")).get("version", -1)
                    except (OSError, json.JSONDecodeError):
                        existing = -1
                if blob.get("version", 0) > existing:
                    target.write_text(json.dumps(blob, indent=2), encoding="utf-8")
                    self.definitionsUpdated.emit(len(blob.get("primaryIDs", {})))
            except (urllib.error.URLError, json.JSONDecodeError, OSError, ValueError):
                pass                                        # definitions are optional

        self.finished.emit()


class UpdateChecker(QObject):
    updateFound = pyqtSignal(str, str, str)
    upToDate = pyqtSignal()
    definitionsUpdated = pyqtSignal(int)
    failed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.thread: QThread | None = None
        self.worker: UpdateWorker | None = None

    def start(self, includeDefinitions: bool = True) -> None:
        if self.thread is not None:
            return                                          # already running
        self.thread = QThread()
        self.worker = UpdateWorker(includeDefinitions)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.updateFound.connect(self.updateFound)
        self.worker.upToDate.connect(self.upToDate)
        self.worker.definitionsUpdated.connect(self.definitionsUpdated)
        self.worker.failed.connect(self.failed)
        self.worker.finished.connect(self._cleanup)
        self.thread.start()

    def _cleanup(self) -> None:
        if self.thread is not None:
            self.thread.quit()
            self.thread.wait(2000)
        self.thread = None
        self.worker = None
