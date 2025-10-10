import click
import sys

from compiler_admin.services import harvest, toggl
from compiler_admin.services.time import TimeSummary
from compiler_admin.services.toggl import normalize_summary

SUMMARIZERS = {
    "harvest": harvest.summarize,
    "toggl": toggl.summarize,
}


def detect_file_type(file_path: str) -> str:
    """Detect the type of a time entry CSV file.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        str: The type of the file (harvest or toggl).
    """
    with open(file_path, "r") as f:
        header = f.readline().lower()
        if "hours" in header:
            return "harvest"
        elif "duration" in header:
            return "toggl"
        else:
            raise ValueError(f"Unknown file type for {file_path}")


def _diff_summaries(summary1: TimeSummary, summary2: TimeSummary):
    diffs = []
    if summary1.earliest_date != summary2.earliest_date:
        diffs.append(f"Earliest date: {summary1.earliest_date} vs {summary2.earliest_date}")
    if summary1.latest_date != summary2.latest_date:
        diffs.append(f"Latest date: {summary1.latest_date} vs {summary2.latest_date}")
    if summary1.total_rows != summary2.total_rows:
        diffs.append(f"Total rows: {summary1.total_rows} vs {summary2.total_rows}")
    if summary1.total_hours != summary2.total_hours:
        diffs.append(f"Total hours: {summary1.total_hours} vs {summary2.total_hours}")
    if summary1.hours_per_project != summary2.hours_per_project:
        diffs.append("Hours per project differ.")
    if summary1.hours_per_user_project != summary2.hours_per_user_project:
        diffs.append("Hours per user/project differ.")
    return diffs


@click.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True))
def verify(files: list[str]):
    """Verify time entry CSV files."""
    if not 1 <= len(files) <= 2:
        click.echo("Please provide one or two files to verify.")
        return

    summaries = []
    for file_path in files:
        try:
            file_type = detect_file_type(file_path)
            summarizer = SUMMARIZERS[file_type]
            summary = summarizer(file_path)
            summaries.append(summary)
        except (ValueError, KeyError) as e:
            click.echo(f"Error processing file {file_path}: {e}", err=True)
            return

    if len(summaries) == 1:
        click.echo(f"Summary for: {files[0]}")
        summary: TimeSummary = summaries[0]
        click.echo(f"  Date range: {summary.earliest_date} - {summary.latest_date}")
        click.echo()
        click.echo(f"  Total entries: {summary.total_rows}")
        click.echo(f"  Total hours: {summary.total_hours}")
        for project, hours in summary.hours_per_project.items():
            click.echo(f"  {project}: {hours}")
        click.echo()
        for user, project_hours in summary.hours_per_user_project.items():
            click.echo(f"  {user}:")
            for project, hours in project_hours.items():
                click.echo(f"    {project}: {hours}")
    elif len(summaries) == 2:
        summary1, summary2 = summaries
        file1_type = detect_file_type(files[0])
        file2_type = detect_file_type(files[1])

        if file1_type == "toggl" and file2_type == "harvest":
            summary1 = normalize_summary(summary1)
        elif file1_type == "harvest" and file2_type == "toggl":
            summary2 = normalize_summary(summary2)

        if summary1 == summary2:
            click.echo("Summaries match.")
        else:
            click.echo("Summaries do not match:", err=True)
            diffs = _diff_summaries(summary1, summary2)
            for diff in diffs:
                click.echo(f"- {diff}", err=True)
            sys.exit(1)
