from typing import BinaryIO

from common import FileComponent, ParseError, readSize
from file.read import readComponent

class Container(FileComponent):
    def __init__(self):
        self.primaryID = b""
        self.size = 0
        self.runSize = 0
        self.elements: list[FileComponent] = []

    def read(self, file: BinaryIO) -> None:
        self.primaryID = file.read(4)
        self.size = readSize(file)
        self.runSize = readSize(file)

        end = file.tell() + self.runSize
        while file.tell() < end:
            self.elements.append(readComponent(file))
        if file.tell() != end: raise ParseError("Container did not end at predicted offset")
        if any(b != 0x00 for b in file.read(4)): raise ParseError("Container end flag is not all 0")

        self.verify()

    def verify(self) -> None:
        if self.size != self.runSize + 8: raise ParseError(f"Inconsistent container sizes: {self.size} and {self.runSize}")
