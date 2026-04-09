import pytest

from compiler_admin import RESULT_SUCCESS
from compiler_admin.commands.user.ls import __name__ as MODULE, ls, ls_google


@pytest.fixture
def mock_google_CallGAMCommand(mock_google_CallGAMCommand):
    return mock_google_CallGAMCommand(MODULE)


@pytest.fixture
def mock_ls_google(mocker):
    return mocker.patch(f"{MODULE}.ls_google")


def test_ls__system_default(cli_runner, mock_ls_google):
    args = []
    result = cli_runner.invoke(ls, args)

    assert result.exit_code == RESULT_SUCCESS
    mock_ls_google.assert_called_once()


def test_ls__system_google(cli_runner, mock_ls_google):
    args = ["--system", "google"]
    result = cli_runner.invoke(ls, args)

    assert result.exit_code == RESULT_SUCCESS
    mock_ls_google.assert_called_once()


def test_ls__system_unknown(cli_runner, mock_ls_google):
    args = ["--system", "unknown"]
    result = cli_runner.invoke(ls, args)

    assert result.exit_code != RESULT_SUCCESS
    mock_ls_google.assert_not_called()


def test_ls_google(mock_google_CallGAMCommand):
    ls_google()

    mock_google_CallGAMCommand.assert_called_once()
