from argparse import Namespace
import pytest

from compiler_admin import RESULT_FAILURE, RESULT_SUCCESS
from compiler_admin.commands.offboard import offboard, __name__ as MODULE


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


def test_offboard_user_username_required():
    args = Namespace()

    with pytest.raises(ValueError, match="username is required"):
        offboard(args)


@pytest.mark.usefixtures("mock_input_yes")
def test_offboard_confirm_yes(
    mock_google_user_exists,
    mock_google_CallGAMCommand,
    mock_google_CallGYBCommand,
    mock_NamedTemporaryFile,
    mock_commands_signout,
    mock_commands_delete,
):
    mock_google_user_exists.return_value = True

    args = Namespace(username="username")
    res = offboard(args)

    assert res == RESULT_SUCCESS
    assert mock_google_CallGAMCommand.call_count > 0
    mock_google_CallGYBCommand.assert_called_once()
    mock_NamedTemporaryFile.assert_called_once()

    mock_commands_signout.assert_called_once()
    assert args in mock_commands_signout.call_args.args

    mock_commands_delete.assert_called_once()
    assert args in mock_commands_delete.call_args.args


@pytest.mark.usefixtures("mock_input_no")
def test_offboard_confirm_no(
    mock_google_user_exists,
    mock_google_CallGAMCommand,
    mock_google_CallGYBCommand,
    mock_commands_signout,
    mock_commands_delete,
):
    mock_google_user_exists.return_value = True

    args = Namespace(username="username")
    res = offboard(args)

    assert res == RESULT_SUCCESS
    mock_google_CallGAMCommand.assert_not_called()
    mock_google_CallGYBCommand.assert_not_called()

    mock_commands_signout.assert_not_called()
    mock_commands_delete.assert_not_called()


def test_offboard_user_does_not_exist(mock_google_user_exists, mock_google_CallGAMCommand):
    mock_google_user_exists.return_value = False

    args = Namespace(username="username")
    res = offboard(args)

    assert res == RESULT_FAILURE
    assert mock_google_CallGAMCommand.call_count == 0


def test_offboard_alias_user_does_not_exist(mock_google_user_exists, mock_google_CallGAMCommand):
    # the first call returns True (the user exists), the second False (the alias user does not)
    # https://stackoverflow.com/a/24897297
    mock_google_user_exists.side_effect = [True, False]

    args = Namespace(username="username", alias="alias_username")
    res = offboard(args)

    assert res == RESULT_FAILURE
    assert mock_google_user_exists.call_count == 2
    assert mock_google_CallGAMCommand.call_count == 0
