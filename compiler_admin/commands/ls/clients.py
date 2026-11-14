import click
import pandas as pd

from compiler_admin import FORMATS, Format
from compiler_admin.services import files
from compiler_admin.services.toggl import TogglUtils

TRACK_EXCLUDED_FIELDS = {"total_count", "permissions", "wid"}


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
def clients(format_key: str, ids: tuple[int, ...], name: str | None):
    """List Toggl clients from the Compiler workspace."""
    format = FORMATS.get(format_key)
    ids_list = list(ids) if ids else None

    api = TogglUtils()
    click.echo("Getting Toggl clients...", err=True)

    # Use Track API for detailed output (csv/json), Reports API for basic
    is_detailed = format in (Format.CSV, Format.JSON)
    if is_detailed:
        click.echo("Fetching detailed client information...", err=True)
        items = api.get_clients_detailed(ids=ids_list, name=name)
        # Exclude internal/auxiliary fields from detailed output
        items = [{k: v for k, v in item.items() if k not in TRACK_EXCLUDED_FIELDS} for item in items]
        click.echo(f"Got {len(items)} Clients", err=True)
    else:
        items = api.get_clients(ids=ids_list, name=name)
        click.echo(f"Got {len(items)} Clients", err=True)

    stdout = click.get_text_stream("stdout")
    if format in [Format.BASIC, Format.CSV]:
        dataframe = pd.DataFrame(items)
        files._ensure_int_columns(dataframe, ["id"])
        if is_detailed:
            requested_columns = list(items[0].keys()) if items else []
        else:
            requested_columns = ["id", "name"]
        files.write_csv(stdout, dataframe, columns=requested_columns)
    elif format == Format.JSON:
        files.write_json(stdout, items)
