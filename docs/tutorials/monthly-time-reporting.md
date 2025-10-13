# Monthly Time Reporting

This tutorial walks you through the complete workflow for processing monthly time reports, a common administrative task at Compiler. The process involves downloading time entries from Toggl, converting them to the format needed for other systems, verifying the data, and finally locking the entries in Toggl to prevent further changes.

## 1. Lock Time Entries in Toggl

Once you have verified the data and are confident the reports are accurate, the final step is to lock the time entries in Toggl. This prevents any further modifications to the time period you have just processed.

The `time lock` command locks entries up to a specific date. By default, it locks entries up to the last day of the previous month, which is exactly what we want in this scenario.

```bash
compiler-admin time lock
```

## 2. Download the Toggl Time Report

The first step is to download the detailed time entries from Toggl. The `time download` command handles this. By default, it downloads all billable time entries for the previous calendar month.

```bash
compiler-admin time download
```

This will create a CSV file in your current directory with a name like `Toggl_time_entries_YYYY-MM-DD_YYYY-MM-DD.csv`.

You can customize the date range and other filters. For a full list of options, run:

```bash
compiler-admin time download --help
```

## 3. Convert the Report Format

Next, you may need to convert the downloaded Toggl report into another format, such as the one used by Harvest. The `time convert` command is used for this.

It can read from a file or standard input and write to a file or standard output. Let's use the file we just downloaded as input and create a new file for the Harvest-formatted data.

```bash
# Let's assume the downloaded file is named
# toggl_report_2025-09.csv
compiler-admin time convert \
  --input toggl_report_2025-09.csv \
  --output harvest_report_2025-09.csv
```

This creates a new file, `harvest_report_2025-09.csv`, with the data correctly formatted for Harvest.

## 4. Verify the Conversion

Before proceeding, it's a good practice to verify that the data was converted correctly and that the totals match. The `time verify` command compares two time entry files.

```bash
compiler-admin time verify \
  Toggl_time_entries_2025-09-01_2025-09-30.csv \
  harvest_report_2025-09.csv
```

If the summaries of the two files match (total hours, hours per project, etc.), the command will exit silently with a "Summaries match." message. If there are discrepancies, it will print them.

After completing these steps, you have successfully downloaded, converted, verified, and finalized the time entries for the month.
