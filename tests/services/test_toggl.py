from datetime import datetime, timedelta
from io import BytesIO, StringIO
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

import pandas as pd
import pytest

import compiler_admin.services.toggl
from compiler_admin.services.toggl import (
    __name__ as MODULE,
    files,
    INPUT_COLUMNS,
    OUTPUT_COLUMNS,
    _get_first_name,
    _get_last_name,
    _str_timedelta,
    convert_to_harvest,
    download_time_entries,
)


@pytest.fixture(autouse=True)
def mock_environment(monkeypatch):
    monkeypatch.setenv("HARVEST_CLIENT_NAME", "Test_Client")
    monkeypatch.setenv("TOGGL_PROJECT_INFO", "notebooks/data/toggl-project-info-sample.json")
    monkeypatch.setenv("TOGGL_USER_INFO", "notebooks/data/toggl-user-info-sample.json")


@pytest.fixture
def spy_files(mocker):
    return mocker.patch.object(compiler_admin.services.toggl, "files", wraps=files)


@pytest.fixture(autouse=True)
def mock_USER_INFO(mocker):
    return mocker.patch(f"{MODULE}.USER_INFO", new={})


@pytest.fixture
def mock_google_user_info(mocker):
    return mocker.patch(f"{MODULE}.google_user_info")


@pytest.fixture
def mock_toggl_api(mocker):
    t = mocker.patch(f"{MODULE}.Toggl")
    return t.return_value


@pytest.fixture
def mock_toggl_api_env(monkeypatch):
    monkeypatch.setenv("TOGGL_API_TOKEN", "token")
    monkeypatch.setenv("TOGGL_CLIENT_ID", "1234")
    monkeypatch.setenv("TOGGL_WORKSPACE_ID", "workspace")


@pytest.fixture
def mock_toggl_detailed_time_entries(mock_toggl_api, toggl_file):
    mock_csv_bytes = Path(toggl_file).read_bytes()
    mock_toggl_api.detailed_time_entries.return_value.content = mock_csv_bytes
    return mock_toggl_api


def test_get_first_name_matching(mock_USER_INFO):
    mock_USER_INFO["email"] = {"First Name": "User"}

    result = _get_first_name("email")

    assert result == "User"


def test_get_first_name_calcuated_with_record(mock_USER_INFO):
    email = "user@email.com"
    mock_USER_INFO[email] = {"Data": 1234}

    result = _get_first_name(email)

    assert result == "User"
    assert mock_USER_INFO[email]["First Name"] == "User"
    assert mock_USER_INFO[email]["Data"] == 1234


def test_get_first_name_calcuated_without_record(mock_USER_INFO):
    email = "user@email.com"
    mock_USER_INFO[email] = {}

    result = _get_first_name(email)

    assert result == "User"
    assert mock_USER_INFO[email]["First Name"] == "User"
    assert list(mock_USER_INFO[email].keys()) == ["First Name"]


def test_get_last_name_matching(mock_USER_INFO, mock_google_user_info):
    mock_USER_INFO["email"] = {"Last Name": "User"}

    result = _get_last_name("email")

    assert result == "User"
    mock_google_user_info.assert_not_called()


def test_get_last_name_lookup_with_record(mock_USER_INFO, mock_google_user_info):
    email = "user@email.com"
    mock_USER_INFO[email] = {"Data": 1234}
    mock_google_user_info.return_value = {"Last Name": "User"}

    result = _get_last_name(email)

    assert result == "User"
    assert mock_USER_INFO[email]["Last Name"] == "User"
    assert mock_USER_INFO[email]["Data"] == 1234
    mock_google_user_info.assert_called_once_with(email)


def test_get_last_name_lookup_without_record(mock_USER_INFO, mock_google_user_info):
    email = "user@email.com"
    mock_USER_INFO[email] = {}
    mock_google_user_info.return_value = {"Last Name": "User"}

    result = _get_last_name(email)

    assert result == "User"
    assert mock_USER_INFO[email]["Last Name"] == "User"
    assert list(mock_USER_INFO[email].keys()) == ["Last Name"]
    mock_google_user_info.assert_called_once_with(email)


def test_str_timedelta():
    dt = "01:30:15"

    result = _str_timedelta(dt)

    assert isinstance(result, timedelta)
    assert result.total_seconds() == (1 * 60 * 60) + (30 * 60) + 15


def test_convert_to_harvest_mocked(toggl_file, spy_files, mock_google_user_info):
    mock_google_user_info.return_value = {}

    convert_to_harvest(toggl_file, client_name=None)

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

    order = ["Date", "First name", "Hours"]
    sample_output_df = pd.read_csv(harvest_file).sort_values(order)
    output_df = pd.read_csv(StringIO(output)).sort_values(order)

    assert set(output_df.columns.to_list()) <= set(sample_output_df.columns.to_list())
    assert output_df["Client"].eq("Test Client 123").all()


@pytest.mark.usefixtures("mock_toggl_api_env", "mock_toggl_detailed_time_entries")
def test_download_time_entries(toggl_file):
    dt = datetime.now()
    mock_csv_bytes = Path(toggl_file).read_bytes()

    with NamedTemporaryFile("w") as temp:
        download_time_entries(dt, dt, temp.name)
        temp.flush()
        response_csv_bytes = Path(temp.name).read_bytes()

        # load each CSV into a DataFrame
        mock_df = pd.read_csv(BytesIO(mock_csv_bytes))
        response_df = pd.read_csv(BytesIO(response_csv_bytes))

        # check that the response DataFrame has all columns from the mock DataFrame
        assert set(response_df.columns.to_list()).issubset(mock_df.columns.to_list())

        # check that all column values from response DataFrame are the same
        # as corresponding column values from the mock DataFrame
        for col in response_df.columns:
            assert response_df[col].equals(mock_df[col])
