# How to Sign a User Out of All Sessions

!!! seealso "Full Command Reference"

    For a complete reference of all options, see the [`compiler-admin user signout` reference section](../../reference/cli/user.md#compiler-admin-user-signout).

This guide explains how to use the `compiler-admin user signout` command to immediately invalidate a user's login sessions on all devices.

This is useful in case a device is lost or stolen, or if an account is suspected of being compromised. This command is also called automatically as part of the `user reset` and `user deactivate` commands.

## Basic Usage

To sign a user out, provide their `username`.

```bash
compiler-admin user signout some.user
```

The command will ask for confirmation before proceeding.

## Forcing the Signout

To bypass the confirmation prompt, use the `--force` flag.

```bash
compiler-admin user signout some.user --force
```

This will immediately revoke all of the user's active Google sessions.
