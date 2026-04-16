import json

import pytest

from compiler_admin import Format, Result
from compiler_admin.commands.user.ls import FORMATS, USER_SYSTEMS, __name__ as MODULE, ls, ls_google, ls_toggl

MOCK_GROUPS = [
    {
        "group_id": "group1",
        "name": "name1",
        "at": "2026-04-20T20:20:00.000000Z",
        "extra": "extra1",
    },
    {
        "group_id": "group2",
        "name": "name2",
        "at": "2026-04-20T20:40:00.000000Z",
        "extra": "extra2",
    },
]

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
def mock_google_get_org_units(mocker):
    return mocker.patch(f"{MODULE}.get_org_units")


@pytest.fixture
def mock_google_get_users(mocker):
    return mocker.patch(f"{MODULE}.get_users")


@pytest.fixture
def mock_toggl_api(mocker):
    mock = mocker.patch(f"{MODULE}.TogglUsers").return_value
    mock.get_organization_users.return_value = MOCK_USERS
    mock.get_organization_groups.return_value = MOCK_GROUPS
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


def test_ls_default(cli_runner, mock_ls_google, mock_ls_toggl):
    args = []
    result = cli_runner.invoke(ls, args)

    assert result.exit_code == Result.SUCCESS
    mock_ls_google.assert_called_once_with(format=Format.BASIC, groups=False, inactive=False)
    mock_ls_toggl.assert_not_called()


def test_ls__groups(cli_runner, mock_ls_google, mock_ls_toggl):
    args = ["--groups"]
    result = cli_runner.invoke(ls, args)

    assert result.exit_code == Result.SUCCESS
    mock_ls_google.assert_called_once_with(format=Format.BASIC, groups=True, inactive=False)
    mock_ls_toggl.assert_not_called()


def test_ls__groups__system_toggl(cli_runner, mock_ls_google, mock_ls_toggl):
    args = ["--groups", "toggl"]
    result = cli_runner.invoke(ls, args)

    assert result.exit_code == Result.SUCCESS
    mock_ls_google.assert_not_called()
    mock_ls_toggl.assert_called_once_with(format=Format.BASIC, groups=True, inactive=False)


def test_ls__system_google(cli_runner, mock_ls_google, mock_ls_toggl):
    args = ["google"]
    result = cli_runner.invoke(ls, args)

    assert result.exit_code == Result.SUCCESS
    mock_ls_google.assert_called_once()
    mock_ls_toggl.assert_not_called()


def test_ls__system_toggl(cli_runner, mock_ls_google, mock_ls_toggl):
    args = ["toggl"]
    result = cli_runner.invoke(ls, args)

    assert result.exit_code == Result.SUCCESS
    mock_ls_google.assert_not_called()
    mock_ls_toggl.assert_called_once()


def test_ls__system_unknown(cli_runner, mock_ls_google, mock_ls_toggl):
    args = ["unknown"]
    result = cli_runner.invoke(ls, args)

    assert result.exit_code != Result.SUCCESS
    mock_ls_google.assert_not_called()
    mock_ls_toggl.assert_not_called()


def test_ls__inactive(cli_runner, mock_ls_google):
    args = ["--inactive"]
    result = cli_runner.invoke(ls, args)

    assert result.exit_code == Result.SUCCESS
    mock_ls_google.assert_called_once_with(format=Format.BASIC, groups=False, inactive=True)


def test_ls__inactive__system_toggl(cli_runner, mock_ls_toggl):
    args = ["--inactive", "toggl"]
    result = cli_runner.invoke(ls, args)

    assert result.exit_code == Result.SUCCESS
    mock_ls_toggl.assert_called_once_with(format=Format.BASIC, groups=False, inactive=True)


def test_ls_google(mock_google_get_users):
    ls_google()

    mock_google_get_users.assert_called_once()


@pytest.mark.parametrize("format", set(FORMATS.values()))
def test_ls_google__format(mock_google_get_users, format):
    ls_google(format=format)

    mock_google_get_users.assert_called_once_with(inactive=False, format=format)


def test_ls_google__groups(mock_google_get_org_units):
    ls_google(groups=True)

    mock_google_get_org_units.assert_called_once()


def test_ls_toggl__default(mock_toggl_api, capfd):
    ls_toggl()
    captured = capfd.readouterr()

    mock_toggl_api.get_organization_users.assert_called_once_with(inactive=False)
    assert "Getting all Toggl users" in captured.err
    assert "Got 2 Users" in captured.err


def test_lg_toggl__groups(mock_toggl_api, capfd):
    ls_toggl(groups=True)
    captured = capfd.readouterr()

    mock_toggl_api.get_organization_groups.assert_called_once_with()
    assert "Getting all Toggl groups" in captured.err
    assert "Got 2 Groups" in captured.err


def test_ls_toggl__inactive(mock_toggl_api):
    ls_toggl(inactive=True)

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
def test_ls_toggl__format(capfd, format, expected_out, not_expected_out):
    ls_toggl(format=format)
    captured = capfd.readouterr()

    for item in expected_out:
        assert item in captured.out
    for item in not_expected_out:
        assert item not in captured.out


@pytest.mark.usefixtures("mock_toggl_api")
@pytest.mark.parametrize(
    "format,expected_out,not_expected_out",
    [
        (
            Format.BASIC,
            [
                "group_id,name,at\n",
                "group1",
                "group2",
                "name1",
                "name2",
                "2026-04-20T20:20:00.000000Z",
                "2026-04-20T20:40:00.000000Z",
            ],
            ["extra1", "extra2"],
        ),
        (
            Format.CSV,
            [
                "group_id,name,at\n",
                "group1",
                "group2",
                "name1",
                "name2",
                "2026-04-20T20:20:00.000000Z",
                "2026-04-20T20:20:00.000000Z",
            ],
            ["extra1", "extra2"],
        ),
        (Format.JSON, [json.dumps(MOCK_GROUPS, indent=2)], []),
        (-1, [], []),
    ],
)
def test_ls_toggl__groups__format(capfd, format, expected_out, not_expected_out):
    ls_toggl(format=format, groups=True)
    captured = capfd.readouterr()

    for item in expected_out:
        assert item in captured.out
    for item in not_expected_out:
        assert item not in captured.out
