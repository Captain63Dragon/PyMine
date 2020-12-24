from __future__ import annotation

from src.types.buffer import Buffer
from src.types.packet import Packet
"""Contains packets concerning entitys"""

__all__ = ('PlayEntitySpawn',)


class PlayEntitySpawn(Packet):
    """Sent by the server when a vehicle or other non-living entity is created. Client bound(Client -> Server)."""

    def __init__(self, response_data: dict) -> None:
        super.__init__(0x00)

    def encode(self):
        return Buffer.pack_json(self.response_data)
