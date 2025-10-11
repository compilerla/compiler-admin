from datetime import date, datetime, timedelta

import click

from compiler_admin.services.toggl import lock_time_entries


@click.command()
@click.option(
    "--date",
    "lock_date_str",
    help="The date to lock time entries, formatted as YYYY-MM-DD. Defaults to the last day of the previous month.",
)
def lock(lock_date_str):
    """Lock Toggl time entries."""
    if lock_date_str:
        lock_date = datetime.strptime(lock_date_str, "%Y-%m-%d")
    else:
        today = date.today()
        first_day_of_current_month = today.replace(day=1)
        lock_date = first_day_of_current_month - timedelta(days=1)

    click.echo(f"Locking time entries on or before: {lock_date.strftime('%Y-%m-%d')}")
    lock_time_entries(lock_date)
    click.echo("Done.")
