import json

import pytest

from compiler_admin import FORMATS, Format, Result
from compiler_admin.commands.ls.users import USER_SYSTEMS, __name__ as MODULE, google, toggl, users

MOCK_USERS = [
    {
        "email": "email1@example.com",
        "name": "name1",
        "id": "id1",
        "user_id": "user1",
        "role_id": "role1",
        "organization_id": 5678,
        "inactive": False,
        "joined": True,
        "can_edit_email": False,
        "2fa_enabled": True,
        "avatar_url": "https://example.com/users/1",
        "extra": "extra1",
    },
    {
        "email": "email2@example.com",
        "name": "name2",
        "id": "id2",
        "user_id": "user2",
        "role_id": "role2",
        "organization_id": 5678,
        "inactive": False,
        "joined": True,
        "can_edit_email": False,
        "2fa_enabled": True,
        "avatar_url": "https://example.com/users/2",
        "extra": "extra1",
    },
]


@pytest.fixture
def mock_google_get_users(mocker):
    return mocker.patch(f"{MODULE}.get_users")


@pytest.fixture
def mock_toggl_api(mocker):
    mock = mocker.patch(f"{MODULE}.TogglUsers").return_value
    mock.get_organization_users.return_value = MOCK_USERS
    return mock


@pytest.fixture
def mock_google(mocker, monkeypatch):
    mock = mocker.patch(f"{MODULE}.google")
    monkeypatch.setitem(USER_SYSTEMS, "google", mock)
    return mock


@pytest.fixture
def mock_toggl(mocker, monkeypatch):
    mock = mocker.patch(f"{MODULE}.toggl")
    monkeypatch.setitem(USER_SYSTEMS, "toggl", mock)
    return mock


def test_users(cli_runner, mock_google, mock_toggl):
    args = []
    result = cli_runner.invoke(users, args)

    assert result.exit_code == Result.SUCCESS
    mock_google.assert_called_once_with(format=Format.BASIC, inactive=False)
    mock_toggl.assert_not_called()


def test_users__system_google(cli_runner, mock_google, mock_toggl):
    args = ["google"]
    result = cli_runner.invoke(users, args)

    assert result.exit_code == Result.SUCCESS
    mock_google.assert_called_once()
    mock_toggl.assert_not_called()


def test_users__system_toggl(cli_runner, mock_google, mock_toggl):
    args = ["toggl"]
    result = cli_runner.invoke(users, args)

    assert result.exit_code == Result.SUCCESS
    mock_google.assert_not_called()
    mock_toggl.assert_called_once()


def test_users__system_unknown(cli_runner, mock_google, mock_toggl):
    args = ["unknown"]
    result = cli_runner.invoke(users, args)

    assert result.exit_code != Result.SUCCESS
    mock_google.assert_not_called()
    mock_toggl.assert_not_called()


def test_users__inactive(cli_runner, mock_google):
    args = ["--inactive"]
    result = cli_runner.invoke(users, args)

    assert result.exit_code == Result.SUCCESS
    mock_google.assert_called_once_with(format=Format.BASIC, inactive=True)


def test_users__inactive__system_toggl(cli_runner, mock_toggl):
    args = ["--inactive", "toggl"]
    result = cli_runner.invoke(users, args)

    assert result.exit_code == Result.SUCCESS
    mock_toggl.assert_called_once_with(format=Format.BASIC, inactive=True)


def test_google(mock_google_get_users):
    google()

    mock_google_get_users.assert_called_once()


@pytest.mark.parametrize("format", set(FORMATS.values()))
def test_google__format(mock_google_get_users, format):
    google(format=format)

    mock_google_get_users.assert_called_once_with(inactive=False, format=format)


def test_toggl(mock_toggl_api, capfd):
    toggl()
    captured = capfd.readouterr()

    mock_toggl_api.get_organization_users.assert_called_once_with(inactive=False)
    assert "Getting all Toggl users" in captured.err
    assert "Got 2 Users" in captured.err


def test_toggl__inactive(mock_toggl_api):
    toggl(inactive=True)

    mock_toggl_api.get_organization_users.assert_called_once_with(inactive=True)


@pytest.mark.usefixtures("mock_toggl_api")
@pytest.mark.parametrize(
    "format,expected_out,not_expected_out",
    [
        (
            Format.BASIC,
            ["email\n", "email1", "email2"],
            ["name,id,user_id,role_id,organization_id,inactive,joined,can_edit_email,2fa_enabled,avatar_url\n"],
        ),
        (
            Format.CSV,
            [
                "email,name,id,user_id,role_id,organization_id,inactive,joined,can_edit_email,2fa_enabled,avatar_url\n",
                "email1",
                "email2",
                "name1",
                "name2",
                "id1",
                "id2",
                "user1",
                "user2",
                "role1",
                "role2",
                "5678",
                "https://example.com/users/1",
                "https://example.com/users/2",
            ],
            ["extra1", "extra2"],
        ),
        (Format.JSON, [json.dumps(MOCK_USERS, indent=2)], []),
        (-1, [], []),
    ],
)
def test_toggl__format(capfd, format, expected_out, not_expected_out):
    toggl(format=format)
    captured = capfd.readouterr()

    for item in expected_out:
        assert item in captured.out
    for item in not_expected_out:
        assert item not in captured.out
