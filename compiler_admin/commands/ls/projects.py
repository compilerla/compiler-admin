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
    "-c",
    "--client-id",
    "client_ids",
    multiple=True,
    type=int,
    help="A Toggl client ID to filter projects by. Can be supplied more than once.",
)
@click.option(
    "-i",
    "--id",
    "ids",
    multiple=True,
    type=int,
    help="A Toggl project ID to filter by. Can be supplied more than once.",
)
@click.option("--name", help="Filter projects by name.")
@click.option(
    "--active/--inactive",
    "is_active",
    default=True,
    help="Filter for active projects if set to --active, archived projects if set to --inactive.",
)
@click.option(
    "--billable/--internal",
    "is_billable",
    default=True,
    help="Filter for billable projects if set to --billable, non-billable if set to --internal.",
)
@click.option(
    "--private/--public",
    "is_private",
    default=True,
    help="Filter for private projects if set to --private, public projects if set to --public.",
)
@click.option(
    "--detailed",
    is_flag=True,
    default=False,
    help="Use the Track API to return detailed project information including rate, estimated hours, dates, and more.",
)
def projects(
    format_key: str,
    client_ids: tuple[int, ...],
    ids: tuple[int, ...],
    name: str | None,
    is_active: bool | None,
    is_billable: bool | None,
    is_private: bool | None,
    detailed: bool = False,
):
    """List Toggl projects from the Compiler workspace."""
    format = FORMATS.get(format_key)
    client_ids_list = list(client_ids) if client_ids else None
    ids_list = list(ids) if ids else None

    api = TogglUtils()
    click.echo("Getting Toggl projects...", err=True)

    if detailed:
        click.echo("Fetching detailed project information (Track API)...", err=True)
        items = api.get_projects_detailed(
            client_ids=client_ids_list,
            ids=ids_list,
            is_active=is_active,
            is_billable=is_billable,
            is_private=is_private,
            name=name,
        )
        click.echo(f"Got {len(items)} Projects (detailed)", err=True)
    else:
        items = api.get_projects(
            client_ids=client_ids_list,
            ids=ids_list,
            is_active=is_active,
            is_billable=is_billable,
            is_private=is_private,
            name=name,
        )
        click.echo(f"Got {len(items)} Projects", err=True)

    stdout = click.get_text_stream("stdout")
    if format in [Format.BASIC, Format.CSV]:
        dataframe = pd.DataFrame(items)
        if detailed:
            # Exclude internal/auxiliary fields from detailed output
            excluded = {"total_count", "pinned", "can_track_time", "permissions", "recurring", "recurring_parameters"}
            items_list = [{k: v for k, v in item.items() if k not in excluded} for item in items]
            dataframe = pd.DataFrame(items_list)
            requested_columns = list(items[0].keys()) if items else []
        else:
            # Ensure all requested columns exist on the dataframe to avoid KeyError
            requested_columns = ["id", "name", "client_id", "active", "billable", "private"]
            for col in requested_columns:
                if col not in dataframe.columns:
                    dataframe[col] = None
        files.write_csv(
            stdout,
            dataframe,
            columns=requested_columns,
        )
    elif format == Format.JSON:
        files.write_json(stdout, items)
