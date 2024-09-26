from argparse import Namespace
from datetime import datetime
import pytest

from compiler_admin import RESULT_SUCCESS
from compiler_admin.commands.time.download import __name__ as MODULE, download, TOGGL_COLUMNS


@pytest.fixture
def mock_download_time_entries(mocker):
    return mocker.patch(f"{MODULE}.download_time_entries")


def test_download_default(mock_download_time_entries):
    date = datetime.now()
    args = Namespace(
        start=date,
        end=date,
        output="output",
        client_ids=None,
        project_ids=None,
        task_ids=None,
        user_ids=None,
    )

    res = download(args)

    assert res == RESULT_SUCCESS
    mock_download_time_entries.assert_called_once_with(
        start_date=args.start,
        end_date=args.end,
        output_path=args.output,
        output_cols=TOGGL_COLUMNS,
    )


def test_download_ids(mock_download_time_entries):
    date = datetime.now()
    ids = [1, 2, 3]
    args = Namespace(start=date, end=date, output="output", client_ids=ids, project_ids=ids, task_ids=ids, user_ids=ids)

    res = download(args)

    assert res == RESULT_SUCCESS
    mock_download_time_entries.assert_called_once_with(
        start_date=args.start,
        end_date=args.end,
        output_path=args.output,
        output_cols=TOGGL_COLUMNS,
        client_ids=ids,
        project_ids=ids,
        task_ids=ids,
        user_ids=ids,
    )
