import click

from compiler_admin import Result
from compiler_admin.commands.user.signout import signout
from compiler_admin.services.google import GoogleAccount, GoogleUsers


@click.command()
@click.option("-f", "--force", is_flag=True, help="Don't ask for confirmation.")
@click.option("-n", "--notify", help="An email address to send the new password notification.")
@click.argument("username")
@click.pass_context
def reset(ctx: click.Context, username: str, force: bool = False, notify: str = "", **kwargs):
    """Reset a user's password."""
    account = GoogleAccount(username)
    google = GoogleUsers()

    if not account.exists():
        click.echo(f"User does not exist: {account}")
        raise SystemExit(Result.FAILURE)

    if not force:
        cont = input(f"Reset password for {account}? (Y/n): ")
        if not cont.lower().startswith("y"):
            click.echo("Aborting password reset.")
            raise SystemExit(Result.SUCCESS)

    click.echo(f"User exists, resetting password: {account}")

    google.reset_password(account=account, notify=notify)

    # call the signout command
    ctx.forward(signout)
