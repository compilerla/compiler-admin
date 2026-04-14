# How to Get Information About Users

!!! seealso "Full Command Reference"

    For a complete reference of all options, see the [`compiler-admin user ls` reference section](../../reference/cli/user.md#compiler-admin-user-ls).

This guide explains how to use the `compiler-admin user ls` command to list users in the Compiler workspace.

## Actions Performed

The `ls` command prints information about users, such as email address, name, and user ID.

## Basic Usage

To list users in the Compiler workspace, call the command without any arguments:

```console
compiler-admin user ls
```

The output will be a list of email addresses of active users in the Compiler Google workspace.

## Listing Another System

To list users in a specific system, use the `system` argument.

```console
compiler-admin user ls toggl
```

## Showing Inactive Users

You can view inactive users in the system with the `--inactive` flag.

```console
compiler-admin user ls --inactive
```

## Changing the Output Format

To get more user details, use the `--format` flag:

```console
compiler-admin user ls --format csv
```

Or for even more detailed JSON output:

```console
compiler-admin user ls --format json
```
