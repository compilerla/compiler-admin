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
def clients(format_key: str, ids: tuple[int, ...], name: str | None):
    """List Toggl clients from the Compiler workspace."""
    format = FORMATS.get(format_key)
    ids_list = list(ids) if ids else None

    api = TogglUtils()
    click.echo("Getting Toggl clients...", err=True)
    items = api.get_clients(ids=ids_list, name=name)
    click.echo(f"Got {len(items)} Clients", err=True)

    stdout = click.get_text_stream("stdout")
    if format in [Format.BASIC, Format.CSV]:
        dataframe = pd.DataFrame(items)
        files.write_csv(stdout, dataframe, columns=["id", "name"])
    elif format == Format.JSON:
        files.write_json(stdout, items)
