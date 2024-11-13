from datetime import datetime
import pytest

from compiler_admin import RESULT_SUCCESS
from compiler_admin.commands_click.time.download import __name__ as MODULE, download, TOGGL_COLUMNS, TZINFO


@pytest.fixture
def mock_download_time_entries(mocker):
    return mocker.patch(f"{MODULE}.download_time_entries")


@pytest.mark.parametrize("billable", [True, False])
def test_download(cli_runner, mock_download_time_entries, billable):
    date = datetime.now(tz=TZINFO).replace(hour=0, minute=0, second=0, microsecond=0)
    args = [
        "--start",
        date.strftime("%Y-%m-%d"),
        "--end",
        date.strftime("%Y-%m-%d"),
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

    if not billable:
        args.append("--all")

    result = cli_runner.invoke(download, args)

    assert result.exit_code == RESULT_SUCCESS
    mock_download_time_entries.assert_called_once_with(
        start_date=date,
        end_date=date,
        output_path="output",
        output_cols=TOGGL_COLUMNS,
        billable=billable,
        client_ids=(1, 2),
        project_ids=(3, 4),
        task_ids=(5, 6),
        user_ids=(7, 8),
    )
