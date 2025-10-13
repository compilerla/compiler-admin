import click

from compiler_admin import RESULT_FAILURE
from compiler_admin.services.google import get_backup_codes, user_account_name, user_exists


@click.command()
@click.argument("username")
def backupcodes(username: str, **kwargs):
    """Get backup codes for the user, creating a new set if needed."""
    account = user_account_name(username)

    if not user_exists(account):
        click.echo(f"User does not exist: {account}")
        raise SystemExit(RESULT_FAILURE)

    backup_codes = get_backup_codes(account)
    click.echo(backup_codes)
