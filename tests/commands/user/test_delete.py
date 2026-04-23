import pytest

from compiler_admin import Result
from compiler_admin.commands.user.delete import __name__ as MODULE, delete


@pytest.fixture
def mock_input_yes(mock_input_yes):
    return mock_input_yes(MODULE)


@pytest.fixture
def mock_input_no(mock_input_no):
    return mock_input_no(MODULE)


@pytest.fixture
def mock_GoogleAccount(mocker):
    return mocker.patch(f"{MODULE}.GoogleAccount").return_value


@pytest.fixture
def mock_GoogleUsers(mocker):
    return mocker.patch(f"{MODULE}.GoogleUsers").return_value


@pytest.mark.usefixtures("mock_input_no")
def test_delete__confirm_no(cli_runner, mock_account_exists, mock_GoogleAccount, mock_GoogleUsers):
    mock_account_exists(mock_GoogleAccount, True)

    result = cli_runner.invoke(delete, ["username"])

    assert result.exit_code == Result.SUCCESS
    mock_GoogleUsers.delete.assert_not_called()


@pytest.mark.usefixtures("mock_input_yes")
def test_delete__confirm_yes(cli_runner, mock_account_exists, mock_GoogleAccount, mock_GoogleUsers):
    mock_account_exists(mock_GoogleAccount, True)

    result = cli_runner.invoke(delete, ["username"])

    assert result.exit_code == Result.SUCCESS
    mock_GoogleUsers.delete.assert_called_once_with(mock_GoogleAccount)


def test_delete__force(cli_runner, mock_account_exists, mock_GoogleAccount, mock_GoogleUsers):
    mock_account_exists(mock_GoogleAccount, True)

    result = cli_runner.invoke(delete, ["--force", "username"])

    assert result.exit_code == Result.SUCCESS
    mock_GoogleUsers.delete.assert_called_once_with(mock_GoogleAccount)


def test_delete__user_does_not_exist(cli_runner, mock_account_exists, mock_GoogleAccount, mock_GoogleUsers):
    mock_account_exists(mock_GoogleAccount, False)

    result = cli_runner.invoke(delete, ["username"])

    assert result.exit_code != Result.SUCCESS
    assert "User does not exist" in result.output
    mock_GoogleUsers.delete.assert_not_called()
