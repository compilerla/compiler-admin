# How to Verify Time Reports

!!! seealso "Full Command Reference"

    For a complete reference of all options, see the [`compiler-admin time verify` reference section](../../reference/cli/time.md#compiler-admin-time-verify).

This guide explains how to use the `compiler-admin time verify` command to check the contents of time report CSV files.

You can use this command in two ways:

1. To get a summary of a single time report.
2. To compare two different time reports (e.g., a Toggl export and a converted Harvest file) to ensure they match.

## Summarizing a Single Report

To see a summary of a single CSV file, provide its path to the command:

```bash
compiler-admin time verify toggl-report.csv
```

The output will show you a summary of the data in that file, including:

- Date range
- Total number of entries
- Total hours
- Hours broken down by project
- Hours broken down by user and project

```text
Summary for: toggl-report.csv
  Date range: 2025-09-01 - 2025-09-30

  Total entries: 150
  Total hours: 160.0
  Project A: 80.0
  Project B: 50.0
  Project C: 30.0

  user1@example.com:
    Project A: 40.0
    Project B: 20.0
  user2@example.com:
    Project A: 40.0
    Project B: 30.0
    Project C: 30.0
```

## Comparing Two Reports

To verify that a conversion was successful, you can provide two file paths. The command will compare their summaries.

The tool automatically detects the file format (Toggl or Harvest) and normalizes the data so that a meaningful comparison can be made.

```bash
compiler-admin time verify toggl-report.csv harvest-report.csv
```

If the reports match, the command will output "Summaries match." and exit successfully.

If there are differences in total hours, projects, or other details, the command will print a list of the discrepancies and exit with an error.

```text
Summaries do not match:
- Total hours: 160.0 vs 155.0
  Project 'Project B' hours: 50.0 vs 45.0
  User 'user1@example.com', Project 'Project B' hours: 20.0 vs 15.0
```
