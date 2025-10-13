# How to Reset a User's Password

!!! seealso "Full Command Reference"

    For a complete reference of all options, see the [`compiler-admin user reset` reference section](../../reference/cli/user.md#compiler-admin-user-reset).

This guide explains how to use the `compiler-admin user reset` command to reset a user's password and sign them out of all sessions.

## Actions Performed

The `reset` command performs two main actions:

1. Generates a new, random password for the user and sets the requirement that they must change it on their next login.
2. Immediately signs the user out of all active Google sessions on all devices.

## Basic Usage

To reset a user's password, provide their `username`.

```bash
compiler-admin user reset some.user
```

The command will ask for confirmation before proceeding.

## Forcing the Reset

To bypass the confirmation prompt, use the `--force` flag.

```bash
compiler-admin user reset some.user --force
```

## Notifying the User or a Manager

You can send the new temporary password to the user or their manager using the `--notify` option.

```bash
compiler-admin user reset some.user --notify manager@compiler.la
```
