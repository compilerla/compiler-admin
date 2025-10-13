# How to Reactivate a User

!!! seealso "Full Command Reference"

    For a complete reference of all options, see the [`compiler-admin user reactivate` reference section](../../reference/cli/user.md#compiler-admin-user-reactivate).

This guide explains how to use the `compiler-admin user reactivate` command to restore a previously deactivated user account.

## Actions Performed

The `reactivate` command performs the following actions:

- Checks that the user is currently in the "Alumni" OU (i.e., deactivated).
- Adds the user back to the default "Team" group.
- Moves the user to either the "Staff" or "Contractors" OU.
- If moved to "Staff", adds them to the "Staff" group.
- Resets their password and requires them to change it on next login.
- Can update their recovery email and phone number.
- Generates a new set of 2-Step Verification backup codes and prints them to the console.

## Basic Usage

To reactivate a user, provide their `username`. By default, they are reactivated as a contractor.

```bash
compiler-admin user reactivate some.user
```

The command will ask for confirmation before proceeding. To bypass this, use the `--force` flag.

## Reactivating as Staff

To reactivate a user as a full staff member, use the `--staff` flag.

```bash
compiler-admin user reactivate some.user --staff
```

## Setting Recovery and Notification Info

You can set the user's recovery information and notify them or a manager of the reactivation.

- `--recovery-email`: Sets the user's recovery email address.
- `--recovery-phone`: Sets the user's recovery phone number.
- `--notify`: Sends the new password credentials to the specified email address.

```bash
compiler-admin user reactivate some.user \
  --staff \
  --recovery-email some.user.personal@email.com \
  --notify manager@compiler.la
```
