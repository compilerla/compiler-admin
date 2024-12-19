import click

from compiler_admin import __version__ as version
from compiler_admin.services.google import CallGAMCommand, CallGYBCommand


@click.command()
def info():
    """
    Print information about the configured environment.
    """
    click.echo(f"compiler-admin, version {version}")

    CallGAMCommand(("version",))
    CallGAMCommand(("info", "domain"))
    CallGYBCommand(("--version",))
