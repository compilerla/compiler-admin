import pytest

from compiler_admin import Result
from compiler_admin.commands.user.backupcodes import __name__ as MODULE, backupcodes


@pytest.fixture
def mock_GoogleAccount(mocker):
    return mocker.patch(f"{MODULE}.GoogleAccount").return_value


def test_backupcodes_user_does_not_exist(cli_runner, mock_account_exists, mock_GoogleAccount):
    mock_account_exists(mock_GoogleAccount, False)

    result = cli_runner.invoke(backupcodes, ["username"])

    assert result.exit_code == Result.FAILURE
    assert "User does not exist" in result.output
    mock_GoogleAccount.get_backup_codes.assert_not_called()


def test_backupcodes_user_exists(cli_runner, mock_account_exists, mock_GoogleAccount):
    mock_account_exists(mock_GoogleAccount, True)
    codes = "123456789"
    mock_GoogleAccount.get_backup_codes.return_value = codes

    result = cli_runner.invoke(backupcodes, ["username"])

    assert result.exit_code == Result.SUCCESS
    assert codes in result.output
    mock_GoogleAccount.get_backup_codes.assert_called_once()
