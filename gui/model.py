from PyQt6.QtCore import Qt, QModelIndex
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QApplication, QStyle

import common
from structs.array_ import Array
from structs.composite import Composite
from structs.container import Container
from structs.record import Record
from structs.save import Save

labels = ["Name", "Type", "Size", "Tag", "Value"]

class FileModel(QStandardItemModel):
    def __init__(self):
        super().__init__()
        self.setHorizontalHeaderLabels(labels)
        self.setColumnCount(len(labels))

        style = QApplication.style()
        self.folderIcon = style.standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        self.leafIcon = style.standardIcon(QStyle.StandardPixmap.SP_FileIcon)

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return super().data(index, role)

        if role == Qt.ItemDataRole.DecorationRole and index.column() == 0:
            item = self.itemFromIndex(index)
            if item is None:
                return None
            return self.folderIcon if item.hasChildren() else self.leafIcon

        return super().data(index, role)

    def nodeCount(self, parent=QModelIndex()) -> int:
        total = self.rowCount(parent)
        for row in range(self.rowCount(parent)):
            total += self.nodeCount(self.index(row, 0, parent))
        return total

    @staticmethod
    def createRecord(parent: QStandardItem, record: Record) -> None:
        recordItem: QStandardItem
        if record.primaryID in common.primaryIDs.keys():
            recordItem = QStandardItem(common.primaryIDs[record.primaryID])
        else:
            recordItem = QStandardItem(record.primaryID.hex().upper())
        recordType = QStandardItem("record")
        recordSize = QStandardItem(str(record.length))
        recordTag: QStandardItem
        recordValue: QStandardItem
        if record.tag in common.tags.keys():
            recordTag = QStandardItem(common.tags[record.tag])
            recordValue = QStandardItem(str(common.decodeTag(record.tag, record.payload)))
        else:
            recordTag = QStandardItem(record.tag.hex().upper())
            recordValue = QStandardItem(record.payload.hex().upper())
        parent.appendRow([recordItem, recordType, recordSize, recordTag, recordValue])

    @staticmethod
    def createArray(parent: QStandardItem, array: Array):
        arrayItem: QStandardItem
        if array.primaryID in common.primaryIDs.keys():
            arrayItem = QStandardItem(common.primaryIDs[array.primaryID])
        else:
            arrayItem = QStandardItem(array.primaryID.hex().upper())
        arrayType = QStandardItem("array")
        arraySize = QStandardItem(str(array.size))
        for value in array.values:
            valueItem: QStandardItem
            if value in common.arrayItems.keys():
                valueItem = QStandardItem(common.arrayItems[value])
            else:
                valueItem = QStandardItem(value.hex().upper())
            valueType = QStandardItem("array value")
            valueSize = QStandardItem("4")
            arrayItem.appendRow([valueItem, valueType, valueSize, QStandardItem(), QStandardItem()])
        parent.appendRow([arrayItem, arrayType, arraySize, QStandardItem(), QStandardItem()])

    def createContainer(self, parent: QStandardItem, container: Container):
        containerItem: QStandardItem
        if container.primaryID in common.primaryIDs.keys():
            containerItem = QStandardItem(common.primaryIDs[container.primaryID])
        else:
            containerItem = QStandardItem(container.primaryID.hex().upper())
        containerType = QStandardItem("container")
        containerSize = QStandardItem(str(container.size))
        for child in container.elements:
            if isinstance(child, Record):
                self.createRecord(containerItem, child)
            elif isinstance(child, Array):
                self.createArray(containerItem, child)
            else:
                self.createComposite(containerItem, child)
        parent.appendRow([containerItem, containerType, containerSize, QStandardItem(), QStandardItem()])

    def createComposite(self, parent: QStandardItem, composite: Composite):
        compositeItem: QStandardItem
        if composite.primaryID in common.primaryIDs.keys():
            compositeItem = QStandardItem(common.primaryIDs[composite.primaryID])
        else:
            compositeItem = QStandardItem(composite.primaryID.hex().upper())
        compositeType = QStandardItem("composite")
        compositeSize = QStandardItem(str(composite.length))
        for container in composite.children:
            self.createContainer(compositeItem, container)
        parent.appendRow([compositeItem, compositeType, compositeSize, QStandardItem(), QStandardItem()])

    def populate(self, save: Save):
        self.clear()
        self.setColumnCount(len(labels))
        self.setHorizontalHeaderLabels(labels)
        rootItem = self.invisibleRootItem()

        header = QStandardItem("Header")
        headerType = QStandardItem("header")
        headerSize = QStandardItem(str(save.header.length))
        rootItem.appendRow([header, headerType, headerSize, QStandardItem(), QStandardItem()])

        checksum = QStandardItem("Checksum")
        checksumType = QStandardItem("string")
        checksumSize = QStandardItem("32")
        checksumStr = save.header.checksum.decode("ascii")
        checksumValue = QStandardItem(checksumStr if any(c != "\x00" for c in checksumStr) else "none")
        header.appendRow([checksum, checksumType, checksumSize, QStandardItem(), checksumValue])

        slot = QStandardItem("Save slot")
        slotType = QStandardItem("string")
        slotSize = QStandardItem("12")
        slotValue = QStandardItem(save.header.slot.decode("utf-16-le"))
        header.appendRow([slot, slotType, slotSize, QStandardItem(), slotValue])

        rootRecord = QStandardItem("Root Record")
        rootRecordType = QStandardItem("root record")
        rootRecordSize = QStandardItem("17")
        rootItem.appendRow([rootRecord, rootRecordType, rootRecordSize, QStandardItem(), QStandardItem()])

        self.createContainer(rootItem, save.root)
