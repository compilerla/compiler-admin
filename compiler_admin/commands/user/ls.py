import click
import pandas as pd

from compiler_admin import Format
from compiler_admin.services import files
from compiler_admin.services.google import get_users
from compiler_admin.services.toggl import TogglUsers


def ls_google(inactive: bool = False, format: int = Format.BASIC, **kwargs):
    """Use GAM to print the users in the Google Workspace."""
    output = get_users(inactive=inactive, format=format, **kwargs)
    click.echo(output)


def ls_toggl(inactive: bool = False, format: int = Format.BASIC, **kwargs):
    """Use the Toggl API to get a list of users."""
    toggl = TogglUsers()
    users = toggl.get_organization_users(inactive=inactive, **kwargs)
    users_df = pd.DataFrame(users)

    # Mirroing the GAM output style
    stdout = click.get_text_stream("stdout")

    match format:
        case Format.BASIC:
            click.echo(f"Got {len(users)} Users")
            files.write_csv(stdout, users_df, columns=["email"])
        case Format.CSV:
            click.echo(f"Got {len(users)} Users")
            files.write_csv(
                stdout,
                users_df,
                columns=[
                    "email",
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
                ],
            )
        case Format.JSON:
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
def ls(system: str, inactive: bool, format_key: str, **kwargs):
    """List users in the Compiler workspace."""
    ls_system = USER_SYSTEMS.get(system)
    format = FORMATS.get(format_key)

    ls_system(inactive=inactive, format=format, **kwargs)
