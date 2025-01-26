import pytest

from compiler_admin import RESULT_SUCCESS
from compiler_admin.commands.user.offboard import offboard, __name__ as MODULE


@pytest.fixture
def mock_input_yes(mock_input_yes):
    return mock_input_yes(MODULE)


@pytest.fixture
def mock_input_no(mock_input_no):
    return mock_input_no(MODULE)


@pytest.fixture
def mock_NamedTemporaryFile(mock_NamedTemporaryFile_with_readlines):
    return mock_NamedTemporaryFile_with_readlines(MODULE, ["Overall Transfer Status: completed"])


@pytest.fixture
def mock_commands_alumni(mock_commands_alumni):
    return mock_commands_alumni(MODULE)


@pytest.fixture
def mock_commands_delete(mock_commands_delete):
    return mock_commands_delete(MODULE)


@pytest.fixture
def mock_google_user_exists(mock_google_user_exists):
    return mock_google_user_exists(MODULE)


@pytest.fixture
def mock_google_CallGAMCommand(mock_google_CallGAMCommand):
    return mock_google_CallGAMCommand(MODULE)


@pytest.fixture
def mock_google_CallGYBCommand(mock_google_CallGYBCommand):
    return mock_google_CallGYBCommand(MODULE)


@pytest.mark.usefixtures("mock_input_yes")
def test_offboard_confirm_yes(
    cli_runner,
    mock_google_user_exists,
    mock_google_CallGAMCommand,
    mock_google_CallGYBCommand,
    mock_NamedTemporaryFile,
    mock_commands_alumni,
    mock_commands_delete,
):
    mock_google_user_exists.return_value = True

    result = cli_runner.invoke(offboard, ["username"])

    assert result.exit_code == RESULT_SUCCESS
    assert mock_google_CallGAMCommand.call_count > 0
    mock_google_CallGYBCommand.assert_called_once()
    mock_NamedTemporaryFile.assert_called_once()

    mock_commands_alumni.callback.assert_called_once()
    mock_commands_delete.callback.assert_called_once()


@pytest.mark.usefixtures("mock_input_no")
def test_offboard_confirm_no(
    cli_runner,
    mock_google_user_exists,
    mock_google_CallGAMCommand,
    mock_google_CallGYBCommand,
    mock_commands_alumni,
    mock_commands_delete,
):
    mock_google_user_exists.return_value = True

    result = cli_runner.invoke(offboard, ["username"])

    assert result.exit_code == RESULT_SUCCESS
    mock_google_CallGAMCommand.assert_not_called()
    mock_google_CallGYBCommand.assert_not_called()

    mock_commands_alumni.callback.assert_not_called()
    mock_commands_delete.callback.assert_not_called()


def test_offboard_user_does_not_exist(cli_runner, mock_google_user_exists, mock_google_CallGAMCommand):
    mock_google_user_exists.return_value = False

    result = cli_runner.invoke(offboard, ["username"])

    assert result.exit_code != RESULT_SUCCESS
    assert mock_google_CallGAMCommand.call_count == 0


def test_offboard_alias_user_does_not_exist(cli_runner, mock_google_user_exists, mock_google_CallGAMCommand):
    # the first call returns True (the user exists), the second False (the alias user does not)
    # https://stackoverflow.com/a/24897297
    mock_google_user_exists.side_effect = [True, False]

    result = cli_runner.invoke(offboard, ["--alias", "alias_username", "username"])

    assert result.exit_code != RESULT_SUCCESS
    assert mock_google_user_exists.call_count == 2
    assert mock_google_CallGAMCommand.call_count == 0
