import click

from compiler_admin import RESULT_FAILURE
from compiler_admin.services.google import CallGAMCommand, user_account_name, user_exists


@click.command()
@click.option("-f", "--force", is_flag=True, help="Don't ask for confirmation.")
@click.argument("username")
def delete(username: str, force: bool = False, **kwargs):
    """
    Delete a user account.
    """
    account = user_account_name(username)

    if not user_exists(account):
        click.echo(f"User does not exist: {account}")
        raise SystemExit(RESULT_FAILURE)

    if not force:
        cont = input(f"Delete account {account}? (Y/n): ")
        if not cont.lower().startswith("y"):
            click.echo("Aborting delete.")
            return

    click.echo(f"User exists, deleting: {account}")

    CallGAMCommand(("delete", "user", account, "noactionifalias"))
