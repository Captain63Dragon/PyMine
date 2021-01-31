from __future__ import annotations
import multiprocessing as mp
import aiofile
import asyncio
import zlib
import os

from pymine.types.buffer import Buffer
from pymine.types.chunk import Chunk
import pymine.types.nbt as nbt


# finds the location of the chunk in the file
def find_chunk_pos_in_buffer(loc: int) -> tuple:
    offset = (loc >> 8) & 0xFFFFFF
    # size = loc & 0xFF

    return offset * 4096  # , size * 4096


def region_coords_from_file(file: str) -> tuple:
    return os.path.split(file)[1].split(".")[1:3]


def unpack_chunk_map(buf: Buffer, q: mp.Queue) -> dict:
    location_table = [buf.unpack("i") for _ in range(1024)]
    timestamp_table = [buf.unpack("i") for _ in range(1024)]

    def unpack_chunk(entry_timestamp) -> tuple:
        entry, timestamp = entry_timestamp

        buf.pos = find_chunk_pos_in_buffer(entry)

        chunk_len = buf.unpack("i")
        buf.read(1)  # comp type, should always be 2 so ignore
        chunk = buf.read(chunk_len)

        chunk = Chunk(nbt.TAG_Compound.unpack(Buffer(zlib.decompress(chunk))), timestamp)
        # we use mod here to convert to chunk coords INSIDE the region
        return (chunk.chunk_x % 32, chunk.chunk_z % 32), chunk

    q.put(dict(map(unpack_chunk, zip(location_table, timestamp_table))))


class Region(dict):
    def __init__(self, chunk_map: dict, region_x: int, region_z: int) -> None:
        dict.__init__(self, chunk_map)

        self.region_x = region_x
        self.region_z = region_z

    @classmethod
    async def from_file(cls, file: str) -> Region:
        async with aiofile.async_open(file, "rb") as region_file:
            buf = Buffer(await region_file.read())

        region_x, region_z = region_coords_from_file(file)

        q = mp.Queue()
        p = mp.Process(target=unpack_chunk_map, args=(buf, q))

        loop = asyncio.get_event_loop()

        await loop.run_in_executor(None, p.start)
        chunk_map = await loop.run_in_executor(None, q.get)
        await loop.run_in_executor(None, p.join)

        return Region(chunk_map, region_x, region_z)
