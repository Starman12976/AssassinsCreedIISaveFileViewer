from typing import BinaryIO

from common import FileComponent, ParseError, readSize

class Header(FileComponent):
    def __init__(self):
        self.length = 548
        self.unknownField = b""
        self.checksum = b""
        self.slot = b""

    def read(self, file: BinaryIO) -> None:
        self.length = readSize(file)
        self.unknownField = file.read(4)
        self.checksum = file.read(32)
        self.slot = file.read(12)
        if any(b != 0x00 for b in file.read(500)): raise ParseError("Header padding is not all 0")

        self.verify()

    def verify(self) -> None:
        if self.length != 548: raise ParseError(f"Incorrect header size: {self.length}")
        if self.unknownField != b"\x00\x00\x00\x00": raise ParseError(f"Unknown header value is not 0")
        if self.slot not in [b"A\x00C\x00I\x00I\x00 \x00" + x + b"\x00" for x in [b"0", b"1", b"2"]]:
            raise ParseError(f"Invalid save string: {self.slot}")
