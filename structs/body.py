from typing import BinaryIO

from common import FileComponent, ParseError, readSize

class Body(FileComponent):
    def __init__(self):
        self.length = 0
        self.bodyID = b"\xAC\xDB\xFE\x00"
        self.unknownConstant1 = b"\01"
        self.rootContainerID = b"\x52\x3B\xBE\xBD"
        self.unknownConstant2 = b"\x03\x00\x00\x00"
        self.unknownConstant3 = b"\x00\x00\x00\x00"

    def read(self, file: BinaryIO) -> None:
        self.length = readSize(file)
        self.bodyID = file.read(4)
        self.unknownConstant1 = file.read(1)
        self.rootContainerID = file.read(4)
        self.unknownConstant2 = file.read(4)
        self.unknownConstant3 = file.read(4)
        if any(b != 0x00 for b in file.read(3)): raise ParseError("Body record padding is not all 0")

        self.verify()

    def verify(self) -> None:
        if self.length != 17: raise ParseError(f"Incorrect body record length: {self.length}")
        if self.bodyID != b"\xAC\xDB\xFE\x00": raise ParseError(f"Invalid body ID: {self.bodyID}")
        if self.unknownConstant1 != b"\x01": raise ParseError(f"Invalid unknown constant 1: {self.unknownConstant1}")
        if self.rootContainerID != b"\x52\x3B\xBE\xBD": raise ParseError(f"Invalid root container ID: {self.rootContainerID}")
        if self.unknownConstant2 != b"\x03\x00\x00\x00": raise ParseError(f"Invalid unknown constant 2: {self.unknownConstant2}")
        if self.unknownConstant3 != b"\x00\x00\x00\x00": raise ParseError(f"Invalid unknown constant 3: {self.unknownConstant3}")
