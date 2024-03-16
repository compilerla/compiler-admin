from argparse import Namespace
import pytest

from compiler_admin.commands import RESULT_FAILURE, RESULT_SUCCESS
from compiler_admin.commands.create import create, __name__ as MODULE


@pytest.fixture
def mock_google_user_exists(mock_google_user_exists):
    return mock_google_user_exists(MODULE)


@pytest.fixture
def mock_google_CallGAMCommand(mock_google_CallGAMCommand):
    return mock_google_CallGAMCommand(MODULE)


@pytest.fixture
def mock_google_add_user_to_group(mock_google_add_user_to_group):
    return mock_google_add_user_to_group(MODULE)


def test_create_user_username_required():
    args = Namespace()

    with pytest.raises(ValueError, match="username is required"):
        create(args)


def test_create_user_exists(mock_google_user_exists):
    mock_google_user_exists.return_value = True

    args = Namespace(username="username")
    res = create(args)

    assert res == RESULT_FAILURE


def test_create_user_does_not_exists(mock_google_user_exists, mock_google_CallGAMCommand, mock_google_add_user_to_group):
    mock_google_user_exists.return_value = False

    args = Namespace(username="username")
    res = create(args)

    assert res == RESULT_SUCCESS

    mock_google_CallGAMCommand.assert_called_once()
    call_args = " ".join(mock_google_CallGAMCommand.call_args[0][0])
    assert "create user" in call_args
    assert "password random changepassword" in call_args

    mock_google_add_user_to_group.assert_called_once()
