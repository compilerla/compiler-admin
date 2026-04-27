import click
import pandas as pd

from compiler_admin import FORMATS, Format
from compiler_admin.services import files
from compiler_admin.services.google import ORG_UNITS, get_users
from compiler_admin.services.toggl import GROUPS, TogglUsers


def google(format: int = Format.BASIC, inactive: bool = False, account_type: str = "", **kwargs):
    """Use GAM to print the users in the Google Workspace."""
    if account_type and account_type not in ORG_UNITS:
        raise ValueError(f"Unexpected account_type: {account_type}")

    org_unit = ORG_UNITS.get(account_type)
    org_units = [org_unit] if org_unit else []
    output = get_users(format=format, inactive=inactive, org_units=org_units, **kwargs)
    click.echo(output)


def toggl(format: int = Format.BASIC, inactive: bool = False, account_type: str = "", **kwargs):
    """Use the Toggl API to get a list of users.

    Mirrors the GAM output style for Google users.
    """
    api = TogglUsers()

    if account_type and account_type not in GROUPS:
        raise ValueError(f"Unexpected account_type: {account_type}")

    group_filter = []
    group_name = GROUPS.get(account_type)
    if group_name:
        group = api.get_organization_group(group_name)
        group_filter.append(group["group_id"])

    click.echo("Getting all Toggl users...", err=True)
    users = api.get_organization_users(inactive=inactive, groups=group_filter, **kwargs)
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


ACCOUNT_TYPES = set((*GROUPS.keys(), *ORG_UNITS.keys()))
USER_SYSTEMS = {"google": google, "toggl": toggl}


@click.command()
@click.option(
    "--format",
    "format_key",
    help="The format of the output.",
    type=click.Choice(FORMATS.keys(), case_sensitive=False),
    default="basic",
)
@click.option("--inactive", help="List inactive users in the system.", is_flag=True)
@click.option(
    "-t",
    "--account_type",
    "account_type",
    help="Only show users with this account type.",
    type=click.Choice(ACCOUNT_TYPES, case_sensitive=False),
)
@click.argument(
    "system",
    type=click.Choice(USER_SYSTEMS.keys(), case_sensitive=False),
    default="google",
)
def users(system: str, format_key: str, inactive: bool, account_type: str, **kwargs):
    """List users in the Compiler workspace."""
    format = FORMATS.get(format_key)

    ls_system = USER_SYSTEMS.get(system)
    ls_system(format=format, inactive=inactive, account_type=account_type, **kwargs)
