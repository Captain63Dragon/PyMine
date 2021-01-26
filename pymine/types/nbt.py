from __future__ import annotations

from mutf8 import encode_modified_utf8, decode_modified_utf8
import gzip

from pymine.types.buffer import Buffer

TYPES = []


def from_buf(buf: Buffer) -> TAG_Compound:
    try:
        buf = Buffer(gzip.decompress(buf.read()))
    except BaseException:
        pass

    return TAG_Compound.from_buf(buf)


class TAG:
    """Base class for an NBT tag.

    :param str name: The name of the TAG.
    :attr int id: The type ID.
    :attr name
    """

    id = None

    def __init__(self, name: str = None) -> None:
        self.id = self.__class__.id
        self.name = name

    def encode_meta(self) -> bytes:
        mutf8_name = encode_modified_utf8(self.name)
        return Buffer.pack("b", self.id) + Buffer.pack("H", len(mutf8_name)) + mutf8_name

    @staticmethod
    def meta_from_buf(buf: Buffer) -> tuple:  # returns the type id and name
        return buf.unpack("b"), decode_modified_utf8(buf.read(buf.unpack("H")))

    def encode_value(self) -> bytes:
        raise NotImplementedError

    def encode(self) -> bytes:
        return self.encode_meta() + self.encode_value()

    @staticmethod
    def value_from_buf(buf: Buffer) -> NotImplemented:
        raise NotImplementedError

    @classmethod
    def from_buf(cls, buf: Buffer):
        return cls(cls.meta_from_buf(buf)[1], cls.value_from_buf(buf))

    def pretty(self, obj: object = None, i: int = 0):
        if obj is None:
            obj = self

        t = "  " * i

        if isinstance(obj, TAG):
            return f"{t}{type(obj).__name__}({obj.name})[\n{self.pretty(obj.value, i+1)}\n{t}]"
        elif isinstance(obj, list):
            return f",\n{t}".join([self.pretty(val, i + 1) for val in obj])
        else:
            return f"{t}{obj}"


class TAG_End(TAG):
    """Used to represent a TAG_End, signifies the end of a TAG_Compound."""

    id = 0

    # tag is nameless and valueless, consists of just \x00
    def __init__(self) -> None:
        super().__init__()

    def encode_meta(self) -> bytes:
        return b''

    @staticmethod
    def meta_from_buf(buf: Buffer) -> tuple:  # returns the type id and name
        return 0, None

    def encode_value(self) -> bytes:
        return b"\x00"

    def encode(self) -> bytes:
        return self.encode_value()

    @staticmethod
    def value_from_buf(buf: Buffer) -> TAG_End:
        assert buf.unpack("b") == b"\x00"
        return b'\x00'

    @classmethod
    def from_buf(cls, buf: Buffer):
        self.value_from_buf(buf)
        return cls()


class TAG_Byte(TAG):
    """Used to represent a TAG_Byte, stores a single signed byte.

    :param str name: The name of the TAG.
    :param int value: A signed byte.
    :int id: The type ID of the TAG.
    :attr value:
    """

    id = 1

    def __init__(self, name: str, value: int) -> None:
        super().__init__(name)

        self.value = value

    def encode_value(self) -> bytes:
        return Buffer.pack("b", self.value)

    @staticmethod
    def value_from_buf(buf: Buffer) -> int:
        return buf.unpack("b")


class TAG_Short(TAG):
    """Used to represent a TAG_Short, stores a single short (2 byte int).

    :param str name: The name of the TAG.
    :param int value: A short (2 byte int).
    :int id: The type ID of the TAG.
    :attr value:
    """

    id = 2

    def __init__(self, name: str, value: int) -> None:
        super().__init__(name)

        self.value = value

    def encode_value(self) -> bytes:
        return Buffer.pack("h", self.value)

    @staticmethod
    def value_from_buf(buf: Buffer) -> int:
        return buf.unpack("h")


class TAG_Int(TAG):
    """Used to represent a TAG_Int, stores an integer (4 bytes).

    :param str name: The name of the TAG.
    :param int value: A int (4 bytes).
    :int id: The type ID of the TAG.
    :attr value:
    """

    id = 3

    def __init__(self, name: str, value: int) -> None:
        super().__init__(name)

        self.value = value

    def encode_value(self) -> bytes:
        return Buffer.pack("i", self.value)

    @staticmethod
    def value_from_buf(buf: Buffer) -> int:
        return buf.unpack("i")


class TAG_Long(TAG):
    """Used to represent a TAG_Long, stores a long long (8 byte int).

    :param str name: The name of the TAG.
    :param int value: A long long (8 byte int).
    :int id: The type ID of the TAG.
    :attr value:
    """

    id = 4

    def __init__(self, name: str, value: int) -> None:
        super().__init__(name)

        self.value = value

    def encode_value(self) -> bytes:
        return Buffer.pack("q", self.value)

    @staticmethod
    def value_from_buf(buf: Buffer) -> int:
        return buf.unpack("q")


class TAG_Float(TAG):
    """Used to represent a TAG_Float, stores a float (4 bytes).

    :param str name: The name of the TAG.
    :param float value: A float (4 bytes).
    :int id: The type ID of the TAG.
    :attr value:
    """

    id = 5

    def __init__(self, name: str, value: float) -> None:
        super().__init__(name)

        self.value = value

    def encode_value(self) -> bytes:
        return Buffer.pack("f", self.value)

    @staticmethod
    def value_from_buf(buf: Buffer) -> float:
        return buf.unpack("f")


