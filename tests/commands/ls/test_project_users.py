import pytest

from compiler_admin import Result
from compiler_admin.commands.ls.project_users import project_users


@pytest.fixture
def mock_toggl_project_users(mocker):
    return mocker.patch("compiler_admin.commands.ls.project_users.TogglUtils").return_value


def test_project_users(cli_runner, mock_toggl_project_users):
    mock_toggl_project_users.get_project_users.return_value = [
        {"id": 21, "group_id": 7, "project_id": 11, "user_id": 99, "hourly_rate": 120, "labour_cost": 80}
    ]

    result = cli_runner.invoke(project_users, ["--client-id", "1", "--project-id", "11"])

    assert result.exit_code == Result.SUCCESS
    mock_toggl_project_users.get_project_users.assert_called_once_with(
        client_ids=[1],
        project_ids=[11],
    )
    assert "group_id" in result.output
