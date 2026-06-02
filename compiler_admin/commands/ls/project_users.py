import click
import pandas as pd

from compiler_admin import FORMATS, Format
from compiler_admin.services import files
from compiler_admin.services.toggl import TogglUtils


@click.command(name="project-users")
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
    help="A Toggl client ID to filter project users by. Can be supplied more than once.",
)
@click.option(
    "-p",
    "--project-id",
    "project_ids",
    multiple=True,
    type=int,
    help="A Toggl project ID to filter project users by. Can be supplied more than once.",
)
def project_users(
    format_key: str,
    client_ids: tuple[int, ...],
    project_ids: tuple[int, ...],
):
    """List Toggl project users from the Compiler workspace."""
    format = FORMATS.get(format_key)
    client_ids_list = list(client_ids) if client_ids else None
    project_ids_list = list(project_ids) if project_ids else None

    api = TogglUtils()
    click.echo("Getting Toggl project users...", err=True)
    items = api.get_project_users(
        client_ids=client_ids_list,
        project_ids=project_ids_list,
    )
    click.echo(f"Got {len(items)} Project Users", err=True)

    stdout = click.get_text_stream("stdout")
    if format in [Format.BASIC, Format.CSV]:
        dataframe = pd.DataFrame(items)
        files.write_csv(
            stdout,
            dataframe,
            columns=["id", "group_id", "project_id", "user_id", "hourly_rate", "labour_cost"],
        )
    elif format == Format.JSON:
        files.write_json(stdout, items)
