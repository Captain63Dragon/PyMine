"""Contains packets relating to chunks."""

from __future__ import annotations
from nbt import nbt

from src.types.packet import Packet
from src.types.buffer import Buffer

__all__ = ('PlayUnloadChunk',)


class PlayUnloadChunk(Packet):
    """Tells the client to unload a chunk column. Clientbound(Server => Client)"""

    id = 0x1C
    to = 1

    def __init__(self, chunk_x: int, chunk_z: int) -> None:
        super().__init__()

        self.chunk_x, self.chunk_z = chunk_x, chunk_z

    def encode(self) -> bytes:
        return Buffer.pack('i', self.chunk_x) + Buffer.pack('i', self.chunk_z)


class PlayChunkData(Packet):
    """Sends chunk data to the client. (Server -> Client)

    :param int chunk_x: The chunk x coordinate (block x coordinate // 16).
    :param int chunk_z: The chunk z coordinate (block z coordinate // 16).
    :param bool full_chunk: Description of parameter `full_chunk`.
    :param int prim_bit_mask: Description of parameter `prim_bit_mask`.
    :param nbt.TAG heightmaps: Compound containing one long array named MOTION_BLOCKING, which is a heightmap for the highest solid block at each position in the chunk (as a compacted long array with 256 entries at 9 bits per entry totaling 36 longs). The Notchian server also adds a WORLD_SURFACE long array, the purpose of which is unknown, but it's not required for the chunk to be accepted.
    :param bytes data: See chunk data format: https://wiki.vg/Chunk_Format#Full_chunk.
    :param list block_entities: Array of nbt.TAGs.
    :param int biomes: Unknown, see here: https://wiki.vg/Protocol#Chunk_Data.
    :attr int id: Unique packet ID.
    :attr int to: Packet direction.
    :attr chunk_x:
    :attr chunk_z:
    :attr full_chunk:
    :attr prim_bit_mask:
    :attr heightmaps:
    :attr data:
    :attr block_entities:
    :attr biomes:
    """

    id = 0x20
    to = 1

    def __init__(self, chunk_x: int, chunk_z: int, full_chunk: bool, prim_bit_mask: int, heightmaps: nbt.TAG, data: bytes, block_entities: list, biomes: int = None) -> None:
        super().__init__()

        self.chunk_x, self.chunk_z = chunk_x, chunk_z
        self.full_chunk = full_chunk
        self.prim_bit_mask = prim_bit_mask
        self.heightmaps = heightmaps
        self.data = data
        self.block_entities = block_entities
        self.biomes = biomes

    def encode(self) -> bytes:
        raise NotImplementedError
