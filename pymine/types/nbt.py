from __future__ import annotations

import struct


class TAG:
    """Base class for an NBT tag."""


class TAG_End(TAG):
    """Used to represent a TAG_End, signifies the end of a TAG_Compound."""

    def __init__(self) -> None:
        super().__init__()

    def encode(self) -> bytes:
        return b"\x00"

    @classmethod
    def from_buf(cls, buf) -> TAG_End:
        assert buf.read(1) == b"\x00"
        return cls()


class TAG_Byte(TAG):  # 1
    """Used to represent a TAG_Byte, stores a single signed byte.

    :param int value: A signed byte.
    :attr value:
    """

    def __init__(self, value: int) -> None:
        super().__init__()

        self.value = value

    def encode(self) -> bytes:
        return self.pack("b", self.value)

    @classmethod
    def from_buf(cls, buf) -> TAG_Byte:
        return cls(buf.unpack("b"))


class TAG_Short(TAG):  # 2
    """Used to represent a TAG_Short, stores a single short (2 byte int).

    :param int value: A short (number).
    :attr value:
    """

    def __init__(self, value: int) -> None:
        super().__init__()

        self.value = value

    def encode(self) -> bytes:
        return self.pack("h", self.value)

    @classmethod
    def from_buf(cls, buf) -> TAG_Short:
        return cls(buf.unpack("h"))


class TAG_Int(TAG):  # 3
    """Used to represent a TAG_Int, stores a single integer (4 bytes).

    :param int value: An integer.
    :attr value:
    """

    def __init__(self, value: int) -> None:
        self.value = value

    def encode(self) -> bytes:
        return self.pack("i", self.value)

    @classmethod
    def from_buf(cls, buf) -> TAG_Int:
        return cls(buf.unpack("i"))


class TAG_Long(TAG):  # 4
    """Used to represent a TAG_Long, stores a long long (8 byte integer).

    :param int value: A long long (number).
    :attr value:
    """

    def __init__(self, value: int) -> None:
        self.value = value

    def encode(self) -> bytes:
        return self.pack("q", self.value)

    @classmethod
    def from_buf(cls, buf) -> TAG_Long:
        return cls(buf.unpack("q"))


class TAG_Float(TAG):  # 5
    """Used to represent a TAG_Float, stores a float (4 bytes).

    :param float value: A float (number).
    :attr value:
    """

    def __init__(self, value: float) -> None:
        self.value = value

    def from_buf(self) -> bytes:
        return self.pack('f', self.value)

    @classmethod
    def from_buf(cls, buf) -> TAG_Float:
        return cls(buf.unpack('f'))


class TAG_Double(TAG):  # 6
    """Used to represent a TAG_Double, stores a double (8 byte float).

    :param float value: A double (number).
    :attr value:
    """

    def __init__(self, value: float) -> None:
        self.value = value

    def encode(self) -> bytes:
        return self.pack('d', self.value)

    @classmethod
    def from_buf(cls, buf) -> TAG_Double:
        return cls(buf.unpack('d'))


class TAG_Byte_Array(TAG, bytearray):  # 7
    """Used to represent a TAG_Byte_Array, stores an array of bytes."""

    def __init__(self, value: bytes) -> None:
        bytearray.__init__(self, value)

    def encode(self) -> bytes:
        return self.pack('i', len(self)) + bytes(self)

    @classmethod
    def from_buf(cls, buf) -> TAG_Byte_Array:
        return cls(buf.unpack_array('b', buf.unpack('i')))
