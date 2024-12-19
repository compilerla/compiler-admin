import pytest

from compiler_admin import RESULT_SUCCESS
from compiler_admin.commands.user.reset import reset, __name__ as MODULE
from compiler_admin.services.google import USER_HELLO


@pytest.fixture
def mock_input_yes(mock_input):
    fix = mock_input(MODULE)
    fix.return_value = "y"
    return fix


@pytest.fixture
def mock_input_no(mock_input):
    fix = mock_input(MODULE)
    fix.return_value = "n"
    return fix


@pytest.fixture
def mock_commands_signout(mock_commands_signout):
    return mock_commands_signout(MODULE)


@pytest.fixture
def mock_google_user_exists(mock_google_user_exists):
    return mock_google_user_exists(MODULE)


@pytest.fixture
def mock_google_CallGAMCommand(mock_google_CallGAMCommand):
    return mock_google_CallGAMCommand(MODULE)


def test_reset_user_does_not_exist(cli_runner, mock_google_user_exists):
    mock_google_user_exists.return_value = False

    result = cli_runner.invoke(reset, ["username"])

    assert result.exit_code != RESULT_SUCCESS


@pytest.mark.usefixtures("mock_input_yes")
def test_reset_confirm_yes(cli_runner, mock_google_user_exists, mock_google_CallGAMCommand, mock_commands_signout):
    mock_google_user_exists.return_value = True

    result = cli_runner.invoke(reset, ["username"])

    assert result.exit_code == RESULT_SUCCESS
    mock_google_CallGAMCommand.assert_called_once()
    mock_commands_signout.callback.assert_called_once()


@pytest.mark.usefixtures("mock_input_no")
def test_reset_confirm_no(cli_runner, mock_google_user_exists, mock_google_CallGAMCommand, mock_commands_signout):
    mock_google_user_exists.return_value = True

    result = cli_runner.invoke(reset, ["username"])

    assert result.exit_code == RESULT_SUCCESS
    mock_google_CallGAMCommand.assert_not_called()
    mock_commands_signout.callback.assert_not_called()


def test_reset_user_exists(cli_runner, mock_google_user_exists, mock_google_CallGAMCommand, mock_commands_signout):
    mock_google_user_exists.return_value = True

    result = cli_runner.invoke(reset, ["--force", "username"])

    assert result.exit_code == RESULT_SUCCESS
    mock_google_CallGAMCommand.assert_called_once()
    call_args = " ".join(mock_google_CallGAMCommand.call_args[0][0])
    assert "update user" in call_args
    assert "password random changepassword" in call_args
    mock_commands_signout.callback.assert_called_once()


def test_reset_notify(cli_runner, mock_google_user_exists, mock_google_CallGAMCommand, mock_commands_signout):
    mock_google_user_exists.return_value = True

    result = cli_runner.invoke(reset, ["--force", "--notify", "notification@example.com", "username"])

    assert result.exit_code == RESULT_SUCCESS
    mock_google_CallGAMCommand.assert_called_once()
    call_args = " ".join(mock_google_CallGAMCommand.call_args[0][0])
    assert "update user" in call_args
    assert "password random changepassword" in call_args
    assert f"notify notification@example.com from {USER_HELLO}" in call_args
    mock_commands_signout.callback.assert_called_once()
