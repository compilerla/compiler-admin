from datetime import datetime, timedelta, date
from io import BytesIO, StringIO
import math
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

import pandas as pd
import pytest

import compiler_admin.services.toggl
from compiler_admin.services.toggl import (
    CONVERTERS,
    __name__ as MODULE,
    _get_first_name,
    _get_last_name,
    _prepare_input,
    _str_timedelta,
    convert_to_harvest,
    convert_to_justworks,
    download_time_entries,
    lock_time_entries,
    summarize,
    TOGGL_COLUMNS,
    HARVEST_COLUMNS,
    JUSTWORKS_COLUMNS,
    files,
)


@pytest.fixture(autouse=True)
def mock_environment(monkeypatch):
    monkeypatch.setenv("HARVEST_CLIENT_NAME", "Test_Client")
    monkeypatch.setenv("TOGGL_PROJECT_INFO", "notebooks/data/toggl-project-info-sample.json")
    monkeypatch.setenv("TOGGL_USER_INFO", "notebooks/data/toggl-user-info-sample.json")


@pytest.fixture
def spy_files(mocker):
    return mocker.patch.object(compiler_admin.services.toggl, "files", wraps=files)


@pytest.fixture()
def mock_user_info(mocker):
    return mocker.patch(f"{MODULE}.user_info")


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


def test_get_first_name_matching(mock_user_info):
    mock_user_info.return_value = {"email": {"First Name": "User"}}

    result = _get_first_name("email")

    assert result == "User"


def test_get_first_name_calcuated_with_record(mock_user_info):
    email = "user@email.com"
    mock_user_info.return_value = {email: {"Data": 1234}}

    result = _get_first_name(email)

    assert result == "User"
    assert mock_user_info.return_value[email]["First Name"] == "User"
    assert mock_user_info.return_value[email]["Data"] == 1234


def test_get_first_name_calcuated_without_record(mock_user_info):
    email = "user@email.com"
    mock_user_info.return_value = {email: {}}

    result = _get_first_name(email)

    assert result == "User"
    assert mock_user_info.return_value[email]["First Name"] == "User"
    assert list(mock_user_info.return_value[email].keys()) == ["First Name"]


def test_get_last_name_matching(mock_user_info, mock_google_user_info):
    mock_user_info.return_value = {"email": {"Last Name": "User"}}

    result = _get_last_name("email")

    assert result == "User"
    mock_google_user_info.assert_not_called()


def test_get_last_name_lookup_with_record(mock_user_info, mock_google_user_info):
    email = "user@email.com"
    mock_user_info.return_value = {email: {"Data": 1234}}
    mock_google_user_info.return_value = {"Last Name": "User"}

    result = _get_last_name(email)

    assert result == "User"
    assert mock_user_info.return_value[email]["Last Name"] == "User"
    assert mock_user_info.return_value[email]["Data"] == 1234
    mock_google_user_info.assert_called_once_with(email)


def test_get_last_name_lookup_without_record(mock_user_info, mock_google_user_info):
    email = "user@email.com"
    mock_user_info.return_value = {email: {}}
    mock_google_user_info.return_value = {"Last Name": "User"}

    result = _get_last_name(email)

    assert result == "User"
    assert mock_user_info.return_value[email]["Last Name"] == "User"
    assert list(mock_user_info.return_value[email].keys()) == ["Last Name"]
    mock_google_user_info.assert_called_once_with(email)


def test_str_timedelta():
    dt = "01:30:15"

    result = _str_timedelta(dt)

    assert isinstance(result, timedelta)
    assert result.total_seconds() == (1 * 60 * 60) + (30 * 60) + 15


