import pytest

from compiler_admin import RESULT_SUCCESS
from compiler_admin.commands.user.ls import USER_SYSTEMS, __name__ as MODULE, ls, ls_google, ls_toggl


@pytest.fixture
def mock_google_CallGAMCommand(mock_google_CallGAMCommand):
    return mock_google_CallGAMCommand(MODULE)


@pytest.fixture
def mock_toggl_api(mocker):
    mock = mocker.patch(f"{MODULE}.TogglUsers").return_value
    mock.get_organization_users.return_value = {"user": "name"}
    return mock


@pytest.fixture
def mock_ls_google(mocker, monkeypatch):
    mock = mocker.patch(f"{MODULE}.ls_google")
    monkeypatch.setitem(USER_SYSTEMS, "google", mock)
    return mock


@pytest.fixture
def mock_ls_toggl(mocker, monkeypatch):
    mock = mocker.patch(f"{MODULE}.ls_toggl")
    monkeypatch.setitem(USER_SYSTEMS, "toggl", mock)
    return mock


def test_ls__system_default(cli_runner, mock_ls_google, mock_ls_toggl):
    args = []
    result = cli_runner.invoke(ls, args)

    assert result.exit_code == RESULT_SUCCESS
    mock_ls_google.assert_called_once()
    mock_ls_toggl.assert_not_called()


def test_ls__system_google(cli_runner, mock_ls_google, mock_ls_toggl):
    args = ["google"]
    result = cli_runner.invoke(ls, args)

    assert result.exit_code == RESULT_SUCCESS
    mock_ls_google.assert_called_once()
    mock_ls_toggl.assert_not_called()


def test_ls__system_toggl(cli_runner, mock_ls_google, mock_ls_toggl):
    args = ["toggl"]
    result = cli_runner.invoke(ls, args)

    assert result.exit_code == RESULT_SUCCESS
    mock_ls_google.assert_not_called()
    mock_ls_toggl.assert_called_once()


def test_ls__system_unknown(cli_runner, mock_ls_google, mock_ls_toggl):
    args = ["unknown"]
    result = cli_runner.invoke(ls, args)

    assert result.exit_code != RESULT_SUCCESS
    mock_ls_google.assert_not_called()
    mock_ls_toggl.assert_not_called()


def test_ls_google(mock_google_CallGAMCommand):
    ls_google()

    mock_google_CallGAMCommand.assert_called_once()


def test_ls_toggl(mock_toggl_api):
    ls_toggl()

    mock_toggl_api.get_organization_users.assert_called_once()
