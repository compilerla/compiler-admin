import pytest

from compiler_admin import Result
from compiler_admin.commands.user.backupcodes import backupcodes
from compiler_admin.commands.user.reactivate import __name__ as MODULE, reactivate
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
    return mocker.patch(f"{MODULE}.GoogleAccount").return_value


@pytest.fixture
def mock_GoogleGroups(mocker):
    return mocker.patch(f"{MODULE}.GoogleGroups").return_value


@pytest.fixture
def mock_GoogleOrgs(mocker):
    return mocker.patch(f"{MODULE}.GoogleOrgs").return_value


@pytest.fixture
def mock_GoogleUsers(mocker):
    return mocker.patch(f"{MODULE}.GoogleUsers").return_value


@pytest.fixture(autouse=True)
def mock_account_exists__true(mock_account_exists, mock_GoogleAccount):
    mock_account_exists(mock_GoogleAccount, True)
    mock_GoogleAccount.is_deactivated.return_value = True


def test_reactivate_user_does_not_exist(cli_runner, mock_account_exists, mock_GoogleAccount):
    mock_account_exists(mock_GoogleAccount, False)

    result = cli_runner.invoke(reactivate, ["username"])

    assert result.exit_code != Result.SUCCESS
    assert "User does not exist" in result.output


def test_reactivate__user_is_not_deactivated(cli_runner, mock_GoogleAccount):
    mock_GoogleAccount.is_deactivated.return_value = False

    result = cli_runner.invoke(reactivate, ["username"])

    assert result.exit_code != Result.SUCCESS
    assert "User is not deactivated, cannot reactivate" in result.output


@pytest.mark.usefixtures("mock_input_no")
def test_reactivate__confirm_no(cli_runner):
    result = cli_runner.invoke(reactivate, ["username"])

    assert result.exit_code == Result.SUCCESS
    assert "Aborting reactivation" in result.output


@pytest.mark.usefixtures("mock_input_yes")
def test_reactivate__confirm_yes(mocker, cli_runner, mock_ctx_forward, mock_GoogleAccount, mock_GoogleGroups, mock_GoogleOrgs):
    result = cli_runner.invoke(reactivate, ["username"])

    assert result.exit_code == Result.SUCCESS
    mock_GoogleGroups.add_user.assert_called_once_with(mock_GoogleAccount)
    mock_GoogleOrgs.move_user.assert_called_once_with(mock_GoogleAccount)
    mock_ctx_forward.assert_has_calls([mocker.call(reset), mocker.call(backupcodes)])


def test_reactivate__force(mocker, cli_runner, mock_ctx_forward, mock_GoogleAccount, mock_GoogleGroups, mock_GoogleOrgs):
    result = cli_runner.invoke(reactivate, ["--force", "username"])

    assert result.exit_code == Result.SUCCESS
    mock_GoogleGroups.add_user.assert_called_once_with(mock_GoogleAccount)
    mock_GoogleOrgs.move_user.assert_called_once_with(mock_GoogleAccount)
    mock_ctx_forward.assert_has_calls([mocker.call(reset), mocker.call(backupcodes)])


def test_reactivate__staff(mocker, cli_runner, mock_ctx_forward, mock_GoogleAccount, mock_GoogleGroups, mock_GoogleOrgs):
    result = cli_runner.invoke(reactivate, ["--force", "--staff", "username"])

    assert result.exit_code == Result.SUCCESS
    mock_GoogleGroups.add_user.assert_has_calls([mocker.call(mock_GoogleAccount), mocker.call(mock_GoogleAccount)])
    mock_GoogleOrgs.move_user.assert_called_once_with(mock_GoogleAccount)
    mock_ctx_forward.assert_has_calls([mocker.call(reset), mocker.call(backupcodes)])


def test_reactivate__recovery_info(mocker, cli_runner, mock_ctx_forward, mock_GoogleAccount, mock_GoogleUsers):
    args = ["--force", "--recovery-email=foo@bar.com", "--recovery-phone=555-555-5555", "username"]
    result = cli_runner.invoke(reactivate, args)

    assert result.exit_code == Result.SUCCESS
    mock_GoogleUsers.reset_recovery_info.assert_called_once_with(
        account=mock_GoogleAccount, recovery_email="foo@bar.com", recovery_phone="555-555-5555"
    )
    mock_ctx_forward.assert_has_calls([mocker.call(reset), mocker.call(backupcodes)])
