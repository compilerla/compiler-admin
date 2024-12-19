from datetime import datetime, timedelta
import os
import sys
from typing import List

import click
from pytz import timezone

from compiler_admin.services.toggl import TOGGL_COLUMNS, download_time_entries


TZINFO = timezone(os.environ.get("TZ_NAME", "America/Los_Angeles"))


def local_now():
    return datetime.now(tz=TZINFO)


def prior_month_end():
    now = local_now()
    first = now.replace(day=1)
    return first - timedelta(days=1)


def prior_month_start():
    end = prior_month_end()
    return end.replace(day=1)


@click.command()
@click.option(
    "--start",
    metavar="YYYY-MM-DD",
    default=prior_month_start(),
    type=lambda s: TZINFO.localize(datetime.strptime(s, "%Y-%m-%d")),
    help="The start date of the reporting period. Defaults to the beginning of the prior month.",
)
@click.option(
    "--end",
    metavar="YYYY-MM-DD",
    default=prior_month_end(),
    type=lambda s: TZINFO.localize(datetime.strptime(s, "%Y-%m-%d")),
    help="The end date of the reporting period. Defaults to the end of the prior month.",
)
@click.option(
    "--output",
    default=os.environ.get("TOGGL_DATA", sys.stdout),
    help="The path to the file where downloaded data should be written. Defaults to a path calculated from the date range.",
)
@click.option(
    "--all",
    "billable",
    is_flag=True,
    default=True,
    help="Download all time entries. The default is to download only billable time entries.",
)
@click.option(
    "-c",
    "--client",
    "client_ids",
    multiple=True,
    help="An ID for a Toggl Client to filter for in reports. Can be supplied more than once.",
    metavar="CLIENT_ID",
    type=int,
)
@click.option(
    "-p",
    "--project",
    "project_ids",
    multiple=True,
    help="An ID for a Toggl Project to filter for in reports. Can be supplied more than once.",
    metavar="PROJECT_ID",
    type=int,
)
@click.option(
    "-t",
    "--task",
    "task_ids",
    multiple=True,
    metavar="TASK_ID",
    help="An ID for a Toggl Project Task to filter for in reports. Can be supplied more than once.",
    type=int,
)
@click.option(
    "-u",
    "--user",
    "user_ids",
    multiple=True,
    help="An ID for a Toggl User to filter for in reports. Can be supplied more than once.",
    metavar="USER_ID",
    type=int,
)
def download(
    start: datetime,
    end: datetime,
    output: str = "",
    billable: bool = True,
    client_ids: List[int] = [],
    project_ids: List[int] = [],
    task_ids: List[int] = [],
    user_ids: List[int] = [],
):
    """
    Download a Toggl time report in CSV format.
    """
    if not output:
        output = f"Toggl_time_entries_{start.strftime('%Y-%m-%d')}_{end.strftime('%Y-%m-%d')}.csv"

    params = dict(start_date=start, end_date=end, output_path=output, output_cols=TOGGL_COLUMNS, billable=billable)

    if client_ids:
        params.update(dict(client_ids=client_ids))
    if project_ids:
        params.update(dict(project_ids=project_ids))
    if task_ids:
        params.update(dict(task_ids=task_ids))
    if user_ids:
        params.update(dict(user_ids=user_ids))

    download_time_entries(**params)
