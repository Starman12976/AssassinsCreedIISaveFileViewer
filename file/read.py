from typing import BinaryIO

from common import readSize, FileComponent

def readComponent(file: BinaryIO) -> FileComponent:
    from structs.array_ import Array
    from structs.composite import Composite
    from structs.record import Record

    offset = file.tell()
    size = readSize(file)
    file.read(10)
    tag = file.read(3)
    file.read(1)
    count = readSize(file)

    if size >= 18 and count != 0 and size - 18 == 4 * count:
        file.seek(offset)
        array = Array()
        array.read(file)
        return array

    if ((tag in [b"\x1D\x0A\x0B", b"\x9D\x0A\x0B", b"\x1D\x0B\x0B"] and size > 18)
        or (tag in [b"\x13\x00\x0B", b"\x16\x00\x0B"] and size > 13)):
        file.seek(offset)
        composite = Composite()
        composite.read(file)
        return composite

    file.seek(offset)
    record = Record()
    record.read(file)
    return record
