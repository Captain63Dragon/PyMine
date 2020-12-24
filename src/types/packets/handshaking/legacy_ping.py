"""Contains packets that support the legacy server list ping protocol"""

from __future__ import annotations

from src.types.buffer import Buffer
from src.types.packet import Packet

__all__ = ('HandshakeLegacyPing_1', 'HandshakeLegacyPing_2',)


class HandshakeLegacyPingRequest(Packet):
    """Request from the client asking for legacy ping response.

    Client -> Server

    :param int protocol: Protocol version being used, should now always be 74/4a.
    :param str hostname: The host/address the client is connecting to.
    :param int port: The port the client is connection on.
    :attr type id_: Unique packet ID.
    :attr protocol:
    :attr hostname:
    :attr port:
    """

    id_ = 0xFE

    def __init__(self, protocol: int, hostname: str, port: int) -> None:
        super().__init__()

        self.protocol = protocol
        self.hostname = hostname
        self.port = port

    @classmethod
    def decode(cls, buf: Buffer) -> HandshakeLegacyPing_1:
        buf.read(15)
        return cls(buf.read(1), buf.read(buf.unpack('h')).decode('UTF-16BE'), buf.unpack('i'))


class HandshakeLegacyPingResponse(Packet):  # Server -> CLient
    """Response from the server acknowledging and accepting the connection"""

    id_ = 0xFF

    def __init__(self, version: str, motd: str, players_online: int, players_max: int, protocol: int = 127) -> None:
        super().__init__()

        self.protocol = protocol
        self.version = version
        self.motd = motd
        self.players_online = players_online
        self.players_max = players_max

    def encode(self) -> bytes:
        out_string = f'§1\x00{self.protocol}\x00{self.motd}\x00{self.players_online}\x00{self.players_max}'
        return b'\xff' + Buffer.pack('h', len(out_string)) + out_string.encode('UTF-16BE')
