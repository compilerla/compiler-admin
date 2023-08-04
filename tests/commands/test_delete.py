import pytest

from compiler_admin.commands import RESULT_FAILURE, RESULT_SUCCESS
from compiler_admin.commands.delete import delete, __name__ as MODULE


@pytest.fixture
def mock_user_exists(mock_user_exists):
    return mock_user_exists(MODULE)


@pytest.fixture
def mock_CallGAMCommand(mock_CallGAMCommand):
    return mock_CallGAMCommand(MODULE)


def test_delete_user_exists(mock_user_exists, mock_CallGAMCommand):
    mock_user_exists.return_value = True

    res = delete("username")

    assert res == RESULT_SUCCESS
    mock_CallGAMCommand.assert_called_once()
    call_args = " ".join(mock_CallGAMCommand.call_args[0][0])
    assert "delete user" in call_args
    assert "noactionifalias" in call_args


def test_delete_user_does_not_exist(mock_user_exists, mock_CallGAMCommand):
    mock_user_exists.return_value = False

    res = delete("username")

    assert res == RESULT_FAILURE
    assert mock_CallGAMCommand.call_count == 0