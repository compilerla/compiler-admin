import pytest

from compiler_admin import Result
from compiler_admin.commands.user.signout import __name__ as MODULE, signout


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


@pytest.mark.usefixtures("mock_input_yes")
def test_signout__confirm_yes(cli_runner, mock_account_exists, mock_GoogleAccount, mock_GoogleUsers):
    mock_account_exists(mock_GoogleAccount, True)

    result = cli_runner.invoke(signout, ["username"])

    assert result.exit_code == Result.SUCCESS
    mock_GoogleUsers.signout.assert_called_once_with(mock_GoogleAccount)


@pytest.mark.usefixtures("mock_input_no")
def test_signout__confirm_no(cli_runner, mock_account_exists, mock_GoogleAccount, mock_GoogleUsers):
    mock_account_exists(mock_GoogleAccount, True)

    result = cli_runner.invoke(signout, ["username"])

    assert result.exit_code == Result.SUCCESS
    mock_GoogleUsers.signout.assert_not_called()


def test_signout__force(cli_runner, mock_account_exists, mock_GoogleAccount, mock_GoogleUsers):
    mock_account_exists(mock_GoogleAccount, True)

    result = cli_runner.invoke(signout, ["--force", "username"])

    assert result.exit_code == Result.SUCCESS
    mock_GoogleUsers.signout.assert_called_once_with(mock_GoogleAccount)


def test_signout__user_does_not_exist(cli_runner, mock_account_exists, mock_GoogleAccount, mock_GoogleUsers):
    mock_account_exists(mock_GoogleAccount, False)

    result = cli_runner.invoke(signout, ["username"])

    assert result.exit_code != Result.SUCCESS
    assert "User does not exist" in result.output
    mock_GoogleUsers.signout.assert_not_called()
