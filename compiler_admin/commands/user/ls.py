import click

from compiler_admin.services.google import CallGAMCommand
from compiler_admin.services.toggl import TogglUsers


def ls_google(inactive: bool = False, **kwargs):
    """Use GAM to print the users in the Google Workspace."""
    flag = str(inactive).lower()
    command = ("print", "users") + ("issuspended", flag, "isarchived", flag)

    CallGAMCommand(command)


def ls_toggl(inactive: bool = False, **kwargs):
    """Use the Toggl API to get a list of users."""
    toggl = TogglUsers()
    if inactive:
        active_status = "inactive,invited"
    else:
        active_status = "active"

    users = toggl.get_organization_users(active_status=active_status)

    # Mirroing the default GAM output for print users
    click.echo(f"Got {len(users)} Users")
    click.echo("email")
    for user in users:
        click.echo(user["email"])


USER_SYSTEMS = {"google": ls_google, "toggl": ls_toggl}


@click.command()
@click.option("--inactive", help="List inactive users in the system.", is_flag=True)
@click.argument(
    "system",
    type=click.Choice(USER_SYSTEMS.keys(), case_sensitive=False),
    default="google",
)
def ls(system: str, inactive: bool, **kwargs):
    """List users in the Compiler workspace."""
    ls_system = USER_SYSTEMS.get(system)
    ls_system(inactive=inactive, **kwargs)
