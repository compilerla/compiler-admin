from tempfile import NamedTemporaryFile

import click

from compiler_admin import RESULT_FAILURE, RESULT_SUCCESS
from compiler_admin.commands.user.alumni import alumni
from compiler_admin.commands.user.delete import delete
from compiler_admin.services.google import (
    USER_ARCHIVE,
    CallGAMCommand,
    CallGYBCommand,
    user_account_name,
    user_exists,
)


@click.command()
@click.option("-a", "--alias", help="Another account to assign username as an alias.")
@click.option("-f", "--force", is_flag=True, help="Don't ask for confirmation.")
@click.option("-n", "--notify", help="An email address to send the new password notification.")
@click.argument("username")
@click.pass_context
def offboard(ctx: click.Context, username: str, alias: str = "", force: bool = False, **kwargs):
    """Fully offboard a user from Compiler.

    Args:
        username (str): The user account to offboard.

        alias (str): [Optional] account to assign username as an alias
    Returns:
        A value indicating if the operation succeeded or failed.
    """
    account = user_account_name(username)

    if not user_exists(account):
        click.echo(f"User does not exist: {account}")
        raise SystemExit(RESULT_FAILURE)

    alias_account = user_account_name(alias)
    if alias_account and not user_exists(alias_account):
        click.echo(f"Alias target user does not exist: {alias_account}")
        raise SystemExit(RESULT_FAILURE)

    if not force:
        cont = input(f"Offboard account {account} {' (assigning alias to ' + alias_account + ')' if alias else ''}? (Y/n): ")
        if not cont.lower().startswith("y"):
            click.echo("Aborting offboard.")
            raise SystemExit(RESULT_SUCCESS)

    click.echo(f"User exists, offboarding: {account}")

    # call the alumni command
    ctx.forward(alumni)

    click.echo("Backing up email")
    CallGYBCommand(("--service-account", "--email", account, "--action", "backup"))

    click.echo("Starting Drive and Calendar transfer")
    CallGAMCommand(("create", "transfer", account, "calendar,drive", USER_ARCHIVE, "all", "releaseresources"))

    status = ""
    with NamedTemporaryFile("w+") as stdout:
        while "Overall Transfer Status: completed" not in status:
            click.echo("Transfer in progress")
            CallGAMCommand(("show", "transfers", "olduser", username), stdout=stdout.name, stderr="stdout")
            status = " ".join(stdout.readlines())
            stdout.seek(0)

    CallGAMCommand(("user", account, "deprovision", "popimap"))

    # call the delete command
    ctx.forward(delete)

    if alias_account:
        click.echo(f"Adding an alias to account: {alias_account}")
        CallGAMCommand(("create", "alias", account, "user", alias_account))

    click.echo(f"Offboarding for user complete: {account}")
