import pytest

from compiler_admin import RESULT_SUCCESS
from compiler_admin.commands.user.create import create, __name__ as MODULE
from compiler_admin.services.google import USER_HELLO


@pytest.fixture
def mock_google_user_exists(mock_google_user_exists):
    return mock_google_user_exists(MODULE)


@pytest.fixture
def mock_google_CallGAMCommand(mock_google_CallGAMCommand):
    return mock_google_CallGAMCommand(MODULE)


@pytest.fixture
def mock_google_add_user_to_group(mock_google_add_user_to_group):
    return mock_google_add_user_to_group(MODULE)


def test_create_user_exists(cli_runner, mock_google_user_exists):
    mock_google_user_exists.return_value = True

    result = cli_runner.invoke(create, ["username"])

    assert result.exit_code != RESULT_SUCCESS


def test_create_user_does_not_exists(
    cli_runner, mock_google_user_exists, mock_google_CallGAMCommand, mock_google_add_user_to_group
):
    mock_google_user_exists.return_value = False

    result = cli_runner.invoke(create, ["username"])

    assert result.exit_code == RESULT_SUCCESS

    mock_google_CallGAMCommand.assert_called_once()
    call_args = " ".join(mock_google_CallGAMCommand.call_args[0][0])
    assert "create user" in call_args
    assert "password random changepassword" in call_args

    mock_google_add_user_to_group.assert_called_once()


def test_create_user_notify(cli_runner, mock_google_user_exists, mock_google_CallGAMCommand, mock_google_add_user_to_group):
    mock_google_user_exists.return_value = False

    result = cli_runner.invoke(create, ["--notify", "notification@example.com", "username"])

    assert result.exit_code == RESULT_SUCCESS

    mock_google_CallGAMCommand.assert_called_once()
    call_args = " ".join(mock_google_CallGAMCommand.call_args[0][0])
    assert "create user" in call_args
    assert "password random changepassword" in call_args
    assert f"notify notification@example.com from {USER_HELLO}" in call_args

    mock_google_add_user_to_group.assert_called_once()


def test_create_user_extras(cli_runner, mock_google_user_exists, mock_google_CallGAMCommand, mock_google_add_user_to_group):
    mock_google_user_exists.return_value = False

    result = cli_runner.invoke(create, ["username", "extra1", "extra2"])

    assert result.exit_code == RESULT_SUCCESS

    mock_google_CallGAMCommand.assert_called_once()
    call_args = " ".join(mock_google_CallGAMCommand.call_args[0][0])
    assert "create user" in call_args
    assert "password random changepassword" in call_args
    assert "extra1 extra2" in call_args

    mock_google_add_user_to_group.assert_called_once()
