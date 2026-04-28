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
def mock_GoogleUsers(mocker):
    return mocker.patch(f"{MODULE}.GoogleUsers").return_value


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
    mock_google.assert_called_once_with(format=Format.BASIC, inactive=False, account_type=None)
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
    mock_google.assert_called_once_with(format=Format.BASIC, inactive=True, account_type=None)


def test_users__inactive__system_toggl(cli_runner, mock_toggl):
    args = ["--inactive", "toggl"]
    result = cli_runner.invoke(users, args)

    assert result.exit_code == Result.SUCCESS
    mock_toggl.assert_called_once_with(format=Format.BASIC, inactive=True, account_type=None)


def test_users__account_type(cli_runner, mock_google):
    args = ["--account_type", "service_accounts"]
    result = cli_runner.invoke(users, args)

    assert result.exit_code == Result.SUCCESS
    mock_google.assert_called_once_with(format=Format.BASIC, inactive=False, account_type="service_accounts")


def test_users__account_type__system_toggl(cli_runner, mock_toggl):
    args = ["--account_type", "service_accounts", "toggl"]
    result = cli_runner.invoke(users, args)

    assert result.exit_code == Result.SUCCESS
    mock_toggl.assert_called_once_with(format=Format.BASIC, inactive=False, account_type="service_accounts")


def test_users__account_type__unknown(cli_runner):
    args = ["--account_type", "unknown"]
    result = cli_runner.invoke(users, args)

    assert result.exit_code != Result.SUCCESS
    assert "Invalid value for '-t' / '--account_type': 'unknown'" in result.output


def test_google(mock_GoogleUsers):
    google()

    mock_GoogleUsers.get.assert_called_once_with(format=Format.BASIC, inactive=False, org_units=[])


def test_google__account_type(mock_GoogleUsers):
    google(account_type="service_accounts")

    mock_GoogleUsers.get.assert_called_once_with(format=Format.BASIC, inactive=False, org_units=["/service-accounts"])


def test_google__account_type__unknown():
    with pytest.raises(ValueError, match="Unexpected account_type: unknown"):
        google(account_type="unknown")


@pytest.mark.parametrize("format", set(FORMATS.values()))
def test_google__format(mock_GoogleUsers, format):
    google(format=format)

    mock_GoogleUsers.get.assert_called_once_with(format=format, inactive=False, org_units=[])


@pytest.mark.parametrize("inactive", (True, False))
def test_google__inactive(mock_GoogleUsers, inactive):
    google(inactive=inactive)

    mock_GoogleUsers.get.assert_called_once_with(format=Format.BASIC, inactive=inactive, org_units=[])


def test_toggl(mock_toggl_api, capfd):
    toggl()
    captured = capfd.readouterr()

    mock_toggl_api.get_organization_users.assert_called_once_with(inactive=False, groups=[])
    assert "Getting all Toggl users" in captured.err
    assert "Got 2 Users" in captured.err


def test_toggl__account_type(mock_toggl_api):
    mock_toggl_api.get_organization_group.return_value = {"group_id": 1234}

    toggl(account_type="service_accounts")

    mock_toggl_api.get_organization_users.assert_called_once_with(inactive=False, groups=[1234])


def test_toggl__account_type__unknown(mock_toggl_api):
    with pytest.raises(ValueError, match="Unexpected account_type: unknown"):
        toggl(account_type="unknown")


def test_toggl__inactive(mock_toggl_api):
    toggl(inactive=True)

    mock_toggl_api.get_organization_users.assert_called_once_with(inactive=True, groups=[])


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
