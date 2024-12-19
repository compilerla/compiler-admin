import pytest

from compiler_admin import RESULT_SUCCESS
from compiler_admin.commands.user.restore import restore, __name__ as MODULE


@pytest.fixture
def mock_Path_exists(mocker):
    return mocker.patch(f"{MODULE}.pathlib.Path.exists")


@pytest.fixture
def mock_google_CallGYBCommand(mock_google_CallGYBCommand):
    return mock_google_CallGYBCommand(MODULE)


def test_restore_backup_exists(cli_runner, mock_Path_exists, mock_google_CallGYBCommand):
    mock_Path_exists.return_value = True

    result = cli_runner.invoke(restore, ["username"])

    assert result.exit_code == RESULT_SUCCESS
    mock_google_CallGYBCommand.assert_called_once()


def test_restore_backup_does_not_exist(cli_runner, mock_Path_exists, mock_google_CallGYBCommand):
    mock_Path_exists.return_value = False

    result = cli_runner.invoke(restore, ["username"])

    assert result.exit_code != RESULT_SUCCESS
    assert mock_google_CallGYBCommand.call_count == 0
