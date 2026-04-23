import pytest

from compiler_admin import Result
from compiler_admin.commands.user.deactivate import __name__ as MODULE, deactivate
from compiler_admin.commands.user.reset import reset


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
    mock = mocker.patch(f"{MODULE}.GoogleAccount").return_value
    mock.is_deactivated.return_value = False
    return mock


@pytest.fixture
def mock_GoogleOrgs(mocker):
    return mocker.patch(f"{MODULE}.GoogleOrgs")


@pytest.fixture
def mock_GoogleUsers(mocker):
    return mocker.patch(f"{MODULE}.GoogleUsers").return_value


def test_deactivate__user_does_not_exists(cli_runner, mock_account_exists, mock_GoogleAccount):
    mock_account_exists(mock_GoogleAccount, False)

    result = cli_runner.invoke(deactivate, ["username"])

    assert result.exit_code != Result.SUCCESS
    assert result.exception
    assert "User does not exist" in result.output


def test_deactivate__user_deactivated(cli_runner, mock_account_exists, mock_GoogleAccount):
    mock_account_exists(mock_GoogleAccount, True)
    mock_GoogleAccount.is_deactivated.return_value = True

    result = cli_runner.invoke(deactivate, ["username"])

    assert result.exit_code != Result.SUCCESS
    assert result.exception
    assert "User is already deactivated" in result.output


@pytest.mark.usefixtures("mock_input_yes")
def test_deactivate__confirm_yes(
    cli_runner, mocker, mock_account_exists, mock_ctx_forward, mock_GoogleAccount, mock_GoogleOrgs, mock_GoogleUsers
):
    mock_account_exists(mock_GoogleAccount, True)
    mock_orgs = mock_GoogleOrgs.return_value

    result = cli_runner.invoke(deactivate, ["username"])

    assert result.exit_code == Result.SUCCESS
    mock_orgs.move_user.assert_called_once_with(mock_GoogleAccount, mock_GoogleOrgs.OU_ALUMNI)
    mock_GoogleUsers.remove_from_groups.assert_called_once_with(mock_GoogleAccount)
    assert mocker.call(reset) in mock_ctx_forward.mock_calls
    mock_GoogleUsers.clear_profile.assert_called_once_with(mock_GoogleAccount)
    mock_GoogleUsers.reset_recovery_info.assert_called_once_with(
        account=mock_GoogleAccount, recovery_email="", recovery_phone=""
    )
    mock_GoogleUsers.disable_2fa.assert_called_once_with(mock_GoogleAccount)


@pytest.mark.usefixtures("mock_input_no")
def test_deactivate__confirm_no(
    cli_runner, mock_account_exists, mock_ctx_forward, mock_GoogleAccount, mock_GoogleOrgs, mock_GoogleUsers
):
    mock_account_exists(mock_GoogleAccount, True)
    mock_orgs = mock_GoogleOrgs.return_value

    result = cli_runner.invoke(deactivate, ["username"])

    assert result.exit_code == Result.SUCCESS
    mock_orgs.move_user.assert_not_called()
    mock_GoogleUsers.remove_from_groups.assert_not_called()
    mock_ctx_forward.assert_not_called()
    mock_GoogleUsers.clear_profile.assert_not_called()
    mock_GoogleUsers.reset_recovery_info.assert_not_called()
    mock_GoogleUsers.disable_2fa.assert_not_called()


def test_deactivate__force(
    cli_runner, mocker, mock_account_exists, mock_ctx_forward, mock_GoogleAccount, mock_GoogleOrgs, mock_GoogleUsers
):
    mock_account_exists(mock_GoogleAccount, True)
    mock_orgs = mock_GoogleOrgs.return_value

    result = cli_runner.invoke(deactivate, ["username", "--force"])

    assert result.exit_code == Result.SUCCESS
    mock_orgs.move_user.assert_called_once_with(mock_GoogleAccount, mock_GoogleOrgs.OU_ALUMNI)
    mock_GoogleUsers.remove_from_groups.assert_called_once_with(mock_GoogleAccount)
    assert mocker.call(reset) in mock_ctx_forward.mock_calls
    mock_GoogleUsers.clear_profile.assert_called_once_with(mock_GoogleAccount)
    mock_GoogleUsers.reset_recovery_info.assert_called_once_with(
        account=mock_GoogleAccount, recovery_email="", recovery_phone=""
    )
    mock_GoogleUsers.disable_2fa.assert_called_once_with(mock_GoogleAccount)
