from __future__ import annotations

from src.types.packet import Packet
from src.types.buffer import Buffer
from src.types.chat import Chat

__all__ = ('PlayPlayerListHeaderAndFooter',)


class PlayPlayerListHeaderAndFooter(Packet):
    """yep"""

    id = 0x53
    to = 1

    def __init__(self, header: Chat, footer: Chat) -> None:
        super().__init__()

        self.header, self.footer = header, footer

    def encode(self) -> bytes:
        return Buffer.pack_chat(self.header) + Buffer.pack_chat(self.footer)
