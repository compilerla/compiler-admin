from argparse import Namespace
from datetime import datetime
import pytest

from compiler_admin import RESULT_SUCCESS
from compiler_admin.commands.time.download import __name__ as MODULE, download, TOGGL_COLUMNS


@pytest.fixture
def mock_download_time_entries(mocker):
    return mocker.patch(f"{MODULE}.download_time_entries")


@pytest.mark.parametrize("billable", [True, False])
def test_download(mock_download_time_entries, billable):
    date = datetime.now()
    args = Namespace(
        start=date,
        end=date,
        output="output",
        billable=billable,
        client_ids=["c1", "c2"],
        project_ids=["p1", "p2"],
        task_ids=["t1", "t2"],
        user_ids=["u1", "u2"],
    )

    res = download(args)

    assert res == RESULT_SUCCESS
    mock_download_time_entries.assert_called_once_with(
        start_date=args.start,
        end_date=args.end,
        output_path=args.output,
        output_cols=TOGGL_COLUMNS,
        billable=args.billable,
        client_ids=args.client_ids,
        project_ids=args.project_ids,
        task_ids=args.task_ids,
        user_ids=args.user_ids,
    )
