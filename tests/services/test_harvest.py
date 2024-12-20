import sys
from datetime import timedelta
from io import StringIO

import numpy as np
import pandas as pd
import pytest

import compiler_admin.services.harvest
from compiler_admin.services.harvest import (
    __name__ as MODULE,
    files,
    HARVEST_COLUMNS,
    TOGGL_COLUMNS,
    CONVERTERS,
    _calc_start_time,
    _duration_str,
    _toggl_client_name,
    convert_to_toggl,
)


@pytest.fixture(autouse=True)
def mock_environment(monkeypatch):
    monkeypatch.setenv("TOGGL_CLIENT_NAME", "Test_Client")


@pytest.fixture
def spy_files(mocker):
    return mocker.patch.object(compiler_admin.services.harvest, "files", wraps=files)


@pytest.fixture
def mock_toggl_client_name(mocker):
    return mocker.patch(f"{MODULE}._toggl_client_name")


def test_calc_start_time():
    durations = pd.to_timedelta(np.arange(1, 6), unit="m")
    df = pd.DataFrame(data={"Duration": durations, "Start time": [pd.to_timedelta("09:00:00") for d in durations]})

    calc_df = _calc_start_time(df)

    assert calc_df.columns.equals(df.columns)
    assert calc_df["Duration"].equals(df["Duration"])
    assert calc_df["Start time"].to_list() == [
        # offset = 0, cumsum = 0
        pd.to_timedelta("09:00:00"),
        # offset = 1, cumsum = 1
        pd.to_timedelta("09:01:00"),
        # offset = 2, cumsum = 3
        pd.to_timedelta("09:03:00"),
        # offset = 3, cumsum = 6
        pd.to_timedelta("09:06:00"),
        # offset = 4, cumsum = 10
        pd.to_timedelta("09:10:00"),
    ]


def test_duration_str():
    td = timedelta(hours=1, minutes=30, seconds=15)

    result = _duration_str(td)

    assert isinstance(result, str)
    assert result == "01:30"


def test_toggl_client_name(monkeypatch):
    assert _toggl_client_name() == "Test_Client"

    monkeypatch.setenv("TOGGL_CLIENT_NAME", "New Test Client")

    assert _toggl_client_name() == "New Test Client"


def test_convert_to_toggl_mocked(harvest_file, spy_files, mock_toggl_client_name):
    convert_to_toggl(harvest_file, client_name=None)

    mock_toggl_client_name.assert_called_once()

    spy_files.read_csv.assert_called_once()
    call_args = spy_files.read_csv.call_args
    assert (harvest_file,) in call_args
    assert call_args.kwargs["usecols"] == HARVEST_COLUMNS
    assert call_args.kwargs["parse_dates"] == ["Date"]
    assert call_args.kwargs["cache_dates"] is True

    spy_files.write_csv.assert_called_once()
    call_args = spy_files.write_csv.call_args
    assert call_args[0][0] == sys.stdout
    assert call_args[0][2] == TOGGL_COLUMNS


def test_convert_to_toggl_sample(harvest_file, toggl_file):
    output = None

    with StringIO() as output_data:
        convert_to_toggl(harvest_file, output_data, client_name="Test Client 123")
        output = output_data.getvalue()

    assert output
    assert isinstance(output, str)
    assert ",".join(TOGGL_COLUMNS) in output

    order = ["Start date", "Start time", "Email"]
    sample_output_df = pd.read_csv(toggl_file).sort_values(order)
    output_df = pd.read_csv(StringIO(output)).sort_values(order)

    assert set(output_df.columns.to_list()) <= set(sample_output_df.columns.to_list())
    assert output_df["Client"].eq("Test Client 123").all()
    assert output_df["Project"].eq("Test Client 123").all()


def test_converters():
    assert CONVERTERS.get("toggl") == convert_to_toggl
