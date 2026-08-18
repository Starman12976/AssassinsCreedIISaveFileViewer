from typing import BinaryIO

from common import FileComponent, readSize, ParseError
from structs.container import Container

payloadTags = [b"\x1D\x0A\x0B", b"\x9D\x0A\x0B", b"\x1D\x0B\x0B"]

class Composite(FileComponent):
    def __init__(self):
        self.length = 0
        self.primaryID = b""
        self.secondaryID = b""
        self.tag = b""
        self.flag = b""
        self.count = 0
        self.children: list[Container] = []

    def read(self, file: BinaryIO) -> None:
        self.length = readSize(file)
        if self.length < 18: raise ParseError(f"Composite length is too small: {self.length}")

        end = file.tell() + self.length
        self.primaryID = file.read(4)
        self.secondaryID = file.read(6)
        self.tag = file.read(3)

        if self.tag in payloadTags:
            self.flag = file.read(1)
            self.count = readSize(file)
        else:
            self.flag = b""
            self.count = 0

        while file.tell() < end:
            pos = file.tell()
            byte = file.read(1)
            while byte == b"\x00" and file.tell() < end:
                pos = file.tell()
                byte = file.read(1)
            if file.tell() >= end: break
            file.seek(pos)

            child = Container()
            child.read(file)
            self.children.append(child)
        if file.tell() != end: raise ParseError(f"Composite size is incorrect")

        self.verify()

    def verify(self) -> None:
        if self.tag[2] != 0x0B: raise ParseError(f"Invalid tag: {self.tag}")
        if self.flag and self.flag not in [b"\x00", b"\x01"]: raise ParseError(f"Invalid composite flag: {self.flag}")
