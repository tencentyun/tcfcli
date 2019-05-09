import click
from .invoke.cli import invoke


@click.group(name='native')
def native():
    """
    Run your scf natively for quick development
    """
    pass


native.add_command(invoke)


