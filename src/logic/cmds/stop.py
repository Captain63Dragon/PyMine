from src.util.commands import command


@command(name='stop')
async def stop_server(uuid: str, cmd: str):
    share['server'].close()
