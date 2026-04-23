import pytest

from compiler_admin import Result
from compiler_admin.commands.user.deactivate import deactivate
from compiler_admin.commands.user.delete import delete
from compiler_admin.commands.user.offboard import __name__ as MODULE, offboard


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
def mock_GoogleArchive(mocker):
    return mocker.patch(f"{MODULE}.GoogleArchive").return_value


@pytest.fixture
def mock_GoogleUsers(mocker):
    return mocker.patch(f"{MODULE}.GoogleUsers").return_value


@pytest.mark.usefixtures("mock_ctx_forward", "mock_input_yes", "mock_GoogleArchive", "mock_GoogleUsers")
def test_offboard__alias(cli_runner, mock_GoogleAccount):
    mock_GoogleAccount.exists.return_value = True

    result = cli_runner.invoke(offboard, ["--alias", "alias_username", "username"])

    assert result.exit_code == Result.SUCCESS
    mock_GoogleAccount.add_email_alias.assert_called_once_with(mock_GoogleAccount)


def test_offboard__alias__user_does_not_exist(cli_runner, mock_GoogleAccount):
    # the first call returns True (the user exists), the second False (the alias user does not exist)
    # https://stackoverflow.com/a/24897297
    mock_GoogleAccount.exists.side_effect = [True, False]

    result = cli_runner.invoke(offboard, ["--alias", "alias_username", "username"])

    assert result.exit_code != Result.SUCCESS
    assert "Alias target user does not exist" in result.output


@pytest.mark.usefixtures("mock_input_yes")
@pytest.mark.parametrize("should_delete", [True, False])
def test_offboard__confirm_yes(
    cli_runner,
    mocker,
    mock_account_exists,
    mock_ctx_forward,
    mock_GoogleAccount,
    mock_GoogleArchive,
    mock_GoogleUsers,
    should_delete,
):
    mock_account_exists(mock_GoogleAccount, True)

    args = ["username"]
    if should_delete:
        args.append("--delete")

    result = cli_runner.invoke(offboard, args)

    assert result.exit_code == Result.SUCCESS
    assert mocker.call(deactivate) in mock_ctx_forward.mock_calls
    mock_GoogleArchive.create_email_backup.assert_called_once_with(mock_GoogleAccount)
    mock_GoogleArchive.archive_content.assert_called_once_with(mock_GoogleAccount)
    mock_GoogleArchive.await_archive_completion.assert_called_once()
    mock_GoogleUsers.deprovision_popimap.assert_called_once_with(mock_GoogleAccount)

    if should_delete:
        assert mocker.call(delete) in mock_ctx_forward.mock_calls
    else:
        assert mocker.call(delete) not in mock_ctx_forward.mock_calls


@pytest.mark.usefixtures("mock_input_no")
def test_offboard__confirm_no(cli_runner, mocker, mock_ctx_forward, mock_GoogleAccount, mock_GoogleArchive, mock_GoogleUsers):
    mock_GoogleAccount.return_value = True

    result = cli_runner.invoke(offboard, ["username"])

    assert result.exit_code == Result.SUCCESS
    assert mocker.call(deactivate) not in mock_ctx_forward.mock_calls
    mock_GoogleArchive.create_email_backup.assert_not_called()
    mock_GoogleArchive.archive_content.assert_not_called()
    mock_GoogleArchive.await_archive_completion.assert_not_called()
    mock_GoogleUsers.deprovision_popimap.assert_not_called()
    assert mocker.call(delete) not in mock_ctx_forward.mock_calls


def test_offboard__force(
    cli_runner, mocker, mock_account_exists, mock_ctx_forward, mock_GoogleAccount, mock_GoogleArchive, mock_GoogleUsers
):
    mock_account_exists(mock_GoogleAccount, True)

    args = ["username", "--force"]
    result = cli_runner.invoke(offboard, args)

    assert result.exit_code == Result.SUCCESS
    assert mocker.call(deactivate) in mock_ctx_forward.mock_calls
    mock_GoogleArchive.create_email_backup.assert_called_once_with(mock_GoogleAccount)
    mock_GoogleArchive.archive_content.assert_called_once_with(mock_GoogleAccount)
    mock_GoogleArchive.await_archive_completion.assert_called_once()
    mock_GoogleUsers.deprovision_popimap.assert_called_once_with(mock_GoogleAccount)


def test_offboard__user_does_not_exist(
    cli_runner, mocker, mock_account_exists, mock_ctx_forward, mock_GoogleAccount, mock_GoogleArchive, mock_GoogleUsers
):
    mock_account_exists(mock_GoogleAccount, False)

    result = cli_runner.invoke(offboard, ["username"])

    assert result.exit_code != Result.SUCCESS
    assert "User does not exist" in result.output
    assert mocker.call(deactivate) not in mock_ctx_forward.mock_calls
    mock_GoogleArchive.create_email_backup.assert_not_called()
    mock_GoogleArchive.archive_content.assert_not_called()
    mock_GoogleArchive.await_archive_completion.assert_not_called()
    mock_GoogleUsers.deprovision_popimap.assert_not_called()
    assert mocker.call(delete) not in mock_ctx_forward.mock_calls
