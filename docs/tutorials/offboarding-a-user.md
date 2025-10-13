# Offboarding a User

This tutorial covers the process of securely offboarding a user from the Compiler Google Workspace. The `compiler-admin` tool automates several critical steps to ensure a smooth and secure transition.

## 1. Offboard the User

The `user offboard` command is a comprehensive script that handles the main steps of offboarding:

- Deactivates the user's account and moves them to the "Alumni" organizational unit (OU).
- Resets their password and signs them out of all active sessions.
- Removes them from all Google Groups.
- Backs up their entire Gmail inbox to a local directory on the machine running the tool.
- Initiates the transfer of their Google Drive and Calendar data to the `archive@compiler.la` user.
- Deprovisions POP/IMAP access.

To run the command, you simply need to provide the user's `username`.

```bash
compiler-admin user offboard departing_username
```

### Assigning an Alias

It's common practice to forward the departing user's email to a manager or a general-purpose inbox. You can do this by assigning their email address as an alias to another account using the `--alias` option.

```bash
compiler-admin user offboard departing_username --alias manager_username
```

### Deleting the Account

By default, the user's account is deactivated but not deleted. If you need to permanently delete the account after the offboarding process is complete, you can add the `--delete` flag.

```bash
# Use with caution!
compiler-admin user offboard departing_username --delete
```

The command will ask for confirmation before proceeding unless you also add the `--force` flag.

## 2. Restoring an Email Backup

The offboarding process creates a local backup of the user's Gmail inbox in a directory named `GYB-GMail-Backup-user@compiler.la`.

If you ever need to access this backup, you can restore it to the central `archive@compiler.la` account. The `user restore` command handles this. It will upload the emails from the backup directory and apply a label with the user's original email address, so they are easy to find.

To restore a backup for `departing_username`:

```bash
compiler-admin user restore departing_username
```

This completes the offboarding and data archival process.
