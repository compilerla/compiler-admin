import pytest

from compiler_admin import RESULT_SUCCESS
from compiler_admin.commands.user.signout import signout, __name__ as MODULE


@pytest.fixture
def mock_input_yes(mock_input_yes):
    return mock_input_yes(MODULE)


@pytest.fixture
def mock_input_no(mock_input_no):
    return mock_input_no(MODULE)


@pytest.fixture
def mock_google_user_exists(mock_google_user_exists):
    return mock_google_user_exists(MODULE)


@pytest.fixture
def mock_google_CallGAMCommand(mock_google_CallGAMCommand):
    return mock_google_CallGAMCommand(MODULE)


@pytest.mark.usefixtures("mock_input_yes")
def test_signout_confirm_yes(cli_runner, mock_google_user_exists, mock_google_CallGAMCommand):
    mock_google_user_exists.return_value = True

    result = cli_runner.invoke(signout, ["username"])

    assert result.exit_code == RESULT_SUCCESS
    mock_google_CallGAMCommand.assert_called_once()
    call_args = mock_google_CallGAMCommand.call_args.args[0]
    assert "user" in call_args and "signout" in call_args


@pytest.mark.usefixtures("mock_input_no")
def test_signout_confirm_no(cli_runner, mock_google_user_exists, mock_google_CallGAMCommand):
    mock_google_user_exists.return_value = True

    result = cli_runner.invoke(signout, ["username"])

    assert result.exit_code == RESULT_SUCCESS
    mock_google_CallGAMCommand.assert_not_called()


def test_signout_user_does_not_exist(cli_runner, mock_google_user_exists, mock_google_CallGAMCommand):
    mock_google_user_exists.return_value = False

    result = cli_runner.invoke(signout, ["username"])

    assert result.exit_code != RESULT_SUCCESS
    mock_google_CallGAMCommand.assert_not_called()
