import pytest

from compiler_admin.commands import RESULT_FAILURE, RESULT_SUCCESS
from compiler_admin.commands.offboard import offboard, __name__ as MODULE


@pytest.fixture
def mock_NamedTemporaryFile(mock_NamedTemporaryFile):
    return mock_NamedTemporaryFile(MODULE, ["Overall Transfer Status: completed"])


@pytest.fixture
def mock_signout(mock_signout):
    return mock_signout(MODULE)


@pytest.fixture
def mock_delete(mock_delete):
    return mock_delete(MODULE)


@pytest.fixture
def mock_user_exists(mock_user_exists):
    return mock_user_exists(MODULE)


@pytest.fixture
def mock_CallGAMCommand(mock_CallGAMCommand):
    return mock_CallGAMCommand(MODULE)


def test_offboard_user_exists(
    mock_user_exists,
    mock_CallGAMCommand,
    mock_NamedTemporaryFile,
    mock_signout,
    mock_delete,
):
    mock_user_exists.return_value = True

    res = offboard("username")

    assert res == RESULT_SUCCESS
    assert mock_CallGAMCommand.call_count > 0
    mock_NamedTemporaryFile.assert_called_once()

    mock_signout.assert_called_once()
    mock_delete.assert_called_once()


def test_offboard_user_does_not_exist(mock_user_exists, mock_CallGAMCommand):
    mock_user_exists.return_value = False

    res = offboard("username")

    assert res == RESULT_FAILURE
    assert mock_CallGAMCommand.call_count == 0


def test_offboard_alias_user_does_not_exist(mock_user_exists, mock_CallGAMCommand):
    # the first call returns True (the user exists), the second False (the alias user does not)
    # https://stackoverflow.com/a/24897297
    mock_user_exists.side_effect = [True, False]

    res = offboard("username", "alias_username")

    assert res == RESULT_FAILURE
    assert mock_user_exists.call_count == 2
    assert mock_CallGAMCommand.call_count == 0
