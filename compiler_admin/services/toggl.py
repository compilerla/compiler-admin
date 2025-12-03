import io
import os
import sys
from datetime import datetime
from functools import cache
from typing import TextIO

import pandas as pd

import compiler_admin.services.files as files
from compiler_admin.api.toggl import Toggl
from compiler_admin.services.google import user_info as google_user_info
from compiler_admin.services.time import TimeSummary

# input columns needed for conversion
TOGGL_COLUMNS = ["Email", "Project", "Task", "Client", "Start date", "Start time", "Duration", "Description"]

# default output CSV columns for Harvest
HARVEST_COLUMNS = ["Date", "Client", "Project", "Task", "Notes", "Hours", "First name", "Last name"]
# default output CSV columns for Justworks
JUSTWORKS_COLUMNS = ["First Name", "Last Name", "Work Email", "Start Date", "End Date", "Regular Hours"]


@cache
def project_info():
    """Cache of previously seen project information, keyed on Toggl project name."""
    return files.JsonFileCache("TOGGL_PROJECT_INFO")


@cache
def user_info():
    """Cache of previously seen user information, keyed on email."""
    return files.JsonFileCache("TOGGL_USER_INFO")


def _get_name(email: str, name_key) -> str:
    """Get cached name or query from Google."""
    info = user_info()
    user = info.get(email)
    name = user.get(name_key) if user else None
    if name is None:
        user = google_user_info(email)
        name = user.get(name_key) if user else None
        if email in info:
            info[email].update(user)
        else:
            info[email] = user
    return name


def _get_first_name(email: str) -> str:
    """Get cached last name or query from Google."""
    return _get_name(email, "First Name")


def _get_last_name(email: str):
    """Get cached last name or query from Google."""
    return _get_name(email, "Last Name")


def _prepare_input(source_path: str | TextIO, column_renames: dict = {}) -> pd.DataFrame:
    """Parse and prepare CSV data from `source_path` into an initial `pandas.DataFrame`."""
    df = files.read_csv(source_path, usecols=TOGGL_COLUMNS, parse_dates=["Start date"], cache_dates=True)

    df["Start time"] = df["Start time"].apply(_str_timedelta)
    df["Duration"] = df["Duration"].apply(_str_timedelta)

    # assign First and Last name
    df["First name"] = df["Email"].apply(_get_first_name)
    df["Last name"] = df["Email"].apply(_get_last_name)

    # calculate hours as a decimal from duration timedelta
    df["Hours"] = (df["Duration"].dt.total_seconds() / 3600).round(2)

    # if there is a Task column, prepend to the Description column and remove
    if "Task" in df.columns:
        df["Description"] = df.apply(
            lambda row: (f"[{row['Task']}] {row['Description']}" if pd.notna(row["Task"]) else row["Description"]), axis=1
        )
        df.drop(columns=["Task"], inplace=True)

    df.sort_values(["Start date", "Start time", "Email"], inplace=True)

    if column_renames:
        df.rename(columns=column_renames, inplace=True)

    return df


def _str_timedelta(td: str):
    """Convert a string formatted duration (e.g. 01:30) to a timedelta."""
    return pd.to_timedelta(pd.to_datetime(td, format="%H:%M:%S").strftime("%H:%M:%S"))


def convert_to_harvest(
    source_path: str | TextIO = sys.stdin,
    output_path: str | TextIO = sys.stdout,
    output_cols: list[str] = HARVEST_COLUMNS,
    client_name: str = None,
    **kwargs,
):
    """Convert Toggl formatted entries in source_path to equivalent Harvest formatted entries.

    Args:
        source_path: The path to a readable CSV file of Toggl time entries; or a readable buffer of the same.

        output_path: The path to a CSV file where Harvest time entries will be written; or a writeable buffer for the same.

        output_cols (list[str]): A list of column names for the output

        client_name (str): The value to assign in the output "Client" field

    Returns:
        None. Either prints the resulting CSV data or writes to output_path.
    """
    if client_name is None:
        client_name = os.environ.get("HARVEST_CLIENT_NAME")

    source = _prepare_input(
        source_path=source_path, column_renames={"Project": "Project", "Description": "Notes", "Start date": "Date"}
    )

    # update static calculated columns
    source["Client"] = client_name
    source["Task"] = "Project Consulting"

    # get cached project name if any, keyed on Toggl project name
    info = project_info()
    source["Project"] = source["Project"].apply(lambda x: info.get(key=x, default=x))

    # find duplicates based on a subset of columns
    cols = ["Date", "Hours", "First name", "Last name", "Notes"]
    is_duplicate = source.duplicated(subset=cols, keep=False)

    if is_duplicate.any():
        # Create a counter for the duplicate rows
        counter = source[is_duplicate].groupby(cols).cumcount() + 1
        group_size = source[is_duplicate].groupby(cols)["Notes"].transform("size")

        # Update the 'Notes' column with the counter
        source.loc[is_duplicate, "Notes"] = (
            source.loc[is_duplicate, "Notes"] + " (" + counter.astype(str) + "/" + group_size.astype(str) + ")"
        )

    files.write_csv(output_path, source, columns=output_cols)


