import asyncio

from src.logic.commands import on_command, handle_server_commands, load_commands

"""
events/decorators:
    * For each event, there should be a list of handlers so there can be multiple handlers between plugins
    server:
        startup: @on_server_ready
        shutdown: @on_server_stop
    command: @on_command(name='name', node='plugin_name.cmds.cmd_name')
    chat message: @on_message
    incoming packets:
        packet logic: @handle_packet(*id=0x00)
        after packet logic: @after_packet_logic(id=0x00)
    tasks: @task(ticks_per=1 or seconds_per=1, minutes_per=1, hours_per=1)
    players:
        player join: @on_player_join
        player leave: @on_player_leave

utility methods/functions:
    set the motd: set_motd(str or Chat)
    set player list header: set_player_list_header(str or Chat)
    set player list footer: set_player_list_footer(str or Chat)
    send_packet()?

models?
    * player model
    * entity model?
"""

running_tasks = []


async def init():
    load_commands()  # load commands in src/logic/cmds/*

    # start command handler task
    running_tasks.append(asyncio.create_task(handle_server_commands()))


async def stop():
    for task in running_tasks:
        task.cancel()


PACKET_HANDLERS = {'handshaking': [], 'login': [], 'play': [], 'status': []}


def handle_packet(state: str, id_: int):
    def command_deco(func):
        PACKET_HANDLERS[state][id_] = [*PACKET_HANDLERS.get(id_, []), func]

        return func

    return command_deco
