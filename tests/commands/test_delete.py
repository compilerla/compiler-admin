from argparse import Namespace
import pytest

from compiler_admin.commands import RESULT_FAILURE, RESULT_SUCCESS
from compiler_admin.commands.delete import delete, __name__ as MODULE


@pytest.fixture
def mock_google_user_exists(mock_google_user_exists):
    return mock_google_user_exists(MODULE)


@pytest.fixture
def mock_google_CallGAMCommand(mock_google_CallGAMCommand):
    return mock_google_CallGAMCommand(MODULE)


def test_delete_user_username_required():
    args = Namespace()

    with pytest.raises(ValueError, match="username is required"):
        delete(args)


def test_delete_user_exists(mock_google_user_exists, mock_google_CallGAMCommand):
    mock_google_user_exists.return_value = True

    args = Namespace(username="username")
    res = delete(args)

    assert res == RESULT_SUCCESS
    mock_google_CallGAMCommand.assert_called_once()
    call_args = mock_google_CallGAMCommand.call_args.args[0]
    assert "delete" in call_args
    assert "user" in call_args
    assert "noactionifalias" in call_args


def test_delete_user_does_not_exist(mock_google_user_exists, mock_google_CallGAMCommand):
    mock_google_user_exists.return_value = False

    args = Namespace(username="username")
    res = delete(args)

    assert res == RESULT_FAILURE
    assert mock_google_CallGAMCommand.call_count == 0
