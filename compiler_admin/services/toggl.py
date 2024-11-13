from base64 import b64encode
from datetime import datetime
import io
import os
import sys
from typing import TextIO

import pandas as pd
import requests

from compiler_admin import __version__
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


class Toggl:
    """Toggl API Client.

    See https://engineering.toggl.com/docs/.
    """

    API_BASE_URL = "https://api.track.toggl.com"
    API_REPORTS_BASE_URL = "reports/api/v3"
    API_WORKSPACE = "workspace/{}"
    API_HEADERS = {"Content-Type": "application/json", "User-Agent": "compilerla/compiler-admin:{}".format(__version__)}

    def __init__(self, api_token: str, workspace_id: int, **kwargs):
        self._token = api_token
        self.workspace_id = workspace_id

        self.headers = dict(Toggl.API_HEADERS)
        self.headers.update(self._authorization_header())

        self.timeout = int(kwargs.get("timeout", 5))

    @property
    def workspace_url_fragment(self):
        """The workspace portion of an API URL."""
        return Toggl.API_WORKSPACE.format(self.workspace_id)

    def _authorization_header(self):
        """Gets an `Authorization: Basic xyz` header using the Toggl API token.

        See https://engineering.toggl.com/docs/authentication.
        """
        creds = f"{self._token}:api_token"
        creds64 = b64encode(bytes(creds, "utf-8")).decode("utf-8")
        return {"Authorization": "Basic {}".format(creds64)}

    def _make_report_url(self, endpoint: str):
        """Get a fully formed URL for the Toggl Reports API v3 endpoint.

        See https://engineering.toggl.com/docs/reports_start.
        """
        return "/".join((Toggl.API_BASE_URL, Toggl.API_REPORTS_BASE_URL, self.workspace_url_fragment, endpoint))

    def post_reports(self, endpoint: str, **kwargs) -> requests.Response:
        """Send a POST request to the Reports v3 `endpoint`.

        Extra `kwargs` are passed through as a POST json body.

        Will raise for non-200 status codes.

        See https://engineering.toggl.com/docs/reports_start.
        """
        url = self._make_report_url(endpoint)

        response = requests.post(url, json=kwargs, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()

        return response

    def detailed_time_entries(self, start_date: datetime, end_date: datetime, **kwargs):
        """Request a CSV report from Toggl of detailed time entries for the given date range.

        Args:
            start_date (datetime): The beginning of the reporting period.

            end_date (str): The end of the reporting period.

        Extra `kwargs` are passed through as a POST json body.

        By default, requests a report with the following configuration:
            * `billable=True`
            * `rounding=1` (True, but this is an int param)
            * `rounding_minutes=15`

        See https://engineering.toggl.com/docs/reports/detailed_reports#post-export-detailed-report.

        Returns:
            response (requests.Response): The HTTP response.
        """
        # ensure start_date precedes end_date
        start_date, end_date = min(start_date, end_date), max(start_date, end_date)
        start = start_date.strftime("%Y-%m-%d")
        end = end_date.strftime("%Y-%m-%d")

        # calculate a timeout based on the size of the reporting period in days
        # approximately 5 seconds per month of query size, with a minimum of 5 seconds
        range_days = (end_date - start_date).days
        current_timeout = self.timeout
        dynamic_timeout = int((max(30, range_days) / 30.0) * 5)
        self.timeout = max(current_timeout, dynamic_timeout)

        params = dict(
            billable=True,
            start_date=start,
            end_date=end,
            rounding=1,
            rounding_minutes=15,
        )
        params.update(kwargs)

        response = self.post_reports("search/time_entries.csv", **params)
        self.timeout = current_timeout

        return response


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
        client_name = os.environ.get("HARVEST_CLIENT_NAME")

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


def download_time_entries(
    start_date: datetime,
    end_date: datetime,
    output_path: str | TextIO = sys.stdout,
    output_cols: list[str] | None = INPUT_COLUMNS,
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