class TAG_Double(TAG):
    """Used to represent a TAG_Double, stores a double (8 byte float).

    :param str name: The name of the TAG.
    :param float value: A double (8 byte float).
    :int id: The type ID of the TAG.
    :attr value:
    """

    id = 6

    def __init__(self, name: str, value: float) -> None:
        super().__init__(name)

        self.value = value

    def encode_value(self) -> bytes:
        return Buffer.pack("d", self.value)

    @staticmethod
    def value_from_buf(buf: Buffer) -> float:
        return buf.unpack("d")


class TAG_Byte_Array(TAG):
    """Used to represent a TAG_Byte_Array, stores an array of bytes.

    :param str name: The name of the TAG.
    :param bytes value: Some bytes.
    :int id: The type ID of the TAG.
    :attr value:
    """

    id = 7

    def __init__(self, name: str, value: bytes) -> None:
        super().__init__(name)

        self.value = bytearray(value)

    def encode_value(self) -> bytes:
        return Buffer.pack("i", len(self.value)) + Buffer.pack_array("b", self.value)

    @staticmethod
    def value_from_buf(buf: Buffer) -> bytearray:
        return bytearray(buf.unpack_array("b", buf.unpack("i")))


class TAG_String(TAG):
    """Used to represent a TAG_String, stores a string.

    :param str name: The name of the TAG.
    :param str value: A string.
    :int id: The type ID of the TAG.
    :attr value:
    """

    id = 8

    def __init__(self, name: str, value: str) -> None:
        super().__init__(name)

        self.value = value

    def encode_value(self) -> bytes:
        mutf8_text = encode_modified_utf8(self.value)
        return Buffer.pack("H", len(mutf8_text)) + mutf8_text

    @staticmethod
    def value_from_buf(buf: Buffer) -> str:
        return decode_modified_utf8(buf.read(buf.unpack("H")))


class TAG_List(TAG):
    """Represents a TAG_List, a list of nameless and typeless tagss.

    :param str name: The name of the TAG.
    :param list value: A uniform list of TAGs.
    :int id: The type ID of the TAG.
    :attr value:
    """

    id = 9

    def __init__(self, name: str, value: list) -> None:
        super().__init__(name)

        self.value = value

    def encode_value(self) -> bytes:
        return (
            Buffer.pack("b", self.value[0].id)
            + Buffer.pack("i", len(self.value))
            + b"".join([value.encode_value() for value in self.value])
        )

    @staticmethod
    def value_from_buf(buf: Buffer) -> list:
        tag_type = TYPES[buf.unpack("b")]
        return [tag_type(None, tag_type.value_from_buf(buf)) for _ in range(buf.unpack("i"))]


class TAG_Compound(TAG):
    """Represents a TAG_Compound, a list of named tags.

    :param str name: The name of the TAG.
    :param list value: A list of tags.
    :int id: The type ID of the TAG.
    :attr value:
    """

    id = 10

    def __init__(self, name: str, value: list) -> None:
        super().__init__(name)

        self.value = value

    def encode_value(self) -> bytes:
        return b"".join([tag.encode() for tag in self.value]) + b"\x00"

    @staticmethod
    def value_from_buf(buf: Buffer) -> list:
        out = []

        while True:
            tag = TYPES[buf.buf[buf.pos]]

            if tag == TAG_End:
                break

            out.append(tag.from_buf(buf))

        return out


class TAG_Int_Array(TAG):
    """Represents a TAG_Int_Array, a list of ints (4 bytes each).

    :param str name: The name of the TAG.
    :param list value: A list of ints (4 bytes each).
    :int id: The type ID of the TAG.
    :attr value:
    """

    id = 11

    def __init__(self, name: str, value: list) -> None:
        super().__init__(name)

        self.value = value

    def encode_value(self) -> bytes:
        return Buffer.pack("i", len(self.value)) + b"".join([Buffer.pack("i", num) for num in self.value])

    @staticmethod
    def value_from_buf(buf: Buffer) -> list:
        return [buf.unpack("i") for _ in range(buf.unpack("i"))]


class TAG_Long_Array(TAG):
    """Represents a TAG_Long_Array, a list of long longs (8 byte ints).

    :param str name: The name of the TAG.
    :param list value: A list of long longs (8 byte ints).
    :int id: The type ID of the TAG.
    :attr value:
    """

    id = 12

    def __init__(self, name: str, value: list) -> None:
        super().__init__(name)

        self.value = value

    def encode_value(self) -> bytes:
        return Buffer.pack("i", len(self.value)) + b"".join([Buffer.pack("q", num) for num in self.value])

    @staticmethod
    def value_from_buf(buf: Buffer) -> list:
        return [buf.unpack("q") for _ in range(buf.unpack("i"))]


TYPES.extend(
    [
        TAG_End,
        TAG_Byte,
        TAG_Short,
        TAG_Int,
        TAG_Long,
        TAG_Float,
        TAG_Double,
        TAG_Byte_Array,
        TAG_String,
        TAG_List,
        TAG_Compound,
        TAG_Int_Array,
        TAG_Long_Array,
    ]
)
