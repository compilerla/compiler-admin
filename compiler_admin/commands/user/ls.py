import click
import pandas as pd

from compiler_admin import Format
from compiler_admin.services import files
from compiler_admin.services.google import get_org_units, get_users
from compiler_admin.services.toggl import TogglUsers


def ls_google(format: int = Format.BASIC, groups: bool = False, inactive: bool = False, **kwargs):
    """Use GAM to print the users in the Google Workspace."""
    if groups:
        get_org_units(format=format)
    else:
        output = get_users(inactive=inactive, format=format, **kwargs)
        click.echo(output)


def ls_toggl(format: int = Format.BASIC, groups: bool = False, inactive: bool = False, **kwargs):
    """Use the Toggl API to get a list of users.

    Mirrors the GAM output style for Google users.
    """
    toggl = TogglUsers()

    if groups:
        click.echo("Getting all Toggl groups...", err=True)
        groups = toggl.get_organization_groups()
        groups_df = pd.DataFrame(groups)
        click.echo(f"Got {len(groups)} Groups", err=True)

        stdout = click.get_text_stream("stdout")
        if format in [Format.BASIC, Format.CSV]:
            files.write_csv(stdout, groups_df, columns=["group_id", "name", "at"])
        elif format == Format.JSON:
            files.write_json(stdout, groups)
        return

    click.echo("Getting all Toggl users...", err=True)
    users = toggl.get_organization_users(inactive=inactive, **kwargs)
    users_df = pd.DataFrame(users)
    click.echo(f"Got {len(users)} Users", err=True)

    stdout = click.get_text_stream("stdout")
    columns = ["email"]
    if format == Format.BASIC:
        files.write_csv(stdout, users_df, columns=columns)
    elif format == Format.CSV:
        columns += [
            "name",
            "id",
            "user_id",
            "role_id",
            "organization_id",
            "inactive",
            "joined",
            "can_edit_email",
            "2fa_enabled",
            "avatar_url",
        ]
        files.write_csv(stdout, users_df, columns=columns)
    elif format == Format.JSON:
        files.write_json(stdout, users)


USER_SYSTEMS = {"google": ls_google, "toggl": ls_toggl}
FORMATS = {
    "b": Format.BASIC,
    "basic": Format.BASIC,
    "c": Format.CSV,
    "csv": Format.CSV,
    "j": Format.JSON,
    "json": Format.JSON,
}


@click.command()
@click.option("--groups", is_flag=True, help="Show groups instead.")
@click.option("--inactive", help="List inactive users in the system.", is_flag=True)
@click.option(
    "--format",
    "format_key",
    help="The format of the output.",
    type=click.Choice(FORMATS.keys(), case_sensitive=False),
    default="basic",
)
@click.argument(
    "system",
    type=click.Choice(USER_SYSTEMS.keys(), case_sensitive=False),
    default="google",
)
def ls(system: str, groups: bool, inactive: bool, format_key: str, **kwargs):
    """List users in the Compiler workspace."""
    format = FORMATS.get(format_key)

    ls_system = USER_SYSTEMS.get(system)
    ls_system(format=format, groups=groups, inactive=inactive, **kwargs)
