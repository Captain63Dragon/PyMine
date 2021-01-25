from __future__ import annotations

import struct


class TAG:
    """Base class for an NBT tag.

    :attr int id: The type ID of the tag, see here: https://wiki.vg/NBT.
    """

    id: int = -1

    def __init__(self) -> None:
        self.id = self.__class__.id

    @staticmethod
    def pack(f: str, *data: object) -> bytes:
        return struct.pack(">" + f, *data)

    @staticmethod
    def unpack(f: str, buf) -> object:
        unpacked = struct.unpack(">" + f, buf.read(struct.calcsize(f)))

        if len(unpacked) == 1:
            return unpacked[0]

        return unpacked


class TAG_End(TAG):
    """Used to represent a TAG_End, signifies the end of a TAG_Compound.

    :attr int id: The type ID of the tag, see here: https://wiki.vg/NBT.
    """

    id = 0

    def __init__(self) -> None:
        super().__init__()

    def encode(self) -> bytes:
        return b"\x00"

    @classmethod
    def decode(cls, buf) -> TAG_End:
        assert buf.read(1) == b"\x00"
        return cls()


class TAG_Byte(TAG):
    """Used to represent a TAG_Byte, stores a single signed byte.

    :param int value: A signed byte.
    :attr int id: The type ID of the tag, see here: https://wiki.vg/NBT.
    :attr value:
    """

    id = 1

    def __init__(self, value: int) -> None:
        super().__init__()

        self.value = value

    def encode(self) -> bytes:
        return self.pack("b", self.value)

    @classmethod
    def decode(cls, buf) -> TAG_Byte:
        return cls(buf.read(1))
