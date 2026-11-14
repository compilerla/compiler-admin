import click
import pandas as pd

from compiler_admin import FORMATS, Format
from compiler_admin.services import files
from compiler_admin.services.toggl import TogglUtils


@click.command()
@click.option(
    "--format",
    "format_key",
    help="The format of the output.",
    type=click.Choice(FORMATS.keys(), case_sensitive=False),
    default="basic",
)
@click.option(
    "-i",
    "--id",
    "ids",
    multiple=True,
    type=int,
    help="A Toggl client ID to filter by. Can be supplied more than once.",
)
@click.option("--name", help="Filter clients by name.")
@click.option(
    "--detailed",
    is_flag=True,
    default=False,
    help="Use the Track API to return detailed client information including archived status, notes, and integration metadata.",
)
def clients(format_key: str, ids: tuple[int, ...], name: str | None, detailed: bool = False):
    """List Toggl clients from the Compiler workspace."""
    format = FORMATS.get(format_key)
    ids_list = list(ids) if ids else None

    api = TogglUtils()
    click.echo("Getting Toggl clients...", err=True)

    if detailed:
        click.echo("Fetching detailed client information (Track API)...", err=True)
        items = api.get_clients_detailed(ids=ids_list, name=name)
        click.echo(f"Got {len(items)} Clients (detailed)", err=True)
        # Exclude internal/auxiliary fields from detailed output
        excluded = {"total_count", "permissions", "wid"}
        items = [{k: v for k, v in item.items() if k not in excluded} for item in items]
    else:
        items = api.get_clients(ids=ids_list, name=name)
        click.echo(f"Got {len(items)} Clients", err=True)

    stdout = click.get_text_stream("stdout")
    if format in [Format.BASIC, Format.CSV]:
        dataframe = pd.DataFrame(items)
        if detailed:
            requested_columns = list(items[0].keys()) if items else []
        else:
            requested_columns = ["id", "name"]
        files.write_csv(stdout, dataframe, columns=requested_columns)
    elif format == Format.JSON:
        files.write_json(stdout, items)
