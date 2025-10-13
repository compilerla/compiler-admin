# How to Offboard a User

!!! seealso "Full Command Reference"

    For a complete reference of all options, see the [`compiler-admin user offboard` reference section](../../reference/cli/user.md#compiler-admin-user-offboard).

This guide explains how to use the `compiler-admin user offboard` command to completely and securely offboard a user from the Compiler Google Workspace.

This is a comprehensive command that orchestrates several other actions. For most offboarding scenarios, this is the command you should use.

## Actions Performed

The `offboard` command performs the following sequence of actions:

1. **Deactivates the user account**: It runs all the steps from the `user deactivate` command (moves to Alumni OU, resets password, signs out, clears profile info, etc.).
2. **Backs up email**: It creates a full backup of the user's Gmail inbox and stores it locally in a `GYB-GMail-Backup-user@compiler.la` directory.
3. **Transfers data**: It initiates a transfer of the user's Google Drive files and Google Calendar events to the `archive@compiler.la` account.
4. **Deprovisions access**: It deprovisions POP and IMAP access for the account.
5. **Sets an alias (optional)**: It can assign the user's email address as an alias to another account.
6. **Deletes the account (optional)**: It can permanently delete the user's account after all other steps are complete.

## Basic Usage

To offboard a user, provide their `username`.

```bash
compiler-admin user offboard departing.user
```

The command will ask for confirmation before proceeding. To bypass this, use the `--force` flag.

## Assigning an Alias

To forward the user's future emails to a manager or a shared inbox, use the `--alias` option.

```bash
compiler-admin user offboard departing.user --alias manager.user
```

## Deleting the Account

If the account should be permanently deleted after the data is backed up and transferred, add the `--delete` flag. **Use this option with caution.**

```bash
compiler-admin user offboard departing.user --delete
```
