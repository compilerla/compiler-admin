from datetime import datetime
from pathlib import Path

import pytest

from compiler_admin import __version__
from compiler_admin.api.toggl import TogglBase, TogglOrganization, TogglReports, TogglWorkspace, __name__ as MODULE


@pytest.fixture(autouse=True)
def mock_requests(mocker):
    return mocker.patch(f"{MODULE}.requests.Session").return_value


class TestTogglBase:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.toggl = TogglBase("token", 1234)

    def test_init(self):
        assert self.toggl.workspace_id == 1234

        token64 = "dG9rZW46YXBpX3Rva2Vu"
        assert self.toggl._token == "token"
        assert self.toggl.headers["Authorization"] == f"Basic {token64}"

        assert self.toggl.headers["Content-Type"] == "application/json"

        user_agent = self.toggl.headers["User-Agent"]
        assert "compilerla/compiler-admin" in user_agent
        assert __version__ in user_agent

        assert self.toggl.timeout == 5

    def test_api_url_resource(self):
        with pytest.raises(NotImplementedError):
            assert self.toggl.api_url_resource

    def test_api_url_version(self):
        assert self.toggl.api_url_version == self.toggl.API_VERSION

    def test_make_api_url(self):
        class TogglTest(TogglBase):
            @property
            def api_url_resource(self):
                return "resource"

        self.toggl = TogglTest(self.toggl._token, self.toggl.workspace_id)

        url = self.toggl.make_api_url("endpoint")

        assert url.startswith(self.toggl.API_BASE_URL)
        assert self.toggl.api_url_version in url
        assert self.toggl.api_url_resource in url
        assert "/endpoint" in url


class TestTogglOrganization:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.toggl = TogglOrganization("token", 1234, 5678)

    def test_init(self):
        assert self.toggl.organization_id == 5678

    def test_api_url_resource(self):
        assert self.toggl.api_url_resource == "organizations/5678"

    def test_get_users(self, mock_requests):
        url = self.toggl.make_api_url("users")
        kwargs = dict(kwarg1=1, kwarg2="two")
        call_kwargs = dict(workspaces="1234", **kwargs)

        response = self.toggl.get_users(**kwargs)

        response.raise_for_status.assert_called_once()
        mock_requests.get.assert_called_once_with(url, params=call_kwargs, timeout=self.toggl.timeout)


class TestTogglReports:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.toggl = TogglReports("token", 1234)

    @pytest.fixture
    def toggl_mock_post_reports(self, mocker, toggl_file):
        # setup a mock response to a requests.post call
        mock_csv_bytes = Path(toggl_file).read_bytes()
        mock_post_response = mocker.Mock()
        mock_post_response.raise_for_status.return_value = None
        # prepend the BOM to the mock content
        mock_post_response.content = b"\xef\xbb\xbf" + mock_csv_bytes
        # override the requests.post call to return the mock response
        mocker.patch.object(self.toggl, "post_reports", return_value=mock_post_response)
        return self.toggl

    def test_api_url_resource(self):
        assert self.toggl.api_url_resource == "workspace/1234"

    def test_api_url_version(self):
        assert self.toggl.api_url_version == self.toggl.REPORTS_API_VERSION

    def test_toggl_post_reports(self, mock_requests):
        url = self.toggl.make_api_url("endpoint")
        response = self.toggl.post_reports("endpoint", kwarg1=1, kwarg2="two")

        response.raise_for_status.assert_called_once()

        mock_requests.post.assert_called_once_with(url, json=dict(kwarg1=1, kwarg2="two"), timeout=self.toggl.timeout)

    def test_toggl_detailed_time_entries(self, toggl_mock_post_reports):
        dt = datetime(2024, 9, 25)
        toggl_mock_post_reports.detailed_time_entries(dt, dt, kwarg1=1, kwarg2="two")

        toggl_mock_post_reports.post_reports.assert_called_once_with(
            "search/time_entries.csv",
            start_date="2024-09-25",
            end_date="2024-09-25",
            rounding=1,
            rounding_minutes=15,
            kwarg1=1,
            kwarg2="two",
        )

    def test_toggl_detailed_time_entries_dynamic_timeout(self, mock_requests):
        # range of 6 months
        # timeout should be 6 * 5 = 30
        start = datetime(2024, 1, 1)
        end = datetime(2024, 6, 30)
        self.toggl.detailed_time_entries(start, end)

        mock_requests.post.assert_called_once()
        assert mock_requests.post.call_args.kwargs["timeout"] == 30


class TestTogglWorkspace:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.toggl = TogglWorkspace("token", 1234)

    def test_api_url_resource(self):
        assert self.toggl.api_url_resource == "workspaces/1234"

    def test_get_users(self, mock_requests):
        url = self.toggl.make_api_url("users")
        kwargs = dict(kwarg1=1, kwarg2="two")

        response = self.toggl.get_users(**kwargs)

        response.raise_for_status.assert_called_once()
        mock_requests.get.assert_called_once_with(url, params=kwargs, timeout=self.toggl.timeout)

    def test_update_preferences(self, mocker, mock_requests):
        url = "http://fake.url"
        mocker.patch.object(self.toggl, "make_api_url", return_value=url)
        prefs = {"pref1": "value1", "pref2": True}

        response = self.toggl.update_preferences(**prefs)

        response.raise_for_status.assert_called_once()
        self.toggl.make_api_url.assert_called_once_with("preferences")
        mock_requests.post.assert_called_once_with(url, json=prefs, timeout=self.toggl.timeout)
