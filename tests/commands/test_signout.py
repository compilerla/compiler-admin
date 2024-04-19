from argparse import Namespace
import pytest

from compiler_admin import RESULT_FAILURE, RESULT_SUCCESS
from compiler_admin.commands.signout import signout, __name__ as MODULE


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
def mock_google_user_exists(mock_google_user_exists):
    return mock_google_user_exists(MODULE)


@pytest.fixture
def mock_google_CallGAMCommand(mock_google_CallGAMCommand):
    return mock_google_CallGAMCommand(MODULE)


def test_signout_user_username_required():
    args = Namespace()

    with pytest.raises(ValueError, match="username is required"):
        signout(args)


@pytest.mark.usefixtures("mock_input_yes")
def test_signout_confirm_yes(mock_google_user_exists, mock_google_CallGAMCommand):
    mock_google_user_exists.return_value = True

    args = Namespace(username="username")
    res = signout(args)

    assert res == RESULT_SUCCESS
    mock_google_CallGAMCommand.assert_called_once()
    call_args = mock_google_CallGAMCommand.call_args.args[0]
    assert "user" in call_args and "signout" in call_args


@pytest.mark.usefixtures("mock_input_no")
def test_signout_confirm_no(mock_google_user_exists, mock_google_CallGAMCommand):
    mock_google_user_exists.return_value = True

    args = Namespace(username="username")
    res = signout(args)

    assert res == RESULT_SUCCESS
    mock_google_CallGAMCommand.assert_not_called()


def test_signout_user_does_not_exist(mock_google_user_exists, mock_google_CallGAMCommand):
    mock_google_user_exists.return_value = False

    args = Namespace(username="username")
    res = signout(args)

    assert res == RESULT_FAILURE
    mock_google_CallGAMCommand.assert_not_called()
