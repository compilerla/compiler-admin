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
    args = Namespace(start=date, end=date, output="output")

    res = download(args)

    assert res == RESULT_SUCCESS
    mock_download_time_entries.assert_called_once_with(args.start, args.end, args.output, TOGGL_COLUMNS)
