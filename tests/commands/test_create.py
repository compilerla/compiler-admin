import pytest

from compiler_admin.commands import RESULT_FAILURE, RESULT_SUCCESS
from compiler_admin.commands.create import create, __name__ as MODULE


@pytest.fixture
def mock_user_exists(mock_user_exists):
    return mock_user_exists(MODULE)


@pytest.fixture
def mock_CallGAMCommand(mock_CallGAMCommand):
    return mock_CallGAMCommand(MODULE)


@pytest.fixture
def mock_add_user_to_group(mock_add_user_to_group):
    return mock_add_user_to_group(MODULE)


def test_create_user_exists(mock_user_exists):
    mock_user_exists.return_value = True

    res = create("username")

    assert res == RESULT_FAILURE


def test_create_user_does_not_exists(mock_user_exists, mock_CallGAMCommand, mock_add_user_to_group):
    mock_user_exists.return_value = False

    res = create("username")

    assert res == RESULT_SUCCESS

    mock_CallGAMCommand.assert_called_once()
    call_args = " ".join(mock_CallGAMCommand.call_args[0][0])
    assert "create user" in call_args
    assert "password random changepassword" in call_args

    mock_add_user_to_group.assert_called_once()
