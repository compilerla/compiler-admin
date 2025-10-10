import click

from compiler_admin import RESULT_FAILURE, RESULT_SUCCESS
from compiler_admin.commands.user.reset import reset
from compiler_admin.services.google import (
    OU_ALUMNI,
    CallGAMCommand,
    move_user_ou,
    user_account_name,
    user_exists,
    user_is_deactivated,
)


@click.command()
@click.option("-f", "--force", is_flag=True, help="Don't ask for confirmation.")
@click.option("-n", "--notify", help="An email address to send the new password notification.")
@click.option(
    "-e",
    "--recovery-email",
    default="",
    help="An email address to use as the new recovery email. Without a value, clears the recovery email.",
)
@click.option(
    "-p",
    "--recovery-phone",
    default="",
    help="A phone number to use as the new recovery phone number. Without a value, clears the recovery phone number.",
)
@click.argument("username")
@click.pass_context
def deactivate(
    ctx: click.Context, username: str, force: bool = False, recovery_email: str = "", recovery_phone: str = "", **kwargs
):
    """
    Deactivate (but do not delete) a user.
    """
    account = user_account_name(username)

    if not user_exists(account):
        click.echo(f"User does not exist: {account}")
        raise SystemExit(RESULT_FAILURE)

    if user_is_deactivated(account):
        click.echo("User is already deactivated")
        raise SystemExit(RESULT_FAILURE)

    if not force:
        cont = input(f"Deactivate account {account}? (Y/n): ")
        if not cont.lower().startswith("y"):
            click.echo("Aborting deactivation")
            raise SystemExit(RESULT_SUCCESS)

    click.echo(f"User exists, deactivating: {account}")

    click.echo("Removing from groups")
    CallGAMCommand(("user", account, "delete", "groups"))

    click.echo(f"Moving to OU: {OU_ALUMNI}")
    move_user_ou(account, OU_ALUMNI)

    # reset password, sign out
    ctx.forward(reset)

    click.echo("Clearing user profile info")
    for prop in ["address", "location", "otheremail", "phone"]:
        command = ("update", "user", account, prop, "clear")
        CallGAMCommand(command)

    click.echo("Resetting recovery email")
    command = ("update", "user", account, "recoveryemail", recovery_email)
    CallGAMCommand(command)

    click.echo("Resetting recovery phone")
    command = ("update", "user", account, "recoveryphone", recovery_phone)
    CallGAMCommand(command)

    click.echo("Turning off 2FA")
    command = ("user", account, "turnoff2sv")
    CallGAMCommand(command)

    click.echo(f"User is deactivated: {account}")
