from datetime import date, datetime, timedelta

import pytest
from click.testing import CliRunner

from compiler_admin import Result
from compiler_admin.commands.time.lock import TogglTime, lock


@pytest.fixture
def mock_lock_time_entries(mocker):
    return mocker.patch.object(TogglTime, "lock")


def test_lock_default_date(mock_lock_time_entries):
    runner = CliRunner()
    result = runner.invoke(lock)

    assert result.exit_code == Result.SUCCESS
    today = date.today()
    first_day_of_current_month = today.replace(day=1)
    lock_date = first_day_of_current_month - timedelta(days=1)
    mock_lock_time_entries.assert_called_once_with(lock_date)


def test_lock_with_date(mock_lock_time_entries):
    runner = CliRunner()
    lock_date_str = "2025-10-11"
    result = runner.invoke(lock, ["--date", lock_date_str])

    assert result.exit_code == Result.SUCCESS
    lock_date = datetime.strptime(lock_date_str, "%Y-%m-%d")
    mock_lock_time_entries.assert_called_once_with(lock_date)
