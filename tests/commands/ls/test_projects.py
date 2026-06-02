import pytest

from compiler_admin import Result
from compiler_admin.commands.ls.projects import projects


@pytest.fixture
def mock_toggl_projects(mocker):
    return mocker.patch("compiler_admin.commands.ls.projects.TogglUtils").return_value


def test_projects(cli_runner, mock_toggl_projects):
    mock_toggl_projects.get_projects.return_value = [
        {"id": 11, "name": "Project A", "client_id": 1, "active": True, "billable": False, "private": False}
    ]

    result = cli_runner.invoke(
        projects,
        ["--client-id", "1", "--id", "11", "--name", "Project A", "--active", "--internal"],
    )

    assert result.exit_code == Result.SUCCESS
    mock_toggl_projects.get_projects.assert_called_once_with(
        client_ids=[1],
        ids=[11],
        is_active=True,
        is_billable=False,
        is_private=True,
        name="Project A",
    )
    assert "Project A" in result.output
