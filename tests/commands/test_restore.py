import pytest
from compiler_admin.commands import RESULT_FAILURE, RESULT_SUCCESS

from compiler_admin.commands.restore import restore, __name__ as MODULE


@pytest.fixture
def mock_Path_exists(mocker):
    return mocker.patch(f"{MODULE}.pathlib.Path.exists")


@pytest.fixture
def mock_google_CallGYBCommand(mock_google_CallGYBCommand):
    return mock_google_CallGYBCommand(MODULE)


def test_restore_backup_exists(mock_Path_exists, mock_google_CallGYBCommand):
    mock_Path_exists.return_value = True

    res = restore("username")

    assert res == RESULT_SUCCESS
    mock_google_CallGYBCommand.assert_called_once()


def test_restore_backup_does_not_exist(mocker, mock_Path_exists, mock_google_CallGYBCommand):
    mock_Path_exists.return_value = False

    res = restore("username")

    assert res == RESULT_FAILURE
    assert mock_google_CallGYBCommand.call_count == 0