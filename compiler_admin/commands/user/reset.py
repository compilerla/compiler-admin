import click

from compiler_admin import RESULT_FAILURE, RESULT_SUCCESS
from compiler_admin.commands.user.signout import signout
from compiler_admin.services.google import USER_HELLO, CallGAMCommand, user_account_name, user_exists


@click.command()
@click.option("-f", "--force", is_flag=True, help="Don't ask for confirmation.")
@click.option("-n", "--notify", help="An email address to send the new password notification.")
@click.argument("username")
@click.pass_context
def reset(ctx: click.Context, username: str, force: bool = False, notify: str = "", **kwargs):
    """
    Reset a user's password.
    """
    account = user_account_name(username)

    if not user_exists(account):
        click.echo(f"User does not exist: {account}")
        raise SystemExit(RESULT_FAILURE)

    if not force:
        cont = input(f"Reset password for {account}? (Y/n): ")
        if not cont.lower().startswith("y"):
            click.echo("Aborting password reset.")
            raise SystemExit(RESULT_SUCCESS)

    click.echo(f"User exists, resetting password: {account}")

    command = ("update", "user", account, "password", "random", "changepassword")
    if notify:
        command += ("notify", notify, "from", USER_HELLO)

    CallGAMCommand(command)

    # call the signout command
    ctx.forward(signout)
