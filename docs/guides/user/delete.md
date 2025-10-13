# How to Delete a User

!!! seealso "Full Command Reference"

    For a complete reference of all options, see the [`compiler-admin user delete` reference section](../../reference/cli/user.md#compiler-admin-user-delete).

This guide explains how to use the `compiler-admin user delete` command to permanently delete a user account from the Compiler Google Workspace.

**Warning:** This action is irreversible. All of the user's data that has not been transferred or backed up will be permanently lost. For a safer, more comprehensive process, use the `user offboard` command. The `offboard` command can also delete the user as its final step.

## Basic Usage

To delete a user, provide their `username`.

```bash
compiler-admin user delete some.user
```

The command will ask for confirmation before proceeding.

## Forcing the Deletion

To bypass the confirmation prompt, use the `--force` flag.

```bash
compiler-admin user delete some.user --force
```

## Important Safeguard

This command will fail if the user's email address has been assigned as an alias to another account. This is a safety measure to prevent accidental deletion of an active email alias. If you intend to delete the user, you must first remove the alias from the other account.
