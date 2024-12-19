import pytest

from compiler_admin import RESULT_SUCCESS, __version__
from compiler_admin.commands.info import info, __name__ as MODULE


@pytest.fixture
def mock_google_CallGAMCommand(mock_google_CallGAMCommand):
    return mock_google_CallGAMCommand(MODULE)


@pytest.fixture
def mock_google_CallGYBCommand(mock_google_CallGYBCommand):
    return mock_google_CallGYBCommand(MODULE)


def test_info(cli_runner, mock_google_CallGAMCommand, mock_google_CallGYBCommand):
    result = cli_runner.invoke(info)

    assert result.exit_code == RESULT_SUCCESS
    assert f"compiler-admin, version {__version__}" in result.output
    assert mock_google_CallGAMCommand.call_count > 0
    mock_google_CallGYBCommand.assert_called_once()
