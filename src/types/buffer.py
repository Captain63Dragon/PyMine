from __future__ import annotations
import struct
import json
import zlib

class Buffer:
    """
    Base class for a buffer, contains methods
    for handling most basic types and for
    converting from/to a Buffer object itself.
    """

    def __init__(self, buf: bytes = None):
        self.buf = b'' if buf is None else buf
        self.pos = 0

    def add(self, data: bytes):
        """Add data to the buffer."""

        self.buf += data

    def read(self, length: int = None) -> bytes:
        """
        Read data from the buffer, if the length is None
        then all remaining data from the buffer is sent.
        """

        try:
            if length is None:
                length = len(self.buf)
                return self.buf[self.pos:]
            else:
                return self.buf[self.pos:self.pos+length]
        finally:
            self.pos += length

    def reset(self) -> None:
        """Reset the position in the buffer."""

        self.pos = 0

    @classmethod
    def pack_array(cls, f: str, array: list) -> bytes:
        """Pack an array/list into bytes."""

        return struct.pack(f'>{f*len(array)}', *array)

    def unpack_array(self, f: str, length: int) -> list:
        """Unpack an array/list from the buffer."""

        data = self.read(struct.calcsize(f'>{f}') * length)
        return list(struct.unpack(f'>{f*length}', data))

    @classmethod
    def pack_bool(cls, boolean) -> bytes:
        """Pack a boolean into bytes."""

        return struct.pack(f'>?', boolean)

    def unpack_bool(self) -> bool:
        """Unpack a boolean from the buffer."""

        return struct.unpack(f'>?', self.read(1))

    @classmethod
    def pack_varint(cls, num: int, max_bits: int = 32) -> bytes:
        """Pack a varint (Varying Integer) into bytes."""

        num_min, num_max = (-1 << (max_bits - 1)), (+1 << (max_bits - 1))

        if not (num_min <= num < num_max):
            raise ValueError(
                f'num doesn\'t fit in given range: {num_min} <= {num} < {num_max}')

        if num < 0:
            num += 1 + 1 << 32

        out = b''

        for i in range(10):
            b = num & 0x7F
            num >>= 7

            out += struct.pack('>B', (b | (0x80 if num > 0 else 0)))

            if num == 0:
                break

        return out

    def unpack_varint(self, max_bits: int = 32) -> int:
        """Unpack a varint from the buffer."""

        num = 0

        for i in range(10):
            b = struct.unpack(f'>B', self.read(1))
            num |= (b & 0x7F) << (7 * i)

            if not b & 0x80:
                break

        if num & (1 << 31):
            num -= 1 << 32

        num_min, num_max = (-1 << (max_bits - 1)), (+1 << (max_bits - 1))

        if not (num_min <= num < num_max):
            raise ValueError(f'num doesn\'t fit in given range: {num_min} <= {num} < {num_max}')

        return num

    @classmethod
    def from_bytes(cls, data: bytes, comp_thresh: int = -1) -> Buffer:
        """
        Converts bytes into a Buffer object, handles compression
        and length prefixing
        """

        buf = cls(data)
        buf = cls(buf.read(buf.unpack_varint()))  # Handle length prefixing

        # Handle if the data was compressed
        if comp_thresh >= 0:
            uncomp_len = buf.unpack_varint()  # Handle decompressed length prefixing

            if uncomp_len > 0:
                buf = cls(zlib.decompress(buf.read()))  # Create new Buffer from decompressed data

        return buf

    def to_bytes(self, comp_thresh: int = -1) -> bytes:
        """
        Packs the final Buffer into bytes, readies the data to be sent,
        handles compression and length prefixing.
        """

        if comp_thresh >= 0:
            if len(self.buf) >= comp_thresh:
                data = self.pack_varint(len(self.buf)) + zlib.compress(self.buf)
            else:
                data = self.pack_varint(0) + self.buf
        else:
            data = self.buf

        return self.pack_varint(len(data), max_bits=32) + data

    @classmethod
    def pack_string(cls, text: str) -> bytes:
        """Packs a string into bytes."""

        text = text.encode('utf-8')
        return cls.pack_varint(len(text), max_bits=16) + text

    def unpack_string(self) -> str:
        """Unpacks a string from the buffer."""

        length = self.unpack_varint(max_bits=16)
        return self.read(length).decode('utf-8')

    @classmethod
    def pack_json(cls, obj: object) -> bytes:
        """Packs json serializable data into bytes."""

        return cls.pack_string(json.dumps(obj))

    def unpack_json(self) -> object:
        """Unpacks serialized json data from the buffer."""

        return json.loads(self.unpack_string())
