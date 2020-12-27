import importlib
import os

from src.util.immutable import make_immutable

__all__ = ('PACKET_MAP',)


def load_packets():
    packet_map = {}

    for state in os.listdir('src/types/packets'):
        packet_map[state] = {}

        for file in os.listdir(f'src/types/packets/{state}'):
            if file.endswith('.py'):
                module = importlib.import_module(f'src.types.packets.{state}.{file[:-3]}')

                for name in module.__all__:
                    packet = module.__dict__.get(name)
                    if packet.to == 2:
                        packet_map[state][(packet.id_, 0,)] = packet
                        packet_map[state][(packet.id_, 1,)] = packet
                    else:
                        packet_map[state][(packet.id_, packet.to,)] = packet

    return make_immutable(packet_map)


PACKET_MAP = load_packets()
