from src.logic.status import status as server_func_status
from src.data.states import *
from src.types.buffer import Buffer
from src.types.packet import Packet
from src.data.server_properties import *
from src.data.packet_map import PACKET_MAP
import immutables
import logging
import asyncio
import base64
import sys
import os
# import uvloop

sys.path.append(os.getcwd())


global share
share = {
    'version': '1.16.4'
}

try:  # Load server.properties
    with open('server.properties', 'r+') as f:
        lines = f.readlines()

        share['PROPERTIES'] = dict(SERVER_PROPERTIES)
        share['PROPERTIES'].update(parse_properties(lines))
        share['PROPERTIES'] = immutables.Map(PROPERTIES)
except Exception:
    with open('server.properties', 'w+') as f:
        f.write(SERVER_PROPERTIES_BLANK)

    share['PROPERTIES'] = SERVER_PROPERTIES

try:  # Load favicon
    with open('server-icon.png', 'rb') as favicon:
        share['favicon'] = 'data:image/png;base64,' + \
            base64.b64encode(favicon.read()).decode('utf-8')
except Exception:
    share['favicon'] = None

states = {}  # {remote_address: state_id}
share['states'] = states

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def handle_con(r, w):
    remote = w.get_extra_info('peername')  # (host, port)
    logger.info(f'Connection received from {remote[0]}:{remote[1]}')

    read = await r.read(1)  # Read first byte

    if read == b'\xFE':  # Legacy ping
        raise NotImplemented

    # Varint can be no longer than 5 bytes, so first 5 bytes are pretty much guaranteed
    read += await r.read(4)
    buf.write(await r.read(Buffer(read).unpack_varint()))  # Read the rest of the packet

    state = STATES_BY_ID[states.get(remote, 0)]
    packet = buf.unpack_packet(state, PACKET_MAP)

    if state == 'status':
        if packet.id_ == 0x00:  # StatusStatusRequest
            await server_func_status(r, w, packet)


async def start():
    port = 69
    server = await asyncio.start_server(handle_con, port=port)

    try:
        async with server:
            print(f'Server started on port {port}')
            await server.serve_forever()
    except KeyboardInterrupt:
        pass

# uvloop.install()
asyncio.run(start())