def convert_to_justworks(
    source_path: str | TextIO = sys.stdin,
    output_path: str | TextIO = sys.stdout,
    output_cols: list[str] = JUSTWORKS_COLUMNS,
    **kwargs,
):
    """Convert Toggl formatted entries in source_path to equivalent Justworks formatted entries.

    Args:
        source_path: The path to a readable CSV file of Toggl time entries; or a readable buffer of the same.

        output_path: The path to a CSV file where Harvest time entries will be written; or a writeable buffer for the same.

        output_cols (list[str]): A list of column names for the output

    Returns:
        None. Either prints the resulting CSV data or writes to output_path.
    """
    source = _prepare_input(
        source_path=source_path,
        column_renames={
            "Email": "Work Email",
            "First name": "First Name",
            "Hours": "Regular Hours",
            "Last name": "Last Name",
            "Start date": "Start Date",
        },
    )

    # aggregate hours per person per day
    cols = ["Work Email", "First Name", "Last Name", "Start Date"]
    people = source.sort_values(cols).groupby(cols, observed=False)
    people_agg = people.agg({"Regular Hours": "sum"})
    people_agg.reset_index(inplace=True)

    # aggregate hours per person and rollup to the week (starting on Sunday)
    cols = ["Work Email", "First Name", "Last Name"]
    weekly_agg = people_agg.groupby(cols).resample("W", label="left", on="Start Date")
    weekly_agg = weekly_agg["Regular Hours"].sum().reset_index()

    # calculate the week end date (the following Saturday)
    weekly_agg["End Date"] = weekly_agg["Start Date"] + pd.Timedelta(days=6)

    files.write_csv(output_path, weekly_agg, columns=output_cols)


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


def lock_time_entries(lock_date: datetime):
    """Lock time entries on the given date.

    Args:
        lock_date (datetime): The date to lock time entries.
    """
    token = os.environ.get("TOGGL_API_TOKEN")
    workspace = os.environ.get("TOGGL_WORKSPACE_ID")
    toggl = Toggl(token, workspace)

    lock_date_str = lock_date.strftime("%Y-%m-%d")
    toggl.update_workspace_preferences(report_locked_at=lock_date_str)


def normalize_summary(toggl_summary: TimeSummary) -> TimeSummary:
    """Normalize a Toggl TimeSummary to match the Harvest format."""
    info = project_info()
    new_summary = TimeSummary(
        earliest_date=toggl_summary.earliest_date,
        latest_date=toggl_summary.latest_date,
        total_rows=toggl_summary.total_rows,
        total_hours=toggl_summary.total_hours,
    )

    for project, hours in toggl_summary.hours_per_project.items():
        harvest_project = info.get(key=project, default=project)
        new_summary.hours_per_project[harvest_project] = hours

    for email, projects in toggl_summary.hours_per_user_project.items():
        first_name = _get_first_name(email)
        last_name = _get_last_name(email)
        user = f"{first_name} {last_name}"
        new_summary.hours_per_user_project[user] = {}
        for project, hours in projects.items():
            harvest_project = info.get(key=project, default=project)
            new_summary.hours_per_user_project[user][harvest_project] = hours

    return new_summary


def summarize(path: str | TextIO) -> TimeSummary:
    """Summarize a Toggl CSV file.

    Args:
        path (str | TextIO): The path to a readable CSV file of Toggl time entries; or a readable buffer of the same.

    Returns:
        TimeSummary: A summary of the time entries.
    """
    source = files.read_csv(path, usecols=TOGGL_COLUMNS, parse_dates=["Start date"], cache_dates=True)

    # calculate hours as a decimal from duration string
    source["Hours"] = (pd.to_timedelta(source["Duration"]).dt.total_seconds() / 3600).round(2)

    summary = TimeSummary(
        earliest_date=source["Start date"].min().date(),
        latest_date=source["Start date"].max().date(),
        total_rows=len(source),
        total_hours=source["Hours"].sum(),
    )

    # Group by Project to get hours per project
    project_hours = source.groupby(["Project"])["Hours"].sum().to_dict()
    summary.hours_per_project = project_hours

    # Group by User and Project to get hours per user/project
    user_project_hours = source.groupby(["Email", "Project"])["Hours"].sum().to_dict()
    # create a nested dict of the form {user: {project: hours}}
    for (email, project), hours in user_project_hours.items():
        if email not in summary.hours_per_user_project:
            summary.hours_per_user_project[email] = {}
        summary.hours_per_user_project[email][project] = hours

    return summary


CONVERTERS = {"harvest": convert_to_harvest, "justworks": convert_to_justworks}
