from base64 import b64encode
from datetime import datetime

import requests

from compiler_admin import __version__


class TogglBase:
    """Base class for Toggl API clients.

    See https://engineering.toggl.com/docs/.

    Sub-classes should implement `api_url_resource(self)`.
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

    def _get(self, url: str, **kwargs) -> requests.Response:
        response = self.session.get(url, params=kwargs, timeout=self.timeout)
        response.raise_for_status()
        return response

    def _post(self, url: str, **kwargs) -> requests.Response:
        response = self.session.post(url, json=kwargs, timeout=self.timeout)
        response.raise_for_status()
        return response


class TogglOrganization(TogglBase):
    ORGANIZATIONS_ID = "organizations/{}"

    def __init__(self, api_token, workspace_id, organization_id, **kwargs):
        super().__init__(api_token, workspace_id, **kwargs)
        self.organization_id = organization_id

    @property
    def api_url_resource(self):
        """The organizations portion of an API URL."""
        return self.ORGANIZATIONS_ID.format(self.organization_id)

    def get_groups(self, name: str = None) -> requests.Response:
        """Request a list of groups from the Toggl organization.

        See
        https://engineering.toggl.com/docs/track/api/groups/#get-list-of-groups-in-organization-with-user-and-workspace-assignments.

        Args:
            name (str): Return groups with a name containing the provided value.

        Returns:
            response (requests.Response): The HTTP response.
        """
        kwargs = {"workspace": str(self.workspace_id)}
        if name:
            kwargs["name"] = name
        url = self.make_api_url("groups")

        return self._get(url, **kwargs)

    def get_users(self, **kwargs) -> requests.Response:
        """Request a list of users from the Toggl organization.

        See https://engineering.toggl.com/docs/track/api/organizations/#get-list-of-users-in-organization.

        Returns:
            response (requests.Response): The HTTP response.
        """
        kwargs["workspaces"] = str(self.workspace_id)
        url = self.make_api_url("users")

        return self._get(url, **kwargs)


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

        url = self.make_api_url("search/time_entries.csv")
        response = self._post(url, **params)
        self.timeout = current_timeout

        return response

    def list_clients(
        self, ids: list[int] | None = None, name: str | None = None, start: int | None = None
    ) -> requests.Response:
        """Request a filtered list of clients from Toggl Reports utils.

        Args:
            ids (list[int] | None): Optional client IDs to filter.
            name (str | None): Optional client name filter.
            start (int | None): Optional pagination cursor.

        Returns:
            requests.Response: The HTTP response.
        """
        params: dict[str, object] = {}
        if ids is not None:
            params["ids"] = ids
        if name is not None:
            params["name"] = name
        if start is not None:
            params["start"] = start

        url = self.make_api_url("filters/clients")
        return self._post(url, **params)

    def list_projects(
        self,
        client_ids: list[int] | None = None,
        currency: str | None = None,
        ids: list[int] | None = None,
        is_active: bool | None = None,
        is_billable: bool | None = None,
        is_private: bool | None = None,
        name: str | None = None,
        page_size: int | None = None,
        start: int | None = None,
    ) -> requests.Response:
        """Request a filtered list of projects from Toggl Reports utils.

        Args:
            client_ids (list[int] | None): Optional Toggl client IDs.
            currency (str | None): Optional currency filter.
            ids (list[int] | None): Optional project IDs.
            is_active (bool | None): Optional archived state filter.
            is_billable (bool | None): Optional billable filter.
            is_private (bool | None): Optional private filter.
            name (str | None): Optional project name filter.
            page_size (int | None): Optional page size.
            start (int | None): Optional pagination cursor.

        Returns:
            requests.Response: The HTTP response.
        """
        params: dict[str, object] = {}
        if client_ids is not None:
            params["client_ids"] = client_ids
        if currency is not None:
            params["currency"] = currency
        if ids is not None:
            params["ids"] = ids
        if is_active is not None:
            params["is_active"] = is_active
        if is_billable is not None:
            params["is_billable"] = is_billable
        if is_private is not None:
            params["is_private"] = is_private
        if name is not None:
            params["name"] = name
        if page_size is not None:
            params["page_size"] = page_size
        if start is not None:
            params["start"] = start

        url = self.make_api_url("filters/projects")
        return self._post(url, **params)

    def list_project_users(
        self,
        client_ids: list[int] | None = None,
        project_ids: list[int] | None = None,
        start_id: int | None = None,
    ) -> requests.Response:
        """Request a filtered list of project users from Toggl Reports utils.

        Args:
            client_ids (list[int] | None): Optional client IDs.
            project_ids (list[int] | None): Optional project IDs.
            start_id (int | None): Optional pagination cursor.

        Returns:
            requests.Response: The HTTP response.
        """
        params: dict[str, object] = {}
        if client_ids is not None:
            params["client_ids"] = client_ids
        if project_ids is not None:
            params["project_ids"] = project_ids
        if start_id is not None:
            params["start_id"] = start_id

        url = self.make_api_url("filters/project_users")
        return self._post(url, **params)


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

        return self._get(url, **kwargs)

    def update_preferences(self, **kwargs) -> requests.Response:
        """Update workspace preferences.

        See https://engineering.toggl.com/docs/api/preferences/#post-update-workspace-preferences.
        """
        url = self.make_api_url("preferences")

        return self._post(url, **kwargs)
