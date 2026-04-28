import pytest

from compiler_admin import Result
from compiler_admin.commands.user.create import __name__ as MODULE, create


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


def test_create__user_exists(cli_runner, mock_account_exists, mock_GoogleAccount):
    mock_account_exists(mock_GoogleAccount, True)

    result = cli_runner.invoke(create, ["username"])

    assert result.exit_code != Result.SUCCESS
    assert "User already exists" in result.output


def test_create__user_does_not_exists(
    cli_runner, mock_account_exists, mock_GoogleAccount, mock_GoogleGroups, mock_GoogleUsers
):
    mock_account_exists(mock_GoogleAccount, False)

    result = cli_runner.invoke(create, ["username"])

    assert result.exit_code == Result.SUCCESS
    mock_GoogleUsers.create.assert_called_once_with(mock_GoogleAccount, None)
    mock_GoogleGroups.add_user.assert_called_once()


def test_create__notify(cli_runner, mock_account_exists, mock_GoogleAccount, mock_GoogleGroups, mock_GoogleUsers):
    mock_account_exists(mock_GoogleAccount, False)

    result = cli_runner.invoke(create, ["--notify", "notification@example.com", "username"])

    assert result.exit_code == Result.SUCCESS
    mock_GoogleUsers.create.assert_called_once_with(mock_GoogleAccount, "notification@example.com")
    mock_GoogleGroups.add_user.assert_called_once()


def test_create__extras(cli_runner, mock_account_exists, mock_GoogleAccount, mock_GoogleGroups, mock_GoogleUsers):
    mock_account_exists(mock_GoogleAccount, False)

    result = cli_runner.invoke(create, ["username", "extra1", "extra2"])

    assert result.exit_code == Result.SUCCESS
    mock_GoogleUsers.create.assert_called_once_with(mock_GoogleAccount, None, "extra1", "extra2")
    mock_GoogleGroups.add_user.assert_called_once()
