# How to Get Information About Users

!!! seealso "Full Command Reference"

    For a complete reference of all options, see the [`compiler-admin ls` reference section](../../reference/cli/ls.md).

This guide explains how to use the `compiler-admin ls` command to list users and other related information from the Compiler workspace.

## Actions Performed

The `ls users` command prints information about users, such as email address, name, and user ID.

## Basic Usage

To list users in the Compiler workspace, call the command without any arguments:

```console
compiler-admin ls users
```

The output will be a list of email addresses of active users in the Compiler Google workspace.

## Listing Another System

To list users in a specific system, use the `system` argument.

```console
compiler-admin ls users toggl
```

## Showing Inactive Users

You can view inactive users in the system with the `--inactive` flag.

```console
compiler-admin ls users --inactive
```

## Changing the Output Format

To get more user details, use the `--format` flag:

```console
compiler-admin ls users --format csv
```

Or for even more detailed JSON output:

```console
compiler-admin ls users --format json
```

## Listing Toggl Resources

Because Toggl is the primary source for workspace project metadata today, `compiler-admin ls` also supports Toggl-specific list operations:

```console
compiler-admin ls clients
compiler-admin ls projects
compiler-admin ls project-users
```

Each command supports the `--format` flag and filtering options such as `--id`, `--client-id`, and `--name`.

### Detailed Output

Use `--format csv` or `--format json` to get all available fields from the Toggl Track API:

```console
compiler-admin ls projects --format csv
compiler-admin ls clients --format csv
```

The basic format (`--format basic`, the default) returns a concise subset of common fields. CSV and JSON formats include everything the Track API provides, excluding only internal/auxiliary fields.
