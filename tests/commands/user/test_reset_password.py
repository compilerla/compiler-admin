from argparse import Namespace
import pytest

from compiler_admin import RESULT_FAILURE, RESULT_SUCCESS
from compiler_admin.commands.user.reset_password import reset_password, __name__ as MODULE
from compiler_admin.services.google import USER_HELLO


@pytest.fixture
def mock_google_user_exists(mock_google_user_exists):
    return mock_google_user_exists(MODULE)


@pytest.fixture
def mock_commands_signout(mock_commands_signout):
    return mock_commands_signout(MODULE)


@pytest.fixture
def mock_google_CallGAMCommand(mock_google_CallGAMCommand):
    return mock_google_CallGAMCommand(MODULE)


def test_reset_password_user_username_required():
    args = Namespace()

    with pytest.raises(ValueError, match="username is required"):
        reset_password(args)


def test_reset_password_user_does_not_exist(mock_google_user_exists):
    mock_google_user_exists.return_value = False

    args = Namespace(username="username")
    res = reset_password(args)

    assert res == RESULT_FAILURE


def test_reset_password_user_exists(mock_google_user_exists, mock_google_CallGAMCommand, mock_commands_signout):
    mock_google_user_exists.return_value = True

    args = Namespace(username="username")
    res = reset_password(args)

    assert res == RESULT_SUCCESS

    mock_google_CallGAMCommand.assert_called_once()
    call_args = " ".join(mock_google_CallGAMCommand.call_args[0][0])
    assert "update user" in call_args
    assert "password random changepassword" in call_args

    mock_commands_signout.assert_called_once_with(args)


def test_reset_password_notify(mock_google_user_exists, mock_google_CallGAMCommand, mock_commands_signout):
    mock_google_user_exists.return_value = True

    args = Namespace(username="username", notify="notification@example.com")
    res = reset_password(args)

    assert res == RESULT_SUCCESS

    mock_google_CallGAMCommand.assert_called_once()
    call_args = " ".join(mock_google_CallGAMCommand.call_args[0][0])
    assert "update user" in call_args
    assert "password random changepassword" in call_args
    assert f"notify notification@example.com from {USER_HELLO}" in call_args

    mock_commands_signout.assert_called_once_with(args)
