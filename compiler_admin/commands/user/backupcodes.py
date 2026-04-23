import click

from compiler_admin import Result
from compiler_admin.services.google import GoogleAccount


@click.command()
@click.argument("username")
def backupcodes(username: str, **kwargs):
    """Get backup codes for the user, creating a new set if needed."""
    account = GoogleAccount(username)

    if not account.exists():
        click.echo(f"User does not exist: {account}")
        raise SystemExit(Result.FAILURE)

    backup_codes = account.get_backup_codes()
    click.echo(backup_codes)
