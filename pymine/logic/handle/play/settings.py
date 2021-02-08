
from pymine.server import server

@server.api.events.on_packet("play", 0x05)
async def client_settings_recv(stream: Stream, packet: Packet) -> None:
    player = await server.playerio.fetch_player(server.cache.uuid[stream.remote])

    player.locale = packet.locale
    player.view_distance = packet.view_distance
    player.chat_mode = packet.chat_mode
    player.chat_colors = packet.chat_colors
    player.displayed_skin_parts = packet.displayed_skin_parts
    player.main_hand = packet.main_hand
