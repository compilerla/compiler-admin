# How to Restore an Email Backup

!!! seealso "Full Command Reference"

    For a complete reference of all options, see the [`compiler-admin user restore` reference section](../../reference/cli/user.md#compiler-admin-user-restore).

This guide explains how to use the `compiler-admin user restore` command to restore a user's Gmail backup into the central `archive@compiler.la` account.

This command is used to access the emails of a user who was previously offboarded using the `user offboard` command, which creates a local backup directory.

## Prerequisites

Before running the restore command, you must have the user's local email backup directory. This directory is created by the `user offboard` command and is named in the format `GYB-GMail-Backup-username@compiler.la`.

This command must be run from the same parent directory where the backup folder is located.

## Basic Usage

To restore a backup for a given `username`, run the following command:

```bash
compiler-admin user restore departing.user
```

This command will:

1. Locate the backup directory `GYB-GMail-Backup-departing.user@compiler.la`.
2. Connect to the `archive@compiler.la` mailbox.
3. Upload all emails from the backup directory into the archive mailbox.
4. Apply a new Gmail label to all restored emails with the user's original email address (`departing.user@compiler.la`) so they can be easily found and filtered within the archive account.
