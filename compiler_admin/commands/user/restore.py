import pathlib

import click

from compiler_admin import RESULT_FAILURE
from compiler_admin.services.google import USER_ARCHIVE, CallGYBCommand, user_account_name


@click.command()
@click.argument("username")
def restore(username: str):
    """Restore an email backup from a prior offboarding."""
    account = user_account_name(username)
    backup_dir = f"GYB-GMail-Backup-{account}"

    if not pathlib.Path(backup_dir).exists():
        click.echo(f"Couldn't find a local backup: {backup_dir}")
        raise SystemExit(RESULT_FAILURE)

    click.echo(f"Found backup, starting restore process with dest: {USER_ARCHIVE} for account: {account}")

    CallGYBCommand(
        (
            "--service-account",
            "--email",
            USER_ARCHIVE,
            "--action",
            "restore",
            "--local-folder",
            backup_dir,
            "--label-restored",
            account,
        )
    )

    click.echo(f"Email restore complete for: {account}")
