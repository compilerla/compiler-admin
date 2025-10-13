# How to Get a User's 2FA Backup Codes

!!! seealso "Full Command Reference"

    For a complete reference of all options, see the [`compiler-admin user backupcodes` reference section](../../reference/cli/user.md#compiler-admin-user-backupcodes).

This guide explains how to use the `compiler-admin user backupcodes` command to get a list of active 2-Step Verification backup codes for a user.

This can be useful if a user has lost their primary 2FA device and any recovery options.

## Basic Usage

To get backup codes for a user, provide their `username`.

```bash
compiler-admin user backupcodes some.user
```

The command will perform the following actions:

1. Check if the user has existing backup codes.
2. If they do, it will print them.
3. If they do not, it will generate a new set of backup codes and print them.

The output will be a list of the user's one-time-use backup codes.
