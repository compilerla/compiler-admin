from datetime import datetime
import pytest

from compiler_admin import RESULT_SUCCESS
from compiler_admin.commands.time.download import (
    __name__ as MODULE,
    download,
    TOGGL_COLUMNS,
    TZINFO,
    prior_month_end,
    prior_month_start,
)


@pytest.fixture
def mock_local_now(mocker):
    dt = datetime(2024, 9, 25, tzinfo=TZINFO)
    mocker.patch(f"{MODULE}.local_now", return_value=dt)
    return dt


@pytest.fixture
def mock_start(mock_local_now):
    return datetime(2024, 8, 1, tzinfo=TZINFO)


@pytest.fixture
def mock_end(mock_local_now):
    return datetime(2024, 8, 31, tzinfo=TZINFO)


@pytest.fixture
def mock_download_time_entries(mocker):
    return mocker.patch(f"{MODULE}.download_time_entries")


def test_prior_month_start(mock_start):
    start = prior_month_start()

    assert start == mock_start


def test_prior_month_end(mock_end):
    end = prior_month_end()

    assert end == mock_end


def test_download(cli_runner, mock_download_time_entries):
    date = datetime.now(tz=TZINFO).replace(hour=0, minute=0, second=0, microsecond=0)
    args = [
        "--start",
        date.strftime("%Y-%m-%d %H:%M:%S%z"),
        "--end",
        date.strftime("%Y-%m-%d %H:%M:%S%z"),
        "--output",
        "output",
        "-c",
        1,
        "-c",
        2,
        "-p",
        3,
        "-p",
        4,
        "-t",
        5,
        "-t",
        6,
        "-u",
        7,
        "-u",
        8,
    ]

    result = cli_runner.invoke(download, args)

    assert result.exit_code == RESULT_SUCCESS
    mock_download_time_entries.assert_called_once_with(
        start_date=date,
        end_date=date,
        output_path="output",
        billable=True,
        output_cols=TOGGL_COLUMNS,
        client_ids=(1, 2),
        project_ids=(3, 4),
        task_ids=(5, 6),
        user_ids=(7, 8),
    )


def test_download_client_envvar(cli_runner, monkeypatch, mock_download_time_entries):
    monkeypatch.setenv("TOGGL_CLIENT_ID", 1234)

    date = datetime.now(tz=TZINFO).replace(hour=0, minute=0, second=0, microsecond=0)
    args = [
        "--start",
        date.strftime("%Y-%m-%d %H:%M:%S%z"),
        "--end",
        date.strftime("%Y-%m-%d %H:%M:%S%z"),
        "--output",
        "output",
    ]

    result = cli_runner.invoke(download, args)

    assert result.exit_code == RESULT_SUCCESS
    mock_download_time_entries.assert_called_once_with(
        start_date=date, end_date=date, output_path="output", output_cols=TOGGL_COLUMNS, billable=True, client_ids=(1234,)
    )


def test_download_all(cli_runner, monkeypatch, mock_download_time_entries):
    monkeypatch.delenv("TOGGL_CLIENT_ID", raising=False)
    date = datetime.now(tz=TZINFO).replace(hour=0, minute=0, second=0, microsecond=0)
    args = [
        "--start",
        date.strftime("%Y-%m-%d %H:%M:%S%z"),
        "--end",
        date.strftime("%Y-%m-%d %H:%M:%S%z"),
        "--output",
        "output",
        "--all",
    ]

    result = cli_runner.invoke(download, args)

    assert result.exit_code == RESULT_SUCCESS
    mock_download_time_entries.assert_called_once_with(
        start_date=date, end_date=date, output_path="output", output_cols=TOGGL_COLUMNS
    )
