import click

from compiler_admin import RESULT_FAILURE, RESULT_SUCCESS
from compiler_admin.commands.user.backupcodes import backupcodes
from compiler_admin.commands.user.reset import reset
from compiler_admin.services.google import (
    GROUP_STAFF,
    GROUP_TEAM,
    OU_CONTRACTORS,
    OU_STAFF,
    CallGAMCommand,
    add_user_to_group,
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
    help="An email address to use as the new recovery email.",
)
@click.option(
    "-p",
    "--recovery-phone",
    default="",
    help="A phone number to use as the new recovery phone number.",
)
@click.option("-s", "--staff", is_flag=True, help="Reactivate the user as a staff member. The default is contractor.")
@click.argument("username")
@click.pass_context
def reactivate(
    ctx: click.Context,
    username: str,
    force: bool = False,
    recovery_email: str = "",
    recovery_phone: str = "",
    staff: bool = False,
    **kwargs,
):
    """Reactivate a previously deactivated user."""
    account = user_account_name(username)

    if not user_exists(account):
        click.echo(f"User does not exist: {account}")
        raise SystemExit(RESULT_FAILURE)

    if not user_is_deactivated(account):
        click.echo("User is not deactivated, cannot reactivate")
        raise SystemExit(RESULT_FAILURE)

    if not force:
        cont = input(f"Reactivate account {account}? (Y/n): ")
        if not cont.lower().startswith("y"):
            click.echo("Aborting reactivation")
            raise SystemExit(RESULT_SUCCESS)

    click.echo(f"User exists, reactivating: {account}")

    click.echo(f"Adding to group: {GROUP_TEAM}")
    add_user_to_group(account, GROUP_TEAM)

    if staff:
        click.echo(f"Moving to OU: {OU_STAFF}")
        move_user_ou(account, OU_STAFF)
        click.echo(f"Adding to group: {GROUP_STAFF}")
        add_user_to_group(account, GROUP_STAFF)
    else:
        click.echo(f"Moving to OU: {OU_CONTRACTORS}")
        move_user_ou(account, OU_CONTRACTORS)

    # reset password, sign out
    ctx.forward(reset)

    click.echo("Update user profile info")
    profile = dict(recoveryemail=recovery_email, recoveryphone=recovery_phone)
    profile = {k: v for k, v in profile.items() if v}
    for prop, val in profile.items():
        command = ("update", "user", account, prop, val)
        CallGAMCommand(command)

    # get the user's backup codes
    ctx.forward(backupcodes)

    click.echo(f"User is reactivated: {account}")
