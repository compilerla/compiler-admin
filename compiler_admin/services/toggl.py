import os
import sys
from typing import TextIO

import pandas as pd

from compiler_admin.services.google import user_info as google_user_info
import compiler_admin.services.files as files

# cache of previously seen project information, keyed on Toggl project name
PROJECT_INFO = {}

# cache of previously seen user information, keyed on email
USER_INFO = {}
NOT_FOUND = "NOT FOUND"

# input CSV columns needed for conversion
INPUT_COLUMNS = ["Email", "Project", "Client", "Start date", "Start time", "Duration", "Description"]

# default output CSV columns
OUTPUT_COLUMNS = ["Date", "Client", "Project", "Task", "Notes", "Hours", "First name", "Last name"]


def _harvest_client_name():
    """Gets the value of the HARVEST_CLIENT_NAME env var."""
    return os.environ.get("HARVEST_CLIENT_NAME")


def _get_info(obj: dict, key: str, env_key: str):
    """Read key from obj, populating obj once from a file path at env_key."""
    if obj == {}:
        file_path = os.environ.get(env_key)
        if file_path:
            file_info = files.read_json(file_path)
            obj.update(file_info)
    return obj.get(key)


def _toggl_project_info(project: str):
    """Return the cached project for the given project key."""
    return _get_info(PROJECT_INFO, project, "TOGGL_PROJECT_INFO")


def _toggl_user_info(email: str):
    """Return the cached user for the given email."""
    return _get_info(USER_INFO, email, "TOGGL_USER_INFO")


def _get_first_name(email: str) -> str:
    """Get cached first name or derive from email."""
    user = _toggl_user_info(email)
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
    user = _toggl_user_info(email)
    last_name = user.get("Last Name") if user else None
    if last_name is None:
        user = google_user_info(email)
        last_name = user.get("Last Name") if user else None
        if email in USER_INFO:
            USER_INFO[email].update(user)
        else:
            USER_INFO[email] = user
    return last_name


def _str_timedelta(td):
    """Convert a string formatted duration (e.g. 01:30) to a timedelta."""
    return pd.to_timedelta(pd.to_datetime(td, format="%H:%M:%S").strftime("%H:%M:%S"))


def convert_to_harvest(
    source_path: str | TextIO = sys.stdin,
    output_path: str | TextIO = sys.stdout,
    client_name: str = None,
    output_cols: list[str] = OUTPUT_COLUMNS,
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
        client_name = _harvest_client_name()

    # read CSV file, parsing dates and times
    source = files.read_csv(source_path, usecols=INPUT_COLUMNS, parse_dates=["Start date"], cache_dates=True)
    source["Start time"] = source["Start time"].apply(_str_timedelta)
    source["Duration"] = source["Duration"].apply(_str_timedelta)
    source.sort_values(["Start date", "Start time", "Email"], inplace=True)

    # rename columns that can be imported as-is
    source.rename(columns={"Project": "Project", "Description": "Notes", "Start date": "Date"}, inplace=True)

    # update static calculated columns
    source["Client"] = client_name
    source["Task"] = "Project Consulting"

    # get cached project name if any
    source["Project"] = source["Project"].apply(lambda x: _toggl_project_info(x) or x)

    # assign First and Last name
    source["First name"] = source["Email"].apply(_get_first_name)
    source["Last name"] = source["Email"].apply(_get_last_name)

    # calculate hours as a decimal from duration timedelta
    source["Hours"] = (source["Duration"].dt.total_seconds() / 3600).round(2)

    files.write_csv(output_path, source, columns=output_cols)
