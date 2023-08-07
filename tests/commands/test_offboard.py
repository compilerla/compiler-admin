import pytest

from compiler_admin.commands import RESULT_FAILURE, RESULT_SUCCESS
from compiler_admin.commands.offboard import offboard, __name__ as MODULE


@pytest.fixture
def mock_NamedTemporaryFile(mock_NamedTemporaryFile):
    return mock_NamedTemporaryFile(MODULE, ["Overall Transfer Status: completed"])


@pytest.fixture
def mock_commands_signout(mock_commands_signout):
    return mock_commands_signout(MODULE)


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


def test_offboard_user_exists(
    mock_google_user_exists,
    mock_google_CallGAMCommand,
    mock_google_CallGYBCommand,
    mock_NamedTemporaryFile,
    mock_commands_signout,
    mock_commands_delete,
):
    mock_google_user_exists.return_value = True

    res = offboard("username")

    assert res == RESULT_SUCCESS
    assert mock_google_CallGAMCommand.call_count > 0
    mock_google_CallGYBCommand.assert_called_once()
    mock_NamedTemporaryFile.assert_called_once()

    mock_commands_signout.assert_called_once()
    mock_commands_delete.assert_called_once()


def test_offboard_user_does_not_exist(mock_google_user_exists, mock_google_CallGAMCommand):
    mock_google_user_exists.return_value = False

    res = offboard("username")

    assert res == RESULT_FAILURE
    assert mock_google_CallGAMCommand.call_count == 0


def test_offboard_alias_user_does_not_exist(mock_google_user_exists, mock_google_CallGAMCommand):
    # the first call returns True (the user exists), the second False (the alias user does not)
    # https://stackoverflow.com/a/24897297
    mock_google_user_exists.side_effect = [True, False]

    res = offboard("username", "alias_username")

    assert res == RESULT_FAILURE
    assert mock_google_user_exists.call_count == 2
    assert mock_google_CallGAMCommand.call_count == 0
