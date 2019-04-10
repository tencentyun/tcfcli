import click
from .invoke.cli import invoke
from .start_api.cli import start_api
from .generate_event.cli import generate_event

@click.group(name='local')
def local():
    """
    Run your scf locally for quick development
    """
    pass


local.add_command(invoke)
# local.add_command(start_api)
local.add_command(generate_event)

