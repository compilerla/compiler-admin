from datetime import datetime
import io
import os
import sys
from typing import TextIO

import pandas as pd

from compiler_admin.api.toggl import Toggl
from compiler_admin.services.google import user_info as google_user_info
import compiler_admin.services.files as files

# cache of previously seen user information, keyed on email
USER_INFO = files.JsonFileCache("TOGGL_USER_INFO")

# input columns needed for conversion
TOGGL_COLUMNS = ["Email", "Project", "Client", "Start date", "Start time", "Duration", "Description"]

# default output CSV columns for Harvest
HARVEST_COLUMNS = ["Date", "Client", "Project", "Task", "Notes", "Hours", "First name", "Last name"]


def _get_first_name(email: str) -> str:
    """Get cached first name or derive from email."""
    user = USER_INFO.get(email)
    first_name = user.get("First Name") if user else None
    if first_name is None:
        parts = email.split("@")
        first_name = parts[0].capitalize()
        data = {"First Name": first_name}
        if email in USER_INFO:
            USER_INFO[email].update(data)
        else:
            USER_INFO[email] = data
    return first_name


def _get_last_name(email: str):
    """Get cached last name or query from Google."""
    user = USER_INFO.get(email)
    last_name = user.get("Last Name") if user else None
    if last_name is None:
        user = google_user_info(email)
        last_name = user.get("Last Name") if user else None
        if email in USER_INFO:
            USER_INFO[email].update(user)
        else:
            USER_INFO[email] = user
    return last_name


def _str_timedelta(td: str):
    """Convert a string formatted duration (e.g. 01:30) to a timedelta."""
    return pd.to_timedelta(pd.to_datetime(td, format="%H:%M:%S").strftime("%H:%M:%S"))


def convert_to_harvest(
    source_path: str | TextIO = sys.stdin,
    output_path: str | TextIO = sys.stdout,
    client_name: str = None,
    output_cols: list[str] = HARVEST_COLUMNS,
):
    """Convert Toggl formatted entries in source_path to equivalent Harvest formatted entries.

    Args:
        source_path: The path to a readable CSV file of Toggl time entries; or a readable buffer of the same.

        client_name (str): The value to assign in the output "Client" field

        output_cols (list[str]): A list of column names for the output

        output_path: The path to a CSV file where Harvest time entries will be written; or a writeable buffer for the same.

    Returns:
        None. Either prints the resulting CSV data or writes to output_path.
    """
    if client_name is None:
        client_name = os.environ.get("HARVEST_CLIENT_NAME")

    # read CSV file, parsing dates and times
    source = files.read_csv(source_path, usecols=TOGGL_COLUMNS, parse_dates=["Start date"], cache_dates=True)
    source["Start time"] = source["Start time"].apply(_str_timedelta)
    source["Duration"] = source["Duration"].apply(_str_timedelta)
    source.sort_values(["Start date", "Start time", "Email"], inplace=True)

    # rename columns that can be imported as-is
    source.rename(columns={"Project": "Project", "Description": "Notes", "Start date": "Date"}, inplace=True)

    # update static calculated columns
    source["Client"] = client_name
    source["Task"] = "Project Consulting"

    # get cached project name if any, keyed on Toggl project name
    project_info = files.JsonFileCache("TOGGL_PROJECT_INFO")
    source["Project"] = source["Project"].apply(lambda x: project_info.get(key=x, default=x))

    # assign First and Last name
    source["First name"] = source["Email"].apply(_get_first_name)
    source["Last name"] = source["Email"].apply(_get_last_name)

    # calculate hours as a decimal from duration timedelta
    source["Hours"] = (source["Duration"].dt.total_seconds() / 3600).round(2)

    files.write_csv(output_path, source, columns=output_cols)


def download_time_entries(
    start_date: datetime,
    end_date: datetime,
    output_path: str | TextIO = sys.stdout,
    output_cols: list[str] | None = TOGGL_COLUMNS,
    **kwargs,
):
    """Download a CSV report from Toggl of detailed time entries for the given date range.

    Args:
        start_date (datetime): The beginning of the reporting period.

        end_date (str): The end of the reporting period.

        output_path: The path to a CSV file where Toggl time entries will be written; or a writeable buffer for the same.

        output_cols (list[str]): A list of column names for the output.

    Extra kwargs are passed along in the POST request body.

    Returns:
        None. Either prints the resulting CSV data or writes to output_path.
    """
    env_client_id = os.environ.get("TOGGL_CLIENT_ID")
    if env_client_id:
        env_client_id = int(env_client_id)
    if ("client_ids" not in kwargs or not kwargs["client_ids"]) and isinstance(env_client_id, int):
        kwargs["client_ids"] = [env_client_id]

    token = os.environ.get("TOGGL_API_TOKEN")
    workspace = os.environ.get("TOGGL_WORKSPACE_ID")
    toggl = Toggl(token, workspace)

    response = toggl.detailed_time_entries(start_date, end_date, **kwargs)
    # the raw response has these initial 3 bytes:
    #
    #   b"\xef\xbb\xbfUser,Email,Client..."
    #
    # \xef\xbb\xb is the Byte Order Mark (BOM) sometimes used in unicode text files
    # these 3 bytes indicate a utf-8 encoded text file
    #
    # See more
    #  - https://en.wikipedia.org/wiki/Byte_order_mark
    #  - https://stackoverflow.com/a/50131187
    csv = response.content.decode("utf-8-sig")

    df = pd.read_csv(io.StringIO(csv))
    files.write_csv(output_path, df, columns=output_cols)
