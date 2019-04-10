"""
Entry point for the CLI
"""

import click
import os
import sys
import logging

work_dir = os.getcwd()
dir_name, file_name = os.path.split(os.path.abspath(sys.argv[0]))
os.chdir(dir_name)
os.chdir('../../..')
sys.path.insert(0, os.getcwd())
os.chdir(work_dir)

from tcfcli.cmds.cli import __version__
from tcfcli.cmds.deploy.cli import deploy
from tcfcli.cmds.package.cli import package
from tcfcli.cmds.local.cli import local
from tcfcli.cmds.init.cli import init
from tcfcli.cmds.validate.cli import validate
from tcfcli.cmds.configure.cli import configure

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


@click.group()
@click.version_option(version=__version__, prog_name="TCF CLI")
def cli():
    pass


"""
Register commands into cli group
"""
cli.add_command(package)
cli.add_command(deploy)
cli.add_command(local)
cli.add_command(init)
cli.add_command(configure)
cli.add_command(validate)

if __name__ == "__main__":
    cli()
