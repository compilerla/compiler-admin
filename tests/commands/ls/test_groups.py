import json

import pytest

from compiler_admin import FORMATS, Format, Result
from compiler_admin.commands.ls.groups import GROUP_SYSTEMS, __name__ as MODULE, google, groups, toggl

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


@pytest.fixture
def mock_GoogleGroups(mocker):
    return mocker.patch(f"{MODULE}.GoogleGroups").return_value


@pytest.fixture
def mock_toggl_api(mocker):
    mock = mocker.patch(f"{MODULE}.TogglUsers").return_value
    mock.get_organization_groups.return_value = MOCK_GROUPS
    return mock


@pytest.fixture
def mock_google(mocker, monkeypatch):
    mock = mocker.patch(f"{MODULE}.google")
    monkeypatch.setitem(GROUP_SYSTEMS, "google", mock)
    return mock


@pytest.fixture
def mock_toggl(mocker, monkeypatch):
    mock = mocker.patch(f"{MODULE}.toggl")
    monkeypatch.setitem(GROUP_SYSTEMS, "toggl", mock)
    return mock


def test_groups__default(cli_runner, mock_google, mock_toggl):
    args = []
    result = cli_runner.invoke(groups, args)

    assert result.exit_code == Result.SUCCESS
    mock_google.assert_called_once_with(format=Format.BASIC)
    mock_toggl.assert_not_called()


def test_groups__system_toggl(cli_runner, mock_google, mock_toggl):
    args = ["toggl"]
    result = cli_runner.invoke(groups, args)

    assert result.exit_code == Result.SUCCESS
    mock_google.assert_not_called()
    mock_toggl.assert_called_once_with(format=Format.BASIC)


def test_groups__system_unknown(cli_runner, mock_google, mock_toggl):
    args = ["unknown"]
    result = cli_runner.invoke(groups, args)

    assert result.exit_code != Result.SUCCESS
    mock_google.assert_not_called()
    mock_toggl.assert_not_called()


def test_google(mock_GoogleGroups):
    google()

    mock_GoogleGroups.get.assert_called_once_with(format=Format.BASIC)


@pytest.mark.parametrize("format", set(FORMATS.values()))
def test_google__format(mock_GoogleGroups, format):
    google(format=format)

    mock_GoogleGroups.get.assert_called_once_with(format=format)


def test_toggl(mock_toggl_api, capfd):
    toggl()
    captured = capfd.readouterr()

    mock_toggl_api.get_organization_groups.assert_called_once_with()
    assert "Getting all Toggl groups" in captured.err
    assert "Got 2 Groups" in captured.err


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
def test_toggl__format(capfd, format, expected_out, not_expected_out):
    toggl(format=format)
    captured = capfd.readouterr()

    for item in expected_out:
        assert item in captured.out
    for item in not_expected_out:
        assert item not in captured.out
