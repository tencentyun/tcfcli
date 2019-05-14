import click
from .invoke.cli import invoke
from tcfcli.cmds.local.generate_event.cli import generate_event


@click.group(name='native')
def native():
    """
    Run your scf natively for quick development
    """
    pass


native.add_command(invoke)
native.add_command(generate_event)


