from base64 import b64encode
from datetime import datetime

import requests

from compiler_admin import __version__


class TogglBase:
    """Base class for Toggl API clients.

    See https://engineering.toggl.com/docs/.

    Sub-classes should implement api_url_resource(self).
    """

    API_BASE_URL = "https://api.track.toggl.com"
    API_VERSION = "api/v9"
    API_HEADERS = {"Content-Type": "application/json", "User-Agent": "compilerla/compiler-admin:{}".format(__version__)}

    def __init__(self, api_token: str, workspace_id: int, **kwargs):
        self._token = api_token
        self.workspace_id = workspace_id

        self.headers = dict(TogglBase.API_HEADERS)
        self.headers.update(self._authorization_header())

        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.timeout = int(kwargs.get("timeout", 5))

    def _authorization_header(self):
        """Gets an `Authorization: Basic xyz` header using the Toggl API token.

        See https://engineering.toggl.com/docs/authentication.
        """
        creds = f"{self._token}:api_token"
        creds64 = b64encode(bytes(creds, "utf-8")).decode("utf-8")
        return {"Authorization": "Basic {}".format(creds64)}

    @property
    def api_url_resource(self):
        """Sub-classes should implement this prop to use make_api_url() for the given API resource."""
        raise NotImplementedError("Implement this property to use make_api_url().")

    @property
    def api_url_version(self):
        """The version information for an API request URL."""
        return self.API_VERSION

    def make_api_url(self, endpoint: str):
        """Get a fully formed and versioned URL for an endpoint within the Toggl API."""
        return "/".join((TogglBase.API_BASE_URL, self.api_url_version, self.api_url_resource, endpoint))


class TogglOrganization(TogglBase):
    ORGANIZATIONS_ID = "organizations/{}"

    def __init__(self, api_token, workspace_id, organization_id, **kwargs):
        super().__init__(api_token, workspace_id, **kwargs)
        self.organization_id = organization_id

    @property
    def api_url_resource(self):
        """The organizations portion of an API URL."""
        return self.ORGANIZATIONS_ID.format(self.organization_id)

    def get_users(self, **kwargs) -> requests.Response:
        """Request a list of users from the Toggl organization.

        See https://engineering.toggl.com/docs/track/api/organizations/#get-list-of-users-in-organization.

        Returns:
            response (requests.Response): The HTTP response.
        """
        url = self.make_api_url("users")

        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()

        return response


class TogglReports(TogglBase):
    REPORTS_API_VERSION = "reports/api/v3"
    WORKSPACE_ID = "workspace/{}"

    @property
    def api_url_resource(self):
        return self.WORKSPACE_ID.format(self.workspace_id)

    @property
    def api_url_version(self):
        return self.REPORTS_API_VERSION

    def detailed_time_entries(self, start_date: datetime, end_date: datetime, **kwargs) -> requests.Response:
        """Request a CSV report from Toggl of detailed time entries for the given date range.

        Args:
            start_date (datetime): The beginning of the reporting period.

            end_date (datetime): The end of the reporting period.

        Extra `kwargs` are passed through as a POST json body.

        By default, requests a report with the following configuration:
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
        url = self.make_api_url(endpoint)

        response = self.session.post(url, json=kwargs, timeout=self.timeout)
        response.raise_for_status()

        return response


class TogglWorkspace(TogglBase):
    WORKSPACES_ID = "workspaces/{}"

    @property
    def api_url_resource(self):
        """The workspaces portion of an API URL."""
        return self.WORKSPACES_ID.format(self.workspace_id)

    def get_users(self, **kwargs) -> requests.Response:
        """Request a list of users from the Toggl workspace.

        See https://engineering.toggl.com/docs/track/api/workspaces/#get-get-workspace-users.

        Returns:
            response (requests.Response): The HTTP response.
        """
        url = self.make_api_url("users")

        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()

        return response

    def update_preferences(self, **kwargs) -> requests.Response:
        """Update workspace preferences.

        See https://engineering.toggl.com/docs/api/preferences/#post-update-workspace-preferences.
        """
        url = self.make_api_url("preferences")

        response = self.session.post(url, json=kwargs, timeout=self.timeout)
        response.raise_for_status()

        return response
