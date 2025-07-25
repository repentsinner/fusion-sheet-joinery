# Assuming you have not changed the general structure of the template no
# modification is needed in this file.
from . import commands
from .lib import fusionAddInUtils as futil


def run(_):
    try:
        # This will run the start function in each of your commands as defined
        # in commands/__init__.py
        commands.start()

    except Exception:
        futil.handle_error("run")


def stop(_):
    try:
        # Remove all of the event handlers your app has created
        futil.clear_handlers()

        # This will run the start function in each of your commands as defined
        # in commands/__init__.py
        commands.stop()

    except Exception:
        futil.handle_error("stop")
