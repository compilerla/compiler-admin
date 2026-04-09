import click

from compiler_admin.services import files
from compiler_admin.services.google import CallGAMCommand
from compiler_admin.services.toggl import TogglUsers


def ls_google(**kwargs):
    """Use GAM to print the users in the Google Workspace."""
    command = ("print", "users")
    CallGAMCommand(command)


def ls_toggl(**kwargs):
    """Use the Toggl API to get a list of Organization users."""
    toggl = TogglUsers()

    users = toggl.get_organization_users()
    files.write_json(click.get_text_stream("stdout"), users)


USER_SYSTEMS = {"google": ls_google, "toggl": ls_toggl}


@click.command()
@click.argument(
    "system",
    type=click.Choice(USER_SYSTEMS.keys(), case_sensitive=False),
    default="google",
)
def ls(system: str, **kwargs):
    """List users in the Compiler workspace SYSTEM (Google by default)."""
    ls_system = USER_SYSTEMS.get(system)
    ls_system(**kwargs)
