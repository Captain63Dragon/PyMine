import pkg_resources
import importlib
import asyncio
import zipfile
import time
import yaml
import git
import os

from pymine.util.immutable import make_immutable
from pymine.util.misc import run_in_executor

from pymine.api.commands import CommandHandler
from pymine.api.events import EventHandler


class StopStream(BaseException):
    pass


class PyMineAPI:
    def __init__(self, server):
        self.server = server
        self.logger = server.logger

        self.plugins = {}
        self.tasks = []

        self.events = EventHandler(server)
        self.commands = CommandHandler(server)

    def taskify_handlers(self, handlers: list):
        for handler in handlers:
            try:
                self.tasks.append(asyncio.create_task(handler()))
            except BaseException as e:
                self.logger.error(
                    f"Failed to call handler {handler.__module__}.{handler.__qualname__} due to: {self.logger.f_traceback(e)}"
                )

    def update_repo(self, git_dir, git_url, root, plugin_name, do_clone=False):
        if do_clone:
            try:
                os.rename(root, os.path.join("plugins", f".{plugin_name}_backup_{int(time.time())}"))
                self.logger.warn(f"Backing up and resetting {plugin_name}...")
            except FileNotFoundError as e:
                pass

            self.logger.debug(f"Cloning from {git_url}...")
            git_dir.clone(git_url)
            self.logger.info(f"Updated {plugin_name}!")

            return

        if not os.path.isdir(os.path.join(root, ".git")):
            return self.update_repo(git_dir, git_url, root, plugin_name, True)

        try:
            self.logger.debug(f"Pulling from {git_url}...")
            res = git.Git(root).pull()  # pull latest from remote
        except BaseException as e:
            self.logger.debug(f"Failed to pull from {git_url}, attempting to clone...")
            return self.update_repo(git_dir, git_url, root, plugin_name, True)

        if res == "Already up to date.":
            self.logger.info(f"No updates found for {plugin_name}.")
        else:
            self.logger.info(f"Updated {plugin_name}!")

    @staticmethod
    def load_plugin_config(root):
        plugin_config_file = os.path.join(root, "plugin.yml")

        try:
            with open(plugin_config_file) as conf:
                conf = yaml.safe_load(conf.read())
        except yaml.YAMLError:
            raise ValueError("Failed to parse plugin.yml")

        if not isinstance(conf, dict):
            raise ValueError("plugin.yml must contain a dict")

        if conf.get("git_url") is not None and not isinstance(conf["git_url"], str):
            raise ValueError('Value "git_url" must be of type "str"')

        if conf.get("module_folder") is not None and not isinstance(conf["module_folder"], str):
            raise ValueError('Value "module_folder" must be of type "str"')

        for key, value in conf.items():
            if value == "":
                conf[key] = None

        return conf

    async def load_plugin(self, git_dir, plugin_name):
        if plugin_name.startswith("."):
            return

        root = os.path.join("plugins", plugin_name)

        if os.path.isfile(root):
            if root.endswith(".py"):  # .py file (so try to import)
                try:
                    plugin_path = root.rstrip(".py").replace("\\", "/").replace("/", ".")

                    plugin_module = importlib.import_module(plugin_path)
                    await plugin_module.setup(self.server, None)

                    self.plugins[plugin_path] = plugin_module
                except BaseException as e:
                    self.logger.error(f"Failed to load {plugin_name} due to: {self.logger.f_traceback(e)}")

            return

        plugin_config_file = os.path.join(root, "plugin.yml")

        if not os.path.isfile(plugin_config_file):
            self.logger.error(f"Failed to load {plugin_name} due to missing plugin.yml.")
            return

        try:
            conf = self.load_plugin_config(root)
        except ValueError as e:
            self.logger.error(f"Failed to load {plugin_name} due to invalid plugin.yml. ({str(e)})")
            return
        except BaseException as e:
            self.logger.error(f"Failed to load {plugin_name} due to invalid plugin.yml. Error: {self.logger.f_traceback(e)}")
            return

        dependencies = conf.get("dependencies")
        if dependencies:
            for i, dependency in enumerate(dependencies):

                try:
                    dep = pkg_resources.Requirement(dependency)
                    pkg_resources.resource_exists(dep, dependency)
                    continue
                except pkg_resources.DistributionNotFound:
                    pass

                if dependency.strip("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_=<>1234567890") != "":
                    self.logger.critical(f"Possible malicious code found in {plugin_name}!")
                    self.logger.warn(f"Failed to load {plugin_name} due to possible malicious code in plugin.yml")
                    return

                self.logger.info(f"Installing {dependency} for {plugin_name} [{i}/{len(dependencies)}]")

                proc = await asyncio.subprocess.create_subprocess_shell(
                    f'pip install -U "{dependency}"', stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )
                _, stderr = await proc.communicate()
                if proc.returncode != 0:
                    self.logger.error(f"Cannot install {dependency} due to \n {stderr.decode()}")
                    self.logger.error(f"Failed to load {plugin_name} due to dependency installation failure!")
                    return

            self.logger.info(f"All dependencies have been installed for {plugin_name}")

        if conf.get("git_url"):
            self.logger.info(f"Checking for updates for {plugin_name}...")

            try:
                self.update_repo(git_dir, conf["git_url"], root, plugin_name)
            except BaseException as e:
                self.logger.error(f"Failed to update {plugin_name} due to: {self.logger.f_traceback(e)}")

        plugin_path = root

        if conf.get("module_folder"):
            plugin_path = os.path.join(plugin_path, conf["module_folder"])

        plugin_path = plugin_path.replace("\\", "/").replace("/", ".")

        try:
            plugin_module = importlib.import_module(plugin_path)
        except BaseException as e:
            self.logger.error(f"Failed to import {plugin_name} due to: {self.logger.f_traceback(e)}")
            return

        try:
            await plugin_module.setup(self.server, conf)
        except BaseException as e:
            self.logger.error(f"Failed to setup {plugin_name} due to: {self.logger.f_traceback(e)}")
            return

        self.plugins[plugin_path] = plugin_module

    async def init(self):  # called when server starts up
        self.commands.load_commands()

        # Load packet handlers / packet logic handlers under pymine/logic/handle
        for root, dirs, files in os.walk(os.path.join("pymine", "logic", "handle")):
            for file in filter((lambda f: f.endswith(".py")), files):
                importlib.import_module(os.path.join(root, file)[:-3].replace("\\", "/").replace("/", "."))

        try:
            os.mkdir("plugins")
        except FileExistsError:
            pass

        plugins_dir = os.listdir("plugins")
        git_dir = git.Git("plugins")

        results = await asyncio.gather(*[self.load_plugin(git_dir, plugin) for plugin in plugins_dir], return_exceptions=True)

        for plugin, result in zip(plugins_dir, results):
            if isinstance(result, BaseException):
                self.logger.error(f"Failed to load {plugin} due to: {self.logger.f_traceback(result)}")

        # *should* make packet handling slightly faster
        self.events._packet = make_immutable(self.events._packet)

        # start console command handler task
        self.tasks.append(asyncio.create_task(self.commands.handle_console()))

    async def stop(self):  # called when server is stopping
        for task in self.tasks:
            try:
                task.cancel()
            except BaseException:
                pass

        for plugin_name, plugin_module in self.plugins.items():
            try:
                await plugin_module.teardown(self.server)
            except BaseException as e:
                self.logger.error(f"Error occurred while tearing down {plugin_name}: {self.logger.f_traceback(e)}")

        # call and await upon all registered on_server_stop handlers
        self.taskify_handlers(self.events._server_stop)
        await asyncio.gather(*self.tasks)
