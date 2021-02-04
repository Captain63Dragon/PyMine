"""Contains packets related to bosses."""

from __future__ import annotations
import uuid

from pymine.types.packet import Packet
from pymine.types.buffer import Buffer
from pymine.types.chat import Chat

__all__ = ("PlayBossBar",)


class PlayBossBar(Packet):
    """Used to send boss bar data. (Server -> Client)

    :param uuid.UUID uuid: UUID of the boss bar.
    :param int action: Action to take.
    :param type **data: Data corresponding to the action.
    :ivar type data: Data corresponding to the action.
    :ivar int id: Unique packet ID.
    :ivar int to: Packet direction.
    :ivar uuid:
    :ivar action:
    """

    id = 0x0C
    to = 1

    def __init__(self, uuid: uuid.UUID, action: int, **data: dict) -> None:
        super().__init__()

        self.uuid = uuid
        self.action = action
        self.data = data

    def encode(self) -> bytes:  # See here for data: https://wiki.vg/Protocol#Boss_Bar
        out = Buffer.pack_uuid(self.uuid) + Buffer.pack_varint(self.action)

        if self.action == 0:
            out += (
                Buffer.pack_chat(self.data["title"])
                + Buffer.pack("f", self.data["health"])
                + Buffer.pack_varint(self.data["color"])
                + Buffer.pack_varint(self.data["division"])
                + Buffer.pack("B", self.data["flags"])
            )
        elif self.action == 2:
            out += Buffer.pack("f", self.data["health"])
        elif self.action == 3:
            out += Buffer.pack_chat(self.data["title"])
        elif self.action == 4:
            out += Buffer.pack_varint(self.data["color"]) + Buffer.pack_varint(self.data["division"])
        elif self.action == 5:
            out += Buffer.pack("B", self.data["flags"])

        return out
