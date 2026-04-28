import pytest

from compiler_admin import Result
from compiler_admin.commands.user.reset import __name__ as MODULE, reset
from compiler_admin.commands.user.signout import signout


@pytest.fixture
def mock_ctx_forward(mocker):
    """Mock click.Context.forward."""
    return mocker.patch("click.Context.forward")


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


def test_reset__user_does_not_exist(cli_runner, mock_account_exists, mock_GoogleAccount):
    mock_account_exists(mock_GoogleAccount, False)

    result = cli_runner.invoke(reset, ["username"])

    assert result.exit_code != Result.SUCCESS
    assert "User does not exist" in result.output


@pytest.mark.usefixtures("mock_input_yes")
def test_reset__confirm_yes(cli_runner, mocker, mock_account_exists, mock_ctx_forward, mock_GoogleAccount, mock_GoogleUsers):
    mock_account_exists(mock_GoogleAccount, True)

    result = cli_runner.invoke(reset, ["username"])

    assert result.exit_code == Result.SUCCESS
    mock_GoogleUsers.reset_password.assert_called_once_with(account=mock_GoogleAccount, notify=None)
    assert mocker.call(signout) in mock_ctx_forward.mock_calls


@pytest.mark.usefixtures("mock_input_no")
def test_reset__confirm_no(cli_runner, mocker, mock_account_exists, mock_ctx_forward, mock_GoogleAccount, mock_GoogleUsers):
    mock_account_exists(mock_GoogleAccount, True)

    result = cli_runner.invoke(reset, ["username"])

    assert result.exit_code == Result.SUCCESS
    mock_GoogleUsers.reset_password.assert_not_called()
    assert mocker.call(signout) not in mock_ctx_forward.mock_calls


def test_reset__force(cli_runner, mocker, mock_account_exists, mock_ctx_forward, mock_GoogleAccount, mock_GoogleUsers):
    mock_account_exists(mock_GoogleAccount, True)

    result = cli_runner.invoke(reset, ["--force", "username"])

    assert result.exit_code == Result.SUCCESS
    mock_GoogleUsers.reset_password.assert_called_once_with(account=mock_GoogleAccount, notify=None)
    assert mocker.call(signout) in mock_ctx_forward.mock_calls


@pytest.mark.usefixtures("mock_input_yes")
def test_reset__notify(cli_runner, mocker, mock_account_exists, mock_ctx_forward, mock_GoogleAccount, mock_GoogleUsers):
    mock_account_exists(mock_GoogleAccount, True)

    result = cli_runner.invoke(reset, ["--notify", "notification@example.com", "username"])

    assert result.exit_code == Result.SUCCESS
    mock_GoogleUsers.reset_password.assert_called_once_with(account=mock_GoogleAccount, notify="notification@example.com")
    assert mocker.call(signout) in mock_ctx_forward.mock_calls
