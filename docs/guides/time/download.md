# How to Download a Toggl Time Report

!!! seealso "Full Command Reference"

    For a complete reference of all options, see the [`compiler-admin time download` reference section](../../reference/cli/time.md#compiler-admin-time-download).

This guide explains how to use the `compiler-admin time download` command to download a detailed time report from Toggl in CSV format.

## Basic Usage

To download a report for the previous calendar month (the default behavior):

```bash
compiler-admin time download
```

This will create a CSV file in the current directory named `Toggl_time_entries_[start-date]_[end-date].csv`.

## Specifying a Date Range

You can specify a custom date range using the `--start` and `--end` options. The date format is `YYYY-MM-DD`.

```bash
compiler-admin time download --start 2025-01-01 --end 2025-01-31
```

## Specifying an Output File

To save the report to a specific file path, use the `--output` option.

```bash
compiler-admin time download --output /path/to/my-report.csv
```

## Filtering the Report

The command provides several options for filtering the time entries included in the report:

- `--all`: Include all time entries, not just billable ones.
- `-c, --client CLIENT_ID`: Filter by a specific Toggl client ID.
- `-p, --project PROJECT_ID`: Filter by a specific Toggl project ID.
- `-t, --task TASK_ID`: Filter by a specific Toggl task ID.
- `-u, --user USER_ID`: Filter by a specific Toggl user ID.

You can use these options multiple times to include multiple IDs.

### Example

To download all billable time entries for Project ID `12345` and `67890` for the prior month:

```bash
compiler-admin time download -p 12345 -p 67890
```
