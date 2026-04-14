import pytest

from compiler_admin import Result
from compiler_admin.commands.user.backupcodes import __name__ as MODULE, backupcodes


@pytest.fixture
def mock_google_user_exists(mock_google_user_exists):
    return mock_google_user_exists(MODULE)


@pytest.fixture
def mock_get_backup_codes(mocker):
    return mocker.patch(f"{MODULE}.get_backup_codes")


def test_backupcodes_user_does_not_exist(cli_runner, mock_google_user_exists, mock_get_backup_codes):
    mock_google_user_exists.return_value = False

    result = cli_runner.invoke(backupcodes, ["username"])

    assert result.exit_code == Result.FAILURE
    mock_get_backup_codes.assert_not_called()


def test_backupcodes_user_exists(cli_runner, mock_google_user_exists, mock_get_backup_codes):
    mock_google_user_exists.return_value = True
    mock_get_backup_codes.return_value = "1234"

    result = cli_runner.invoke(backupcodes, ["username"])

    assert result.exit_code == Result.SUCCESS
    mock_get_backup_codes.assert_called_once()
