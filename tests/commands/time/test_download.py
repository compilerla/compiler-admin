from datetime import datetime
import pytest

from compiler_admin import RESULT_SUCCESS
from compiler_admin.commands.time.download import (
    __name__ as MODULE,
    TOGGL_COLUMNS,
    TZINFO,
    download,
    prior_month_end,
    prior_month_start,
)


@pytest.fixture
def mock_local_now(mocker):
    dt = datetime(2024, 9, 25, tzinfo=TZINFO)
    mocker.patch(f"{MODULE}.local_now", return_value=dt)
    return dt


@pytest.fixture
def mock_download_time_entries(mocker):
    return mocker.patch(f"{MODULE}.download_time_entries")


def test_prior_month_start(mock_local_now):
    start = prior_month_start()

    assert start.year == 2024
    assert start.month == 8
    assert start.day == 1
    assert start.tzinfo == TZINFO


def test_prior_month_end(mock_local_now):
    end = prior_month_end()

    assert end.year == 2024
    assert end.month == 8
    assert end.day == 31
    assert end.tzinfo == TZINFO


def test_download(cli_runner, mock_local_now, mock_download_time_entries):
    args = [
        "--start",
        mock_local_now.strftime("%Y-%m-%d"),
        "--end",
        mock_local_now.strftime("%Y-%m-%d"),
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
        start_date=mock_local_now,
        end_date=mock_local_now,
        output_path="output",
        billable=True,
        output_cols=TOGGL_COLUMNS,
        client_ids=(1, 2),
        project_ids=(3, 4),
        task_ids=(5, 6),
        user_ids=(7, 8),
    )


def test_download_default(cli_runner, mock_download_time_entries):
    expected_start, expected_end = prior_month_start(), prior_month_end()

    result = cli_runner.invoke(download, [])

    assert result.exit_code == RESULT_SUCCESS
    mock_download_time_entries.assert_called_once()
    call = mock_download_time_entries.mock_calls[0]

    actual_start = call.kwargs["start_date"]
    assert actual_start.year == expected_start.year
    assert actual_start.month == expected_start.month
    assert actual_start.day == expected_start.day

    actual_end = call.kwargs["end_date"]
    assert actual_end.year == expected_end.year
    assert actual_end.month == expected_end.month
    assert actual_end.day == expected_end.day

    assert (
        call.kwargs["output_path"]
        == f"Toggl_time_entries_{expected_start.strftime('%Y-%m-%d')}_{expected_end.strftime('%Y-%m-%d')}.csv"
    )
    assert call.kwargs["output_cols"] == TOGGL_COLUMNS
    assert call.kwargs["billable"] is True


def test_download_client_envvar(cli_runner, monkeypatch, mock_download_time_entries):
    monkeypatch.setenv("TOGGL_CLIENT_ID", 1234)

    result = cli_runner.invoke(download, [])

    assert result.exit_code == RESULT_SUCCESS
    mock_download_time_entries.assert_called_once()
    call = mock_download_time_entries.mock_calls[0]
    assert call.kwargs["client_ids"] == (1234,)


def test_download_all(cli_runner, mock_download_time_entries):
    result = cli_runner.invoke(download, ["--all"])

    assert result.exit_code == RESULT_SUCCESS
    mock_download_time_entries.assert_called_once()
    call = mock_download_time_entries.mock_calls[0]
    assert "billable" not in call.kwargs