@pytest.mark.usefixtures("mock_google_user_info")
def test_prepare_input(toggl_file, spy_files):
    df = _prepare_input(toggl_file)

    spy_files.read_csv.assert_called_once()
    call_args = spy_files.read_csv.call_args
    assert (toggl_file,) in call_args
    assert call_args.kwargs["usecols"] == TOGGL_COLUMNS
    assert call_args.kwargs["parse_dates"] == ["Start date"]
    assert call_args.kwargs["cache_dates"] is True

    df_cols = df.columns.to_list()

    assert "First name" in df_cols
    assert "Last name" in df_cols
    assert df["Start date"].dtype.name == "datetime64[ns]"
    assert df["Start time"].dtype.name == "timedelta64[ns]"
    assert df["Duration"].dtype.name == "timedelta64[ns]"
    assert df["Hours"].dtype.name == "float64"

    df = _prepare_input(toggl_file, column_renames={"Start date": "SD", "Start time": "ST", "Duration": "D"})

    assert "Start date" not in df.columns
    assert "Start time" not in df.columns
    assert "Duration" not in df.columns
    assert df["SD"].dtype.name == "datetime64[ns]"
    assert df["ST"].dtype.name == "timedelta64[ns]"
    assert df["D"].dtype.name == "timedelta64[ns]"


def test_convert_to_harvest_mocked(toggl_file, spy_files, mock_google_user_info):
    mock_google_user_info.return_value = {}

    convert_to_harvest(toggl_file, client_name=None)

    spy_files.write_csv.assert_called_once()
    call_args = spy_files.write_csv.call_args
    assert sys.stdout in call_args[0]
    assert call_args.kwargs["columns"] == HARVEST_COLUMNS


def test_convert_to_harvest_sample(toggl_file, harvest_file, mock_google_user_info):
    mock_google_user_info.return_value = {}
    output = None

    with StringIO() as output_data:
        convert_to_harvest(toggl_file, output_data, client_name="Test Client 123")
        output = output_data.getvalue()

    assert output
    assert isinstance(output, str)
    assert ",".join(HARVEST_COLUMNS) in output

    order = ["Date", "First name", "Hours"]
    sample_output_df = pd.read_csv(harvest_file).sort_values(order)
    output_df = pd.read_csv(StringIO(output)).sort_values(order)

    assert set(output_df.columns.to_list()) <= set(sample_output_df.columns.to_list())
    assert output_df["Client"].eq("Test Client 123").all()


def test_convert_to_justworks_mocked(toggl_file, spy_files):
    convert_to_justworks(toggl_file)

    spy_files.write_csv.assert_called_once()
    call_args = spy_files.write_csv.call_args
    assert sys.stdout in call_args[0]
    assert call_args.kwargs["columns"] == JUSTWORKS_COLUMNS


def test_convert_to_justworks_sample(toggl_file, justworks_file):
    output = None

    with StringIO() as output_data:
        convert_to_justworks(toggl_file, output_data)
        output = output_data.getvalue()

    assert output
    assert isinstance(output, str)
    assert ",".join(JUSTWORKS_COLUMNS) in output

    order = ["Start Date", "First Name", "Regular Hours"]
    sample_output_df = pd.read_csv(justworks_file).sort_values(order)
    output_df = pd.read_csv(StringIO(output)).sort_values(order)

    assert set(output_df.columns.to_list()) <= set(sample_output_df.columns.to_list())
    assert output_df.shape == sample_output_df.shape


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


@pytest.mark.usefixtures("mock_toggl_api_env")
def test_lock_time_entries(mock_toggl_api):
    lock_date = datetime(2025, 10, 11)
    lock_time_entries(lock_date)

    mock_toggl_api.update_workspace_preferences.assert_called_once_with(report_locked_at="2025-10-11")


def test_summarize(toggl_file):
    """Test that summarize returns a valid TimeSummary object."""
    summary = summarize(toggl_file)

    assert summary.earliest_date == date(2023, 1, 2)
    assert summary.latest_date == date(2023, 1, 30)
    assert summary.total_rows == 250
    assert math.isclose(summary.total_hours, 518.32, rel_tol=1e-5)
    assert len(summary.hours_per_project) > 0
    assert len(summary.hours_per_user_project) > 0


def test_converters():
    assert CONVERTERS.get("harvest") == convert_to_harvest
    assert CONVERTERS.get("justworks") == convert_to_justworks
