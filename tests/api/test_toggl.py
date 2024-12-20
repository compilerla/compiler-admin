from datetime import datetime
from pathlib import Path

import pytest

from compiler_admin import __version__
from compiler_admin.api.toggl import __name__ as MODULE, Toggl


@pytest.fixture
def mock_requests(mocker):
    return mocker.patch(f"{MODULE}.requests.Session").return_value


@pytest.fixture
def toggl():
    return Toggl("token", 1234)


@pytest.fixture
def toggl_mock_post_reports(mocker, toggl, toggl_file):
    # setup a mock response to a requests.post call
    mock_csv_bytes = Path(toggl_file).read_bytes()
    mock_post_response = mocker.Mock()
    mock_post_response.raise_for_status.return_value = None
    # prepend the BOM to the mock content
    mock_post_response.content = b"\xef\xbb\xbf" + mock_csv_bytes
    # override the requests.post call to return the mock response
    mocker.patch.object(toggl, "post_reports", return_value=mock_post_response)
    return toggl


def test_toggl_init(toggl):
    token64 = "dG9rZW46YXBpX3Rva2Vu"

    assert toggl._token == "token"
    assert toggl.workspace_id == 1234
    assert toggl.workspace_url_fragment == "workspace/1234"

    assert toggl.headers["Content-Type"] == "application/json"

    user_agent = toggl.headers["User-Agent"]
    assert "compilerla/compiler-admin" in user_agent
    assert __version__ in user_agent

    assert toggl.headers["Authorization"] == f"Basic {token64}"

    assert toggl.timeout == 5


def test_toggl_make_report_url(toggl):
    url = toggl._make_report_url("endpoint")

    assert url.startswith(toggl.API_BASE_URL)
    assert toggl.API_REPORTS_BASE_URL in url
    assert toggl.workspace_url_fragment in url
    assert "/endpoint" in url


def test_toggl_post_reports(mock_requests, toggl):
    url = toggl._make_report_url("endpoint")
    response = toggl.post_reports("endpoint", kwarg1=1, kwarg2="two")

    response.raise_for_status.assert_called_once()

    mock_requests.post.assert_called_once_with(url, json=dict(kwarg1=1, kwarg2="two"), timeout=toggl.timeout)


def test_toggl_detailed_time_entries(toggl_mock_post_reports):
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


def test_toggl_detailed_time_entries_dynamic_timeout(mock_requests, toggl):
    # range of 6 months
    # timeout should be 6 * 5 = 30
    start = datetime(2024, 1, 1)
    end = datetime(2024, 6, 30)
    toggl.detailed_time_entries(start, end)

    mock_requests.post.assert_called_once()
    assert mock_requests.post.call_args.kwargs["timeout"] == 30
