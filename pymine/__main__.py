from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit import PromptSession
import asyncio
import sys
import os

# ensure the pymine modules are accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pymine.util.logging import Logger, task_exception_handler
import pymine.server

if __name__ == "__main__":
    prompt_ses = PromptSession(auto_suggest=AutoSuggestFromHistory())
    logger = Logger(prompt_ses)  # debug status will be set later after config is loaded

    loop = asyncio.get_event_loop()
    loop.set_exception_handler(task_exception_handler)

    server = pymine.server.Server(prompt_ses, logger)
    pymine.server.server = server

    try:
        loop.run_until_complete(server.start())
    except asyncio.CancelledError:
        pass
    except BaseException as e:
        logger.critical(logger.f_traceback(e))

    try:
        loop.run_until_complete(server.stop())
    except BaseException as e:
        logger.critical(logger.f_traceback(e))

    loop.stop()
    loop.close()
