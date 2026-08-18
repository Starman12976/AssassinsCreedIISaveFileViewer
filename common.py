from abc import ABC, abstractmethod
import json
import struct
from typing import Any, BinaryIO

from file.paths import definitionsPaths

def _loadDefinitions() -> tuple[dict, dict, dict]:
    ids: dict[bytes, str] = {}
    tagNames: dict[bytes, str] = {}
    items: dict[bytes, str] = {}
    for path in definitionsPaths():
        try:
            with open(path, "r", encoding="utf-8") as handle:
                blob = json.load(handle)
        except (OSError, json.JSONDecodeError):
            continue
        for key, value in blob.get("primaryIDs", {}).items():
            try: ids[bytes.fromhex(key.replace(" ", ""))] = value
            except ValueError: pass
        for key, value in blob.get("tags", {}).items():
            try: tagNames[bytes.fromhex(key.replace(" ", ""))] = value
            except ValueError: pass
        for key, value in blob.get("arrayItems", {}).items():
            try: items[bytes.fromhex(key.replace(" ", ""))] = value
            except ValueError: pass
    return ids, tagNames, items

primaryIDs, tags, arrayItems = _loadDefinitions()

def reloadDefinitions() -> None:
    global primaryIDs, tags, arrayItems
    primaryIDs, tags, arrayItems = _loadDefinitions()

def name(primaryID: bytes) -> str:
    return primaryIDs.get(primaryID, primaryID.hex().upper())

def tagName(tag: bytes) -> str:
    return tags.get(tag, tag.hex().upper())

def decodeTag(tag: bytes, value: bytes) -> Any:
    if not value:
        return ""
    try:
        if tag in (b"\x07\x00\x0B", b"\x06\x00\x0B", b"\x11\x00\x0B"):
            return int.from_bytes(value, "little", signed=False)
        if tag == b"\x00\x00\x0B":
            return bool(value[0])
        if tag == b"\x03\x00\x0B":
            return value[0]
        if tag == b"\x0A\x00\x0B":
            return round(struct.unpack("<f", value[:4])[0], 6)
        if tag == b"\x12\x00\x0B":
            return value.hex().upper()
        if tag == b"\x19\x00\x0B":
            return (f"{int.from_bytes(value[:4], 'little')} "
                    f"hash {value[4:8].hex().upper()}")
        if tag == b"\x1A\x00\x0B":
            length = int.from_bytes(value[:4], "little")
            return repr(value[4:4 + length].decode("ascii", "replace"))
        if tag in (b"\x1D\x0A\x0B", b"\x1D\x0B\x0B", b"\x9D\x0A\x0B"):
            return (f"flag {value[0]}, "
                    f"value {int.from_bytes(value[1:5], 'little')}")
    except (struct.error, IndexError, UnicodeDecodeError):
        pass
    return value.hex(" ").upper()

def readSize(file: BinaryIO) -> int:
    return struct.unpack("<I", file.read(4))[0]

def readString(file: BinaryIO, size: int) -> str:
    return file.read(size).decode(encoding="ascii")

class ParseError(Exception):
    pass

class FileComponent(ABC):
    @abstractmethod
    def read(self, file: BinaryIO) -> None:
        pass

    @abstractmethod
    def verify(self) -> None:
        pass
