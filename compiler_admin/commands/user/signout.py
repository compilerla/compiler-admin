import click

from compiler_admin import RESULT_FAILURE, RESULT_SUCCESS
from compiler_admin.services.google import CallGAMCommand, user_account_name, user_exists


@click.command()
@click.option("-f", "--force", is_flag=True, help="Don't ask for confirmation.")
@click.argument("username")
def signout(username: str, force: bool = False, **kwargs):
    """Sign a user out from all active sessions."""
    account = user_account_name(username)

    if not user_exists(account):
        click.echo(f"User does not exist: {account}")
        raise SystemExit(RESULT_FAILURE)

    if not force:
        cont = input(f"Signout account {account} from all active sessions? (Y/n): ")
        if not cont.lower().startswith("y"):
            click.echo("Aborting signout.")
            raise SystemExit(RESULT_SUCCESS)

    click.echo(f"User exists, signing out from all active sessions: {account}")

    CallGAMCommand(("user", account, "signout"))
