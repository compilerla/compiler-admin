import click

from compiler_admin.services.google import get_users
from compiler_admin.services.toggl import TogglUsers


def ls_google(inactive: bool = False, **kwargs):
    """Use GAM to print the users in the Google Workspace."""
    output = get_users(inactive, **kwargs)
    click.echo(output)


def ls_toggl(inactive: bool = False, **kwargs):
    """Use the Toggl API to get a list of users."""
    toggl = TogglUsers()
    users = toggl.get_organization_users(inactive=inactive, **kwargs)

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
