from base64 import b64encode
from datetime import datetime

import requests

from compiler_admin import __version__


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

    def post_reports(self, endpoint: str, **kwargs) -> requests.Response:
        """Send a POST request to the Reports v3 `endpoint`.

        Extra `kwargs` are passed through as a POST json body.

        Will raise for non-200 status codes.

        See https://engineering.toggl.com/docs/reports_start.
        """
        url = self._make_report_url(endpoint)

        response = requests.post(url, json=kwargs, timeout=self.timeout)
        response.raise_for_status()

        return response
