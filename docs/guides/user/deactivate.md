# How to Deactivate a User

!!! seealso "Full Command Reference"

    For a complete reference of all options, see the [`compiler-admin user deactivate` reference section](../../reference/cli/user.md#compiler-admin-user-deactivate).

This guide explains how to use the `compiler-admin user deactivate` command.

This command is a major step in the offboarding process. It secures an account by revoking access, clearing personal information, and moving the user to the "Alumni" organizational unit (OU). This command is automatically called as part of the more comprehensive `user offboard` command. For most offboarding scenarios, you should use `user offboard` instead.

## Actions Performed

The `deactivate` command performs the following actions:

- Removes the user from all of their groups.
- Moves the user to the "Alumni" OU.
- Resets their password to a random string.
- Signs the user out of all active sessions.
- Clears profile information (address, location, phone number, secondary email).
- Resets their recovery email and phone number.
- Turns off 2-Step Verification on their account.

## Basic Usage

To deactivate a user, provide their `username`.

```bash
compiler-admin user deactivate some.user
```

The command will ask for confirmation before proceeding. To bypass this, use the `--force` flag.

## Setting Recovery Information

You can set a new recovery email or phone number for the deactivated account using the `--recovery-email` and `--recovery-phone` options.

```bash
compiler-admin user deactivate some.user --recovery-email personal@email.com
```

To clear the recovery information, pass an empty string (which is the default):

```bash
compiler-admin user deactivate some.user --recovery-email "" --recovery-phone ""
```
