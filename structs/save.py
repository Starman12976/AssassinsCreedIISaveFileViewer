from typing import BinaryIO

from structs.body import Body
from common import FileComponent, ParseError
from structs.container import Container
from structs.header import Header

class Save(FileComponent):
    def __init__(self, file: BinaryIO | None = None):
        self.header = Header()
        self.body = Body()
        self.root = Container()

        if file: self.read(file)

    def read(self, file: BinaryIO) -> None:
        file.seek(0)

        self.header.read(file)
        self.body.read(file)
        self.root.read(file)

        if file.tell() != file.seek(0, 2): raise ParseError("File is longer than expected")

        self.verify()

    def verify(self) -> None:
        pass
