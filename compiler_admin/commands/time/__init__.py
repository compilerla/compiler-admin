import click

from compiler_admin.commands.time.convert import convert
from compiler_admin.commands.time.download import download
from compiler_admin.commands.time.lock import lock
from compiler_admin.commands.time.verify import verify


@click.group
def time():
    """
    Work with Compiler time entries.
    """
    pass


time.add_command(convert)
time.add_command(download)
time.add_command(lock)
time.add_command(verify)
