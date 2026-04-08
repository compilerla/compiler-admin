import pytest

from compiler_admin import RESULT_SUCCESS
from compiler_admin.commands.user.ls import __name__ as MODULE, ls


@pytest.fixture
def mock_google_CallGAMCommand(mock_google_CallGAMCommand):
    return mock_google_CallGAMCommand(MODULE)


def test_ls(cli_runner, mock_google_CallGAMCommand):
    args = []
    result = cli_runner.invoke(ls, args)

    assert result.exit_code == RESULT_SUCCESS
    mock_google_CallGAMCommand.assert_called_once()
