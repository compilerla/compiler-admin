from datetime import date

from compiler_admin.services.time import TimeSummary


def test_TimeSummary_initialization():
    """Test that TimeSummary initializes with default values."""
    summary = TimeSummary()
    assert summary.earliest_date is None
    assert summary.latest_date is None
    assert summary.total_rows == 0
    assert summary.total_hours == 0.0
    assert summary.hours_per_project == {}
    assert summary.hours_per_user_project == {}


def test_TimeSummary_with_values():
    """Test that TimeSummary initializes with specified values."""
    earliest = date(2025, 1, 1)
    latest = date(2025, 1, 31)
    summary = TimeSummary(
        earliest_date=earliest,
        latest_date=latest,
        total_rows=10,
        total_hours=40.5,
        hours_per_project={"Project A": 20.0},
        hours_per_user_project={"user@example.com": {"Project A": 20.0}},
    )
    assert summary.earliest_date == earliest
    assert summary.latest_date == latest
    assert summary.total_rows == 10
    assert summary.total_hours == 40.5
    assert summary.hours_per_project == {"Project A": 20.0}
    assert summary.hours_per_user_project == {"user@example.com": {"Project A": 20.0}}
