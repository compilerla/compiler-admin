from argparse import Namespace
import pytest

from compiler_admin import RESULT_FAILURE, RESULT_SUCCESS
from compiler_admin.commands.user.alumni import alumni, __name__ as MODULE
from compiler_admin.services.google import OU_ALUMNI


@pytest.fixture
def mock_commands_reset(mock_commands_reset):
    return mock_commands_reset(MODULE)


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


def test_alumni_username_required():
    args = Namespace()

    with pytest.raises(ValueError, match="username is required"):
        alumni(args)


def test_alumni_user_does_not_exists(mock_google_user_exists, mock_google_CallGAMCommand):
    mock_google_user_exists.return_value = False

    args = Namespace(username="username")
    res = alumni(args)

    assert res == RESULT_FAILURE
    mock_google_CallGAMCommand.assert_not_called()


@pytest.mark.usefixtures("mock_input_yes")
def test_alumni_confirm_yes(
    mock_google_user_exists, mock_google_CallGAMCommand, mock_commands_reset, mock_google_move_user_ou
):
    mock_google_user_exists.return_value = True

    args = Namespace(username="username", force=False)
    res = alumni(args)

    assert res == RESULT_SUCCESS
    mock_google_CallGAMCommand.assert_called()
    mock_google_move_user_ou.assert_called_once_with("username@compiler.la", OU_ALUMNI)
    mock_commands_reset.assert_called_once_with(args)


@pytest.mark.usefixtures("mock_input_no")
def test_alumni_confirm_no(mock_google_user_exists, mock_google_CallGAMCommand, mock_commands_reset, mock_google_move_user_ou):
    mock_google_user_exists.return_value = True

    args = Namespace(username="username", force=False)
    res = alumni(args)

    assert res == RESULT_SUCCESS
    mock_google_CallGAMCommand.assert_not_called()
    mock_commands_reset.assert_not_called()
    mock_google_move_user_ou.assert_not_called()


def test_alumni_force(mock_google_user_exists, mock_google_CallGAMCommand, mock_commands_reset, mock_google_move_user_ou):
    mock_google_user_exists.return_value = True

    args = Namespace(username="username", force=True)
    res = alumni(args)

    assert res == RESULT_SUCCESS
    mock_google_CallGAMCommand.assert_called()
    mock_google_move_user_ou.assert_called_once_with("username@compiler.la", OU_ALUMNI)
    mock_commands_reset.assert_called_once_with(args)
