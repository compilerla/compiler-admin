import sys
from datetime import timedelta
from io import StringIO
from tempfile import NamedTemporaryFile

import pandas as pd
import pytest

import compiler_admin.services.toggl
from compiler_admin.services.toggl import (
    __name__ as MODULE,
    files,
    INPUT_COLUMNS,
    OUTPUT_COLUMNS,
    PROJECT_INFO,
    USER_INFO,
    _harvest_client_name,
    _get_info,
    _toggl_project_info,
    _toggl_user_info,
    _get_first_name,
    _get_last_name,
    _str_timedelta,
    convert_to_harvest,
)


@pytest.fixture(autouse=True)
def mock_environment(monkeypatch):
    monkeypatch.setenv("HARVEST_CLIENT_NAME", "Test_Client")
    monkeypatch.setenv("TOGGL_PROJECT_INFO", "notebooks/data/toggl-project-info-sample.json")
    monkeypatch.setenv("TOGGL_USER_INFO", "notebooks/data/toggl-user-info-sample.json")


@pytest.fixture(autouse=True)
def reset_USER_INFO():
    USER_INFO.clear()


@pytest.fixture
def spy_files(mocker):
    return mocker.patch.object(compiler_admin.services.toggl, "files", wraps=files)


@pytest.fixture
def mock_harvest_client_name(mocker):
    return mocker.patch(f"{MODULE}._harvest_client_name")


@pytest.fixture
def mock_get_info(mocker):
    return mocker.patch(f"{MODULE}._get_info")


@pytest.fixture
def mock_google_user_info(mocker):
    return mocker.patch(f"{MODULE}.google_user_info")


def test_harvest_client_name(monkeypatch):
    assert _harvest_client_name() == "Test_Client"

    monkeypatch.setenv("HARVEST_CLIENT_NAME", "New Test Client")

    assert _harvest_client_name() == "New Test Client"


def test_get_info(monkeypatch):
    with NamedTemporaryFile("w") as temp:
        monkeypatch.setenv("INFO_FILE", temp.name)
        temp.write('{"key": "value"}')
        temp.seek(0)

        obj = {}
        result = _get_info(obj, "key", "INFO_FILE")

        assert result == "value"
        assert obj["key"] == "value"


def test_get_info_no_file():
    obj = {}
    result = _get_info(obj, "key", "INFO_FILE")

    assert result is None
    assert "key" not in obj


def test_toggl_project_info(mock_get_info):
    _toggl_project_info("project")

    mock_get_info.assert_called_once_with(PROJECT_INFO, "project", "TOGGL_PROJECT_INFO")


def test_toggl_user_info(mock_get_info):
    _toggl_user_info("user")

    mock_get_info.assert_called_once_with(USER_INFO, "user", "TOGGL_USER_INFO")


def test_get_first_name_matching(mock_get_info):
    mock_get_info.return_value = {"First Name": "User"}

    result = _get_first_name("email")

    assert result == "User"


def test_get_first_name_calcuated_with_record(mock_get_info):
    email = "user@email.com"
    mock_get_info.return_value = {}
    USER_INFO[email] = {"Data": 1234}

    result = _get_first_name(email)

    assert result == "User"
    assert USER_INFO[email]["First Name"] == "User"
    assert USER_INFO[email]["Data"] == 1234


def test_get_first_name_calcuated_without_record(mock_get_info):
    email = "user@email.com"
    mock_get_info.return_value = {}

    result = _get_first_name(email)

    assert result == "User"
    assert USER_INFO[email]["First Name"] == "User"
    assert list(USER_INFO[email].keys()) == ["First Name"]


def test_get_last_name_matching(mock_get_info, mock_google_user_info):
    mock_get_info.return_value = {"Last Name": "User"}

    result = _get_last_name("email")

    assert result == "User"
    mock_google_user_info.assert_not_called()


def test_get_last_name_lookup_with_record(mock_get_info, mock_google_user_info):
    email = "user@email.com"
    mock_get_info.return_value = {}
    USER_INFO[email] = {"Data": 1234}
    mock_google_user_info.return_value = {"Last Name": "User"}

    result = _get_last_name(email)

    assert result == "User"
    assert USER_INFO[email]["Last Name"] == "User"
    assert USER_INFO[email]["Data"] == 1234
    mock_google_user_info.assert_called_once_with(email)


def test_get_last_name_lookup_without_record(mock_get_info, mock_google_user_info):
    email = "user@email.com"
    mock_get_info.return_value = {}
    mock_google_user_info.return_value = {"Last Name": "User"}

    result = _get_last_name(email)

    assert result == "User"
    assert USER_INFO[email]["Last Name"] == "User"
    assert list(USER_INFO[email].keys()) == ["Last Name"]
    mock_google_user_info.assert_called_once_with(email)


def test_str_timedelta():
    dt = "01:30:15"

    result = _str_timedelta(dt)

    assert isinstance(result, timedelta)
    assert result.total_seconds() == (1 * 60 * 60) + (30 * 60) + 15


def test_convert_to_harvest_mocked(toggl_file, spy_files, mock_harvest_client_name, mock_google_user_info):
    mock_google_user_info.return_value = {}

    convert_to_harvest(toggl_file, client_name=None)

    mock_harvest_client_name.assert_called_once()

    spy_files.read_csv.assert_called_once()
    call_args = spy_files.read_csv.call_args
    assert (toggl_file,) in call_args
    assert call_args.kwargs["usecols"] == INPUT_COLUMNS
    assert call_args.kwargs["parse_dates"] == ["Start date"]
    assert call_args.kwargs["cache_dates"] is True

    spy_files.write_csv.assert_called_once()
    call_args = spy_files.write_csv.call_args
    assert sys.stdout in call_args[0]
    assert call_args.kwargs["columns"] == OUTPUT_COLUMNS


def test_convert_to_harvest_sample(toggl_file, harvest_file, mock_google_user_info):
    mock_google_user_info.return_value = {}
    output = None

    with StringIO() as output_data:
        convert_to_harvest(toggl_file, output_data, "Test Client 123")
        output = output_data.getvalue()

    assert output
    assert isinstance(output, str)
    assert ",".join(OUTPUT_COLUMNS) in output

    order = ["Date", "First Name", "Hours"]
    sample_output_df = pd.read_csv(harvest_file).sort_values(order)
    output_df = pd.read_csv(StringIO(output)).sort_values(order)

    assert set(output_df.columns.to_list()) <= set(sample_output_df.columns.to_list())
    assert output_df["Client"].eq("Test Client 123").all()
