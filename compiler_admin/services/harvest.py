import os
import sys
import time
from datetime import timedelta
from typing import TextIO

import pandas as pd

import compiler_admin.services.files as files
from compiler_admin.services.time import TimeSummary

# input CSV columns needed for conversion
HARVEST_COLUMNS = ["Date", "Client", "Project", "Notes", "Hours", "First name", "Last name"]

# default output CSV columns
TOGGL_COLUMNS = ["Email", "Start date", "Start time", "Duration", "Project", "Task", "Client", "Billable", "Description"]


def _calc_start_time(group: pd.DataFrame):
    """Start time is offset by the previous record's duration, with a default of 0 offset for the first record."""
    group["Start time"] = group["Start time"] + group["Duration"].shift(fill_value=pd.to_timedelta("00:00:00")).cumsum()
    return group


def _duration_str(duration: timedelta) -> str:
    """Use total seconds to convert to a datetime and format as a string e.g. 01:30."""
    return time.strftime("%H:%M", time.gmtime(duration.total_seconds()))


def _toggl_client_name():
    """Gets the value of the TOGGL_CLIENT_NAME env var."""
    return os.environ.get("TOGGL_CLIENT_NAME")


def convert_to_toggl(
    source_path: str | TextIO = sys.stdin,
    output_path: str | TextIO = sys.stdout,
    output_cols: list[str] = TOGGL_COLUMNS,
    client_name: str = None,
    **kwargs,
):
    """Convert Harvest formatted entries in source_path to equivalent Toggl formatted entries.

    Args:
        source_path: The path to a readable CSV file of Harvest time entries; or a readable buffer of the same.

        output_cols (list[str]): A list of column names for the output

        output_path: The path to a CSV file where Toggl time entries will be written; or a writeable buffer for the same.

    Returns:
        None. Either prints the resulting CSV data or writes to output_path.
    """
    if client_name is None:
        client_name = _toggl_client_name()

    # read CSV file, parsing dates
    source = files.read_csv(source_path, usecols=HARVEST_COLUMNS, parse_dates=["Date"], cache_dates=True)

    # rename columns that can be imported as-is
    source.rename(columns={"Project": "Task", "Notes": "Description", "Date": "Start date"}, inplace=True)

    # update static calculated columns
    source["Client"] = client_name
    source["Project"] = client_name
    source["Billable"] = "Yes"

    # add the Email column
    source["Email"] = source["First name"].apply(lambda x: f"{x.lower()}@compiler.la")

    # Convert numeric Hours to timedelta Duration
    source["Duration"] = source["Hours"].apply(pd.to_timedelta, unit="hours")

    # Default start time to 09:00
    source["Start time"] = pd.to_timedelta("09:00:00")

    user_days = (
        source
        # sort and group by email and date
        .sort_values(["Email", "Start date"]).groupby(["Email", "Start date"], observed=False)
        # calculate a start time within each group (excluding the groupby columns)
        .apply(_calc_start_time, include_groups=False)
    )

    # convert timedeltas to duration strings
    user_days["Duration"] = user_days["Duration"].apply(_duration_str)
    user_days["Start time"] = user_days["Start time"].apply(_duration_str)

    # re-sort by start date/time and user
    # reset the index to get rid of the group multi index and fold the group columns back down
    output_data = pd.DataFrame(data=user_days).reset_index()
    output_data.sort_values(["Start date", "Start time", "Email"], inplace=True)

    files.write_csv(output_path, output_data, output_cols)


def summarize(path: str | TextIO) -> "TimeSummary":
    """Summarize a Harvest CSV file.

    Args:
        path (str | TextIO): The path to a readable CSV file of Harvest time entries; or a readable buffer of the same.

    Returns:
        TimeSummary: A summary of the time entries.
    """

    # read CSV file, parsing dates
    source = files.read_csv(path, usecols=HARVEST_COLUMNS, parse_dates=["Date"], cache_dates=True)

    summary = TimeSummary(
        earliest_date=source["Date"].min().date(),
        latest_date=source["Date"].max().date(),
        total_rows=len(source),
        total_hours=source["Hours"].sum(),
    )

    # Group by Project to get hours per project
    project_hours = source.groupby(["Project"])["Hours"].sum().to_dict()
    summary.hours_per_project = project_hours

    # Group by User and Project to get hours per user/project
    user_project_hours = source.groupby(["First name", "Last name", "Project"])["Hours"].sum().to_dict()
    # create a nested dict of the form {user: {project: hours}}
    for (first, last, project), hours in user_project_hours.items():
        user = f"{first} {last}"
        if user not in summary.hours_per_user_project:
            summary.hours_per_user_project[user] = {}
        summary.hours_per_user_project[user][project] = hours

    return summary


CONVERTERS = {"toggl": convert_to_toggl}
