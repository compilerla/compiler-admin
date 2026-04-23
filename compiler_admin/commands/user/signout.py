import click

from compiler_admin import Result
from compiler_admin.services.google import GoogleAccount, GoogleUsers


@click.command()
@click.option("-f", "--force", is_flag=True, help="Don't ask for confirmation.")
@click.argument("username")
def signout(username: str, force: bool = False, **kwargs):
    """Sign a user out from all active sessions."""
    account = GoogleAccount(username)
    google = GoogleUsers()

    if not account.exists():
        click.echo(f"User does not exist: {account}")
        raise SystemExit(Result.FAILURE)

    if not force:
        cont = input(f"Signout account {account} from all active sessions? (Y/n): ")
        if not cont.lower().startswith("y"):
            click.echo("Aborting signout.")
            raise SystemExit(Result.SUCCESS)

    click.echo(f"User exists, signing out from all active sessions: {account}")

    google.signout(account)
