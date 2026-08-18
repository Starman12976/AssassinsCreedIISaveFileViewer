from typing import BinaryIO

from common import FileComponent, ParseError, readSize

class Record(FileComponent):
    def __init__(self):
        self.length = 0
        self.primaryID = b""
        self.secondaryID = b""
        self.tag = b""
        self.payload = b""

    def read(self, file: BinaryIO) -> None:
        self.length = readSize(file)
        if self.length < 13: raise ParseError(f"Record length {self.length} is too small")

        self.primaryID = file.read(4)
        self.secondaryID = file.read(6)
        self.tag = file.read(3)
        self.payload = file.read(self.length - 13)

        self.verify()

    def verify(self) -> None:
        if self.tag[2] != 0x0B: raise ParseError(f"Invalid tag: {self.tag}")
