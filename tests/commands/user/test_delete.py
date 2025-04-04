import pytest

from compiler_admin import RESULT_SUCCESS
from compiler_admin.commands.user.delete import delete, __name__ as MODULE


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


@pytest.mark.usefixtures("mock_input_yes")
def test_delete_confirm_yes(cli_runner, mock_google_user_exists, mock_google_CallGAMCommand):
    mock_google_user_exists.return_value = True

    result = cli_runner.invoke(delete, ["username"])

    assert result.exit_code == RESULT_SUCCESS
    mock_google_CallGAMCommand.assert_called_once()
    call_args = mock_google_CallGAMCommand.call_args.args[0]
    assert "delete" in call_args
    assert "user" in call_args
    assert "noactionifalias" in call_args


@pytest.mark.usefixtures("mock_input_no")
def test_delete_confirm_no(cli_runner, mock_google_user_exists, mock_google_CallGAMCommand):
    mock_google_user_exists.return_value = True

    result = cli_runner.invoke(delete, ["username"])

    assert result.exit_code == RESULT_SUCCESS
    mock_google_CallGAMCommand.assert_not_called()


def test_delete_user_does_not_exist(cli_runner, mock_google_user_exists, mock_google_CallGAMCommand):
    mock_google_user_exists.return_value = False

    result = cli_runner.invoke(delete, ["username"])

    assert result.exit_code != RESULT_SUCCESS
    assert mock_google_CallGAMCommand.call_count == 0
