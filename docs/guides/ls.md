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
