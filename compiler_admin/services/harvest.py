from datetime import datetime, timedelta
import os
import sys
from typing import TextIO

import pandas as pd

import compiler_admin.services.files as files

# input CSV columns needed for conversion
INPUT_COLUMNS = ["Date", "Client", "Project", "Notes", "Hours", "First Name", "Last Name"]

# default output CSV columns
OUTPUT_COLUMNS = ["Email", "Start date", "Start time", "Duration", "Project", "Task", "Client", "Billable", "Description"]


def _calc_start_time(group: pd.DataFrame):
    """Start time is offset by the previous record's duration, with a default of 0 offset for the first record."""
    group["Start time"] = group["Start time"] + group["Duration"].shift(fill_value=pd.to_timedelta("00:00:00")).cumsum()
    return group


def _duration_str(duration: timedelta) -> str:
    """Use total seconds to convert to a datetime and format as a string e.g. 01:30."""
    return datetime.fromtimestamp(duration.total_seconds()).strftime("%H:%M")


def _toggl_client_name():
    """Gets the value of the TOGGL_CLIENT_NAME env var."""
    return os.environ.get("TOGGL_CLIENT_NAME")


def convert_to_toggl(
    source_path: str | TextIO = sys.stdin,
    output_path: str | TextIO = sys.stdout,
    client_name: str = None,
    output_cols: list[str] = OUTPUT_COLUMNS,
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
    source = files.read_csv(source_path, usecols=INPUT_COLUMNS, parse_dates=["Date"], cache_dates=True)

    # rename columns that can be imported as-is
    source.rename(columns={"Project": "Task", "Notes": "Description", "Date": "Start date"}, inplace=True)

    # update static calculated columns
    source["Client"] = client_name
    source["Project"] = client_name
    source["Billable"] = "Yes"

    # add the Email column
    source["Email"] = source["First Name"].apply(lambda x: f"{x.lower()}@compiler.la")

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
