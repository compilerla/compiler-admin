import click
import pandas as pd

from compiler_admin import FORMATS, Format
from compiler_admin.services import files
from compiler_admin.services.google import GoogleGroups
from compiler_admin.services.toggl import TogglUsers


def google(format: int = Format.BASIC, **kwargs):
    """Use GAM to print the groups in the Google Workspace."""
    output = GoogleGroups().get(format=format, **kwargs)
    click.echo(output)


def toggl(format: int = Format.BASIC, **kwargs):
    """Use the Toggl API to get a list of groups.

    Mirrors the GAM output style for Google groups.
    """
    api = TogglUsers()

    click.echo("Getting all Toggl groups...", err=True)
    groups = api.get_organization_groups()
    click.echo(f"Got {len(groups)} Groups", err=True)

    stdout = click.get_text_stream("stdout")
    if format in [Format.BASIC, Format.CSV]:
        dataframe = pd.DataFrame(groups)
        files.write_csv(stdout, dataframe, columns=["group_id", "name", "at"])
    elif format == Format.JSON:
        files.write_json(stdout, groups)


GROUP_SYSTEMS = {"google": google, "toggl": toggl}


@click.command()
@click.option(
    "--format",
    "format_key",
    help="The format of the output.",
    type=click.Choice(FORMATS.keys(), case_sensitive=False),
    default="basic",
)
@click.argument(
    "system",
    type=click.Choice(GROUP_SYSTEMS.keys(), case_sensitive=False),
    default="google",
)
def groups(system: str, format_key: str, **kwargs):
    """List groups in the Compiler workspace."""
    format = FORMATS.get(format_key)

    ls_system = GROUP_SYSTEMS.get(system)
    ls_system(format=format, **kwargs)
