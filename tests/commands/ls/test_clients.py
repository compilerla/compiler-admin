import json

import pytest

from compiler_admin import Result
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


def test_clients_json_format(cli_runner, mock_toggl_clients):
    mock_toggl_clients.get_clients.return_value = [{"id": 2, "name": "Client B"}]

    result = cli_runner.invoke(clients, ["--format", "json"])

    assert result.exit_code == Result.SUCCESS
    assert json.dumps(mock_toggl_clients.get_clients.return_value, indent=2) in result.output
