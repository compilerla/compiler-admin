import click

from compiler_admin import Result
from compiler_admin.commands.user.backupcodes import backupcodes
from compiler_admin.commands.user.reset import reset
from compiler_admin.services.google import GoogleAccount, GoogleGroups, GoogleOrgs, GoogleUsers


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
    account = GoogleAccount(username)

    if not account.exists():
        click.echo(f"User does not exist: {account}")
        raise SystemExit(Result.FAILURE)

    if not account.is_deactivated():
        click.echo("User is not deactivated, cannot reactivate")
        raise SystemExit(Result.FAILURE)

    if not force:
        cont = input(f"Reactivate account {account}? (Y/n): ")
        if not cont.lower().startswith("y"):
            click.echo("Aborting reactivation")
            raise SystemExit(Result.SUCCESS)

    click.echo(f"User exists, reactivating: {account}")

    click.echo(f"Adding to group: {GoogleGroups.GROUP_TEAM}")
    GoogleGroups(GoogleGroups.GROUP_TEAM).add_user(account)

    if staff:
        click.echo(f"Moving to OU: {GoogleOrgs.OU_STAFF}")
        GoogleOrgs(GoogleOrgs.OU_STAFF).move_user(account)
        click.echo(f"Adding to group: {GoogleGroups.GROUP_STAFF}")
        GoogleGroups(GoogleGroups.GROUP_STAFF).add_user(account)
    else:
        click.echo(f"Moving to OU: {GoogleOrgs.OU_CONTRACTORS}")
        GoogleOrgs(GoogleOrgs.OU_CONTRACTORS).move_user(account)

    # reset password, sign out
    ctx.forward(reset)

    click.echo("Update user profile info")
    GoogleUsers().reset_recovery_info(account=account, recovery_email=recovery_email, recovery_phone=recovery_phone)

    # get the user's backup codes
    ctx.forward(backupcodes)

    click.echo(f"User is reactivated: {account}")
