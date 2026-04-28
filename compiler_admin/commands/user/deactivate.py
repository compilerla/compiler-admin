import click

from compiler_admin import Result
from compiler_admin.commands.user.reset import reset
from compiler_admin.services.google import GoogleAccount, GoogleOrgs, GoogleUsers


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
    """Deactivate (but do not delete) a user."""
    account = GoogleAccount(username)
    google_users = GoogleUsers()
    google_orgs = GoogleOrgs()

    if not account.exists():
        click.echo(f"User does not exist: {account}")
        raise SystemExit(Result.FAILURE)

    if account.is_deactivated():
        click.echo("User is already deactivated")
        raise SystemExit(Result.FAILURE)

    if not force:
        cont = input(f"Deactivate account {account}? (Y/n): ")
        if not cont.lower().startswith("y"):
            click.echo("Aborting deactivation")
            raise SystemExit(Result.SUCCESS)

    click.echo(f"User exists, deactivating: {account}")

    click.echo(f"Moving to OU: {GoogleOrgs.OU_ALUMNI}")
    google_orgs.move_user(account, GoogleOrgs.OU_ALUMNI)

    click.echo("Removing from groups")
    google_users.remove_from_groups(account)

    # reset password, sign out
    ctx.forward(reset)

    click.echo("Clearing user profile info")
    google_users.clear_profile(account)

    click.echo("Resetting recovery email and phone")
    google_users.reset_recovery_info(account=account, recovery_email=recovery_email, recovery_phone=recovery_phone)

    click.echo("Turning off 2FA")
    google_users.disable_2fa(account)

    click.echo(f"User is deactivated: {account}")
