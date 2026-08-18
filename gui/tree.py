from PyQt6.QtCore import Qt, QSortFilterProxyModel, QSize
from PyQt6.QtWidgets import QTreeView, QHeaderView, QAbstractItemView, QWidget, QLineEdit, QVBoxLayout, \
    QStyledItemDelegate

from gui.model import FileModel
from structs.save import Save

class PaddedDelegate(QStyledItemDelegate):
    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setHeight(size.height() + 8)
        return size

class FileTree(QTreeView):
    def __init__(self):
        super().__init__()
        header = self.header()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)
        self.minColWidth = 70
        self.cellPadding = 18
        header.setMinimumSectionSize(self.minColWidth)

        self.setAlternatingRowColors(True)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setIndentation(12)
        self.setItemDelegate(PaddedDelegate(self))
        self.header().setStyleSheet("""
        QHeaderView::section { padding: 6px; border: none;
                               border-bottom: 1px solid palette(mid); }
        """)
        self.setUniformRowHeights(True)
        self.setAnimated(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setTextElideMode(Qt.TextElideMode.ElideMiddle)
        self.setIconSize(QSize(16, 16))
        self.fileModel = FileModel()

        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.fileModel)
        self.proxy.setRecursiveFilteringEnabled(True)
        self.proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy.setFilterKeyColumn(-1)
        self.setModel(self.proxy)

    def setFilter(self, text: str) -> None:
        self.proxy.setFilterFixedString(text)
        if text:
            self.expandAll()
        else:
            self.collapseAll()

    def fitName(self) -> None:
        self.resizeColumnToContents(0)

    def populate(self, save: Save):
        self.fileModel.populate(save)
        self.expandAll()

        for col in range(self.fileModel.columnCount()):
            self.resizeColumnToContents(col)
            self.setColumnWidth(col, self.columnWidth(col) + self.cellPadding)
        self.collapseAll()

class FilePanel(QWidget):
    def __init__(self):
        super().__init__()
        self.tree = FileTree()

        self.filterBox = QLineEdit()
        self.filterBox.setPlaceholderText("Filter... (Ctrl+F)")
        self.filterBox.setClearButtonEnabled(True)
        self.filterBox.textChanged.connect(self.tree.setFilter)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)
        layout.addWidget(self.filterBox)
        layout.addWidget(self.tree)

    def populate(self, save: Save) -> None:
        self.filterBox.clear()
        self.tree.populate(save)
