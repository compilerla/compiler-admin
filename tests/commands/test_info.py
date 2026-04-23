import pytest

from compiler_admin import Result, __version__
from compiler_admin.commands.info import __name__ as MODULE, info


@pytest.fixture
def mock_GoogleService(mocker):
    return mocker.patch(f"{MODULE}.GoogleService").return_value


def test_info(cli_runner, mock_GoogleService):
    result = cli_runner.invoke(info)

    assert result.exit_code == Result.SUCCESS
    assert f"compiler-admin, version {__version__}" in result.output

    assert mock_GoogleService.gam_command.call_count == 2
    mock_GoogleService.gyb_command.assert_called_once()
