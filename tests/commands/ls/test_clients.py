import pytest

from compiler_admin import Result
from compiler_admin.api.toggl import TogglWorkspace
from compiler_admin.commands.ls.clients import clients


@pytest.fixture
def mock_toggl_clients(mocker):
    return mocker.patch("compiler_admin.commands.ls.clients.TogglUtils").return_value


def test_clients(cli_runner, mock_toggl_clients):
    mock_toggl_clients.get_clients.return_value = [{"id": 1, "name": "Client A"}]

    result = cli_runner.invoke(clients, [])

    assert result.exit_code == Result.SUCCESS
    mock_toggl_clients.get_clients.assert_called_once_with(ids=None, name=None)
    assert "id,name" in result.output
    assert "Client A" in result.output


def test_clients_json_format(cli_runner, mock_workspace_get_clients):
    """JSON format uses Track API and returns detailed data."""
    result = cli_runner.invoke(clients, ["--format", "json"])

    assert result.exit_code == Result.SUCCESS
    assert "archived" in result.output
    assert "Test Client" in result.output


@pytest.fixture
def mock_workspace_get_clients(mocker):
    """Mock TogglWorkspace.get_clients for Track API detailed output."""
    mock_clients = [
        {
            "id": 1,
            "name": "Test Client",
            "archived": False,
            "at": "2024-01-01T00:00:00Z",
            "creator_id": 123,
            "external_reference": "EXT-001",
            "integration_ext_id": None,
            "integration_ext_type": None,
            "integration_provider": None,
            "notes": "Test client notes",
            "permissions": {"view": True, "edit": False},
            "total_count": 1,
            "wid": 789,
        },
    ]
    mock_response = mocker.Mock()
    mock_response.json.return_value = mock_clients
    mock = mocker.patch.object(TogglWorkspace, "get_clients")
    mock.return_value = mock_response
    return mock


def test_clients_csv_format(cli_runner, mock_workspace_get_clients):
    """CSV format uses Track API and returns detailed fields."""
    result = cli_runner.invoke(clients, ["--format", "csv"])

    assert result.exit_code == Result.SUCCESS
    assert "id" in result.output
    assert "name" in result.output
    assert "archived" in result.output
    assert "notes" in result.output
    assert "Test Client" in result.output


def test_clients_json_detailed(cli_runner, mock_workspace_get_clients):
    """JSON format uses Track API and returns detailed fields."""
    result = cli_runner.invoke(clients, ["--format", "json"])

    assert result.exit_code == Result.SUCCESS
    assert "archived" in result.output
    assert "notes" in result.output


def test_clients_csv_excludes_internal(cli_runner, mock_workspace_get_clients):
    """Detailed output excludes internal/auxiliary Track API fields."""
    result = cli_runner.invoke(clients, ["--format", "csv"])

    assert result.exit_code == Result.SUCCESS
    assert "total_count" not in result.output
    assert "permissions" not in result.output
    assert "wid" not in result.output


def test_clients_basic_no_track_api(cli_runner, mocker):
    """Verify that basic format uses Reports API, not Track API."""
    mock_utils = mocker.patch("compiler_admin.commands.ls.clients.TogglUtils").return_value
    mock_utils.get_clients.return_value = [{"id": 1, "name": "Mock Client"}]

    result = cli_runner.invoke(clients, [])

    assert result.exit_code == Result.SUCCESS
    mock_utils.get_clients.assert_called_once()
