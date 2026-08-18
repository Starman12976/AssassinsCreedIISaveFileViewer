import os.path
import sys

from PyQt6.QtCore import QSettings, Qt, QUrl
from PyQt6.QtGui import QKeySequence, QAction, QDesktopServices
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QLabel, QStackedWidget, \
    QStyle, QToolBar

import common
from common import ParseError
from gui.update import UpdateChecker
from file.version import __version__
from gui.tree import FilePanel
from structs.save import Save

class FileViewWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.appTitle = "Assassin's Creed II: Save File Viewer"
        self.setWindowTitle(self.appTitle)
        self.resize(800, 600)
        self.settings = QSettings()

        self.placeholder = QLabel("Open a save file to begin\n\nCtrl+O")
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setStyleSheet(
            "color: palette(mid); font-size: 15pt;"
        )

        self.panel = FilePanel()

        self.stack = QStackedWidget()
        self.stack.addWidget(self.placeholder)
        self.stack.addWidget(self.panel)
        self.setCentralWidget(self.stack)

        openIcon = self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton)
        self.openAction = QAction(openIcon, "Open...", self)
        self.openAction.setShortcut(QKeySequence.StandardKey.Open)
        self.openAction.triggered.connect(self.openFile)

        self.fileMenu = self.menuBar().addMenu("File")
        self.fileMenu.addAction(self.openAction)

        toolbar = QToolBar("Main")
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        toolbar.addAction(self.openAction)
        self.addToolBar(toolbar)

        self.helpMenu = self.menuBar().addMenu("Help")
        self.updateAction = QAction("Check for updates", self)
        self.updateAction.triggered.connect(lambda: self.checkForUpdates(quiet=False))
        self.helpMenu.addAction(self.updateAction)
        self.aboutAction = QAction("About", self)
        self.aboutAction.triggered.connect(self.showAbout)
        self.helpMenu.addAction(self.aboutAction)

        self.statusBar().showMessage("No file loaded")

        self.updater = UpdateChecker(self)
        self.updater.updateFound.connect(self.onUpdateFound)
        self.updater.upToDate.connect(self.onUpToDate)
        self.updater.definitionsUpdated.connect(self.onDefinitionsUpdated)
        self.updater.failed.connect(self.onUpdateFailed)
        self.quietCheck = True

        findAction = QAction(self)
        findAction.setShortcut(QKeySequence.StandardKey.Find)
        findAction.triggered.connect(self.panel.filterBox.setFocus)
        self.addAction(findAction)

    def checkForUpdates(self, quiet: bool = True) -> None:
        self.quietCheck = quiet
        if not quiet:
            self.statusBar().showMessage("Checking for updates...")
        self.updater.start()

    def onUpdateFound(self, tag: str, url: str, notes: str) -> None:
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Information)
        box.setWindowTitle("Update available")
        box.setText(f"Version {tag} is available.\n\nYou are running {__version__}.")
        if notes:
            box.setDetailedText(notes)
        openButton = box.addButton("Open download page", QMessageBox.ButtonRole.AcceptRole)
        box.addButton("Later", QMessageBox.ButtonRole.RejectRole)
        box.exec()
        if box.clickedButton() is openButton and url:
            QDesktopServices.openUrl(QUrl(url))

    def onUpToDate(self) -> None:
        if not self.quietCheck:
            QMessageBox.information(self, "Up to date",
                                    f"You are running the latest version ({__version__}).")
        self.statusBar().clearMessage()

    def onDefinitionsUpdated(self, count: int) -> None:
        common.reloadDefinitions()
        self.statusBar().showMessage(
            f"Definitions updated ({count} named ids) - reopen a file to apply", 8000)

    def onUpdateFailed(self, message: str) -> None:
        if not self.quietCheck:
            QMessageBox.warning(self, "Couldn't check for updates", message)
        self.statusBar().clearMessage()

    def showAbout(self) -> None:
        QMessageBox.about(
            self, "About",
            f"<b>{self.appTitle}</b><br>Version {__version__}<br><br>"
            f"Reads Assassin's Creed II save files and shows their structure.")

    def openFile(self) -> None:
        lastDir = self.settings.value("lastDir", "", type=str)

        filePath, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption="Open Save File",
            directory=lastDir,
            filter="Save Files (*.save);;All Files (*)"
        )
        if not filePath:
            return
        if not os.path.exists(filePath):
            QMessageBox.warning(self, "File not found", f"{filePath} no longer exists")
            return

        self.settings.setValue("lastDir", os.path.dirname(filePath))

        try:
            with open(filePath, "rb") as saveFile:
                saveStruct = Save(saveFile)
        except ParseError as e:
            QMessageBox.critical(
                self,
                "Couldn't open file",
                f"{os.path.basename(filePath)} isn't a valid save file\n\n{e}"
            )
            return
        except OSError as e:
            QMessageBox.critical(self, "Couldn't read file", str(e))
            return

        self.panel.populate(saveStruct)
        self.stack.setCurrentWidget(self.panel)
        self.showLoaded(filePath)

    def showLoaded(self, filePath: str) -> None:
        name = os.path.basename(filePath)
        size = os.path.getsize(filePath)
        nodes = self.panel.tree.fileModel.nodeCount()

        self.setWindowTitle(f"{name} - {self.appTitle}")
        self.statusBar().showMessage(f"{name}  ·  {size:,} bytes  ·  {nodes:,} entries")

def openWindow() -> int:
    app = QApplication(sys.argv)
    app.setOrganizationName("AssassinsForge")
    app.setApplicationName("AC2SaveViewer")

    window = FileViewWindow()
    window.show()

    return app.exec()
