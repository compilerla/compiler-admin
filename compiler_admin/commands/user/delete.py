import click

from compiler_admin import Result
from compiler_admin.services.google import GoogleAccount, GoogleUsers


@click.command()
@click.option("-f", "--force", is_flag=True, help="Don't ask for confirmation.")
@click.argument("username")
def delete(username: str, force: bool = False, **kwargs):
    """Delete a user account."""
    account = GoogleAccount(username)
    google = GoogleUsers(account)

    if not account.exists():
        click.echo(f"User does not exist: {account}")
        raise SystemExit(Result.FAILURE)

    if not force:
        cont = input(f"Delete account {account}? (Y/n): ")
        if not cont.lower().startswith("y"):
            click.echo("Aborting delete.")
            return

    click.echo(f"User exists, deleting: {account}")
    google.delete(account)
