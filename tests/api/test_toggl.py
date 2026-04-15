from datetime import datetime

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

    def test_get(self, mock_requests):
        url = "https://example.com"
        kwargs = dict(kwarg1=1, kwarg2="two")
        response = self.toggl._get(url, **kwargs)

        mock_requests.get.assert_called_once_with(url, params=kwargs, timeout=self.toggl.timeout)
        response.raise_for_status.assert_called_once()

    def test_post(self, mock_requests):
        url = "https://example.com"
        kwargs = dict(kwarg1=1, kwarg2="two")
        response = self.toggl._post(url, **kwargs)

        mock_requests.post.assert_called_once_with(url, json=kwargs, timeout=self.toggl.timeout)
        response.raise_for_status.assert_called_once()


class TestTogglOrganization:
    @pytest.fixture(autouse=True)
    def setup(self, mocker):
        self.toggl = TogglOrganization("token", 1234, 5678)
        self.get_spy = self.toggl._get = mocker.patch.object(self.toggl, "_get")

    def test_init(self):
        assert self.toggl.organization_id == 5678

    def test_api_url_resource(self):
        assert self.toggl.api_url_resource == "organizations/5678"

    def test_get_users(self):
        url = self.toggl.make_api_url("users")
        kwargs = dict(kwarg1=1, kwarg2="two")
        call_kwargs = dict(workspaces="1234", **kwargs)

        self.toggl.get_users(**kwargs)

        self.get_spy.assert_called_once_with(url, **call_kwargs)


class TestTogglReports:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.toggl = TogglReports("token", 1234)

    def test_api_url_resource(self):
        assert self.toggl.api_url_resource == "workspace/1234"

    def test_api_url_version(self):
        assert self.toggl.api_url_version == self.toggl.REPORTS_API_VERSION

    def test_toggl_detailed_time_entries(self, mocker):
        dt = datetime(2024, 9, 25)
        url = "https://api.track.toggl.com/reports/api/v3/workspace/1234/search/time_entries.csv"
        self.toggl._post = mocker.Mock()

        self.toggl.detailed_time_entries(dt, dt, kwarg1=1, kwarg2="two")

        self.toggl._post.assert_called_once_with(
            url,
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
    def setup(self, mocker):
        self.toggl = TogglWorkspace("token", 1234)
        self.get_spy = self.toggl._get = mocker.Mock()
        self.post_spy = self.toggl._post = mocker.Mock()

    def test_api_url_resource(self):
        assert self.toggl.api_url_resource == "workspaces/1234"

    def test_get_users(self):
        url = self.toggl.make_api_url("users")
        kwargs = dict(kwarg1=1, kwarg2="two")

        self.toggl.get_users(**kwargs)

        self.get_spy.assert_called_once_with(url, **kwargs)

    def test_update_preferences(self, mocker, mock_requests):
        url = "http://fake.url"
        mocker.patch.object(self.toggl, "make_api_url", return_value=url)
        prefs = {"pref1": "value1", "pref2": True}

        self.toggl.update_preferences(**prefs)

        self.toggl.make_api_url.assert_called_once_with("preferences")
        self.post_spy.assert_called_once_with(url, **prefs)
