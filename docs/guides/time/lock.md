# How to Lock Time Entries in Toggl

!!! seealso "Full Command Reference"

    For a complete reference of all options, see the [`compiler-admin time lock` reference section](../../reference/cli/time.md#compiler-admin-time-lock).

This guide explains how to use the `compiler-admin time lock` command to lock time entries in Toggl, preventing them from being edited.

This is typically the first step before downloading and preparing time reports.

You can see the current lock date at <https://track.toggl.com/${TOGGL_WORKSPACE_ID}/settings/general>.

## Basic Usage

To lock time entries up to the last day of the previous calendar month (the default behavior), run the command without any options:

```bash
compiler-admin time lock
```

The command will print the date it is locking entries up to and ask for confirmation before proceeding.

## Specifying a Lock Date

You can lock entries up to any specific date using the `--date` option. The date format is `YYYY-MM-DD`.

For example, to lock all entries on or before January 31, 2025:

```bash
compiler-admin time lock --date 2025-01-31
```
