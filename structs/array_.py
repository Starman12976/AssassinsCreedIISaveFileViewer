from typing import BinaryIO

from common import FileComponent, ParseError, readSize

class Array(FileComponent):
    def __init__(self):
        self.size = 0
        self.primaryID = b""
        self.secondaryID = b""
        self.tag = b""
        self.flag = b""
        self.count = 0
        self.values: list[bytes] = []

    def read(self, file: BinaryIO) -> None:
        self.size = readSize(file)
        end = file.tell() + self.size
        self.primaryID = file.read(4)
        self.secondaryID = file.read(6)
        self.tag = file.read(3)
        self.flag = file.read(1)
        self.count = readSize(file)

        for _ in range(self.count):
            self.values.append(file.read(4))
        if file.tell() != end: raise ParseError("Incorrect array size")

        self.verify()

    def verify(self) -> None:
        if self.flag not in [b"\x00", b"\x01"]: raise ParseError(f"Invalid flag: {self.flag}")
        if self.tag[2] != 0x0B: raise ParseError(f"Invalid tag: {self.tag}")
