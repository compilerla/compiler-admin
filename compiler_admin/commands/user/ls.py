import click

from compiler_admin import RESULT_SUCCESS
from compiler_admin.services.google import CallGAMCommand


@click.command()
def ls(**kwargs):
    """Lists users in the Compiler workspace."""
    click.echo("Listing users in Compiler workspace")

    command = ("print", "users")
    CallGAMCommand(command)
    raise SystemExit(RESULT_SUCCESS)
