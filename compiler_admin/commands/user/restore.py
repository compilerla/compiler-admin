import pathlib

import click

from compiler_admin import Result
from compiler_admin.services.google import GoogleAccount, GoogleArchive, GoogleUsers


@click.command()
@click.argument("username")
def restore(username: str):
    """Restore an email backup from a prior offboarding."""
    account = GoogleAccount(username)
    backup_dir = f"GYB-GMail-Backup-{account}"

    if not pathlib.Path(backup_dir).exists():
        click.echo(f"Couldn't find a local backup: {backup_dir}")
        raise SystemExit(Result.FAILURE)

    click.echo(f"Found backup, starting restore process with dest: {GoogleUsers.USER_ARCHIVE} for account: {account}")

    GoogleArchive().restore_email_backup(account=account, backup_dir=backup_dir)

    click.echo(f"Email restore complete for: {account}")
