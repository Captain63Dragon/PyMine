from pymine.server import server


@server.api.on_command(name="stop", node="minecraft.cmd.stop")
def stop_server(uuid: str, args: str):
    share["server"].close()
