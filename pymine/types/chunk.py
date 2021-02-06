from __future__ import annotations

import numpy

from pymine.types.buffer import Buffer
import pymine.types.nbt as nbt

from pymine.data.registries import BLOCK_REGISTRY
from pymine.data.block_states import BLOCK_STATES


class Chunk(nbt.TAG_Compound):
    def __init__(self, tag: nbt.TAG_Compound, timestamp: int) -> None:
        super().__init__("Level", tag["Level"].data)

        self.data_version = tag["DataVersion"]

        self.chunk_x = self["xPos"].data
        self.chunk_z = self["zPos"].data

        self.timestamp = timestamp

    @classmethod
    def new(cls, chunk_x: int, chunk_z: int, timestamp: int) -> Chunk:
        return cls(cls.new_nbt(chunk_x, chunk_z), timestamp)

    @staticmethod
    def new_nbt(chunk_x: int, chunk_z: int) -> nbt.TAG_Compound:
        return nbt.TAG_Compound(
            "",
            [
                nbt.TAG_Int("DataVersion", 2586),
                nbt.TAG_Compound(
                    "Level",
                    [
                        nbt.TAG_Int_Array("Biomes", []),
                        nbt.TAG_Compound("CarvingMasks", [nbt.TAG_Byte_Array("AIR", []), nbt.TAG_Byte_Array("LIQUID", [])]),
                        nbt.TAG_List("Entities", []),
                        nbt.TAG_Compound(
                            "Heightmaps",
                            [
                                nbt.TAG_Long_Array("MOTION_BLOCKING", []),
                                nbt.TAG_Long_Array("MOTION_BLOCKING_NO_LEAVES", []),
                                nbt.TAG_Long_Array("OCEAN_FLOOR", []),
                                nbt.TAG_Long_Array("OCEAN_FLOOR_WG", []),
                                nbt.TAG_Long_Array("WORLD_SURFACE", []),
                                nbt.TAG_Long_Array("WORLD_SURFACE_WG", []),
                            ],
                        ),
                    ],
                ),
                nbt.TAG_Long("LastUpdate", 0),
                nbt.TAG_List("Lights", [nbt.TAG_List(None, []) for _ in range(16)]),
                nbt.TAG_List("LiquidsToBeTicked", [nbt.TAG_List(None, []) for _ in range(16)]),
                nbt.TAG_List("LiquidTicks", []),
                nbt.TAG_Long("InhabitedTime", 0),
                nbt.TAG_List("PostProcessing", [nbt.TAG_List(None, []) for _ in range(16)]),
                nbt.TAG_List("Sections", []),
                nbt.TAG_String("Status", "empty"),
                nbt.TAG_List("TileEntities", []),
                nbt.TAG_List("TileTicks", []),
                nbt.TAG_List("ToBeTicked", [nbt.TAG_List(None, []) for _ in range(16)]),
                nbt.TAG_Compound("Structures", [nbt.TAG_Compound("References", []), nbt.TAG_Compound("Starts")]),
                nbt.TAG_Int("xPos", chunk_x),
                nbt.TAG_iNT("zPos", chunk_z),
            ],
        )

    @classmethod
    def write_chunk_section(buf: Buffer, chunk_section: list) -> None:  # 0..16[0..16[0..16[]]]
        buf.write(Buffer.pack("b", math.log2()))

    @classmethod
    def write_chunk_data_packet(cls, buf: Buffer, cx: int, cz: int, chunk: list) -> None:  # (16, 256, 16)?
        CHUNK_HEIGHT = 256
        SECTION_HEIGHT = 16
        SECTION_WIDTH = 16

        # write chunk coordinates and say that it's a full chunk
        buf.write(Buffer.pack("i", cx) + Buffer.pack("i", cz) + Buffer.pack("?", True))

        mask = 0
        column_buffer = Buffer()

        for i, chunk_section in enumerate(chunk):  # iterate through chunk sections
            if any(chunk_section):  # check if chunk section is empty or not
                mask |= 1 << i
                cls.write_chunk_section(buf, chunk_section)
