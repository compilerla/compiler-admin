import pytest

from compiler_admin import RESULT_FAILURE, RESULT_SUCCESS
from compiler_admin.commands.user.alumni import alumni, __name__ as MODULE
from compiler_admin.services.google import OU_ALUMNI


@pytest.fixture
def mock_commands_reset(mock_commands_reset):
    return mock_commands_reset(MODULE)


@pytest.fixture
def mock_input_yes(mock_input_yes):
    return mock_input_yes(MODULE)


@pytest.fixture
def mock_input_no(mock_input_no):
    return mock_input_no(MODULE)


@pytest.fixture
def mock_google_CallGAMCommand(mock_google_CallGAMCommand):
    return mock_google_CallGAMCommand(MODULE)


@pytest.fixture
def mock_google_move_user_ou(mock_google_move_user_ou):
    return mock_google_move_user_ou(MODULE)


@pytest.fixture
def mock_google_remove_user_from_group(mock_google_remove_user_from_group):
    return mock_google_remove_user_from_group(MODULE)


@pytest.fixture
def mock_google_user_exists(mock_google_user_exists):
    return mock_google_user_exists(MODULE)


def test_alumni_user_does_not_exists(cli_runner, mock_google_user_exists, mock_google_CallGAMCommand):
    mock_google_user_exists.return_value = False

    result = cli_runner.invoke(alumni, ["username"])

    assert result.exit_code == RESULT_FAILURE
    assert result.exception
    assert "User does not exist: username@compiler.la" in result.output
    mock_google_CallGAMCommand.assert_not_called()


@pytest.mark.usefixtures("mock_input_yes")
def test_alumni_confirm_yes(
    cli_runner, mock_google_user_exists, mock_google_CallGAMCommand, mock_google_move_user_ou, mock_commands_reset
):
    mock_google_user_exists.return_value = True

    result = cli_runner.invoke(alumni, ["username"])

    assert result.exit_code == RESULT_SUCCESS
    mock_google_CallGAMCommand.assert_called()
    mock_google_move_user_ou.assert_called_once_with("username@compiler.la", OU_ALUMNI)


@pytest.mark.usefixtures("mock_input_no")
def test_alumni_confirm_no(
    cli_runner, mock_google_user_exists, mock_google_CallGAMCommand, mock_google_move_user_ou, mock_commands_reset
):
    mock_google_user_exists.return_value = True

    result = cli_runner.invoke(alumni, ["username"])

    assert result.exit_code == RESULT_SUCCESS
    mock_google_CallGAMCommand.assert_not_called()
    mock_google_move_user_ou.assert_not_called()


def test_alumni_force(
    cli_runner, mock_google_user_exists, mock_google_CallGAMCommand, mock_google_move_user_ou, mock_commands_reset
):
    mock_google_user_exists.return_value = True

    result = cli_runner.invoke(alumni, ["--force", "username"])

    assert result.exit_code == RESULT_SUCCESS
    mock_google_CallGAMCommand.assert_called()
    mock_google_move_user_ou.assert_called_once_with("username@compiler.la", OU_ALUMNI)
