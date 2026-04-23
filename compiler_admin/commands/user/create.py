import click

from compiler_admin import Result
from compiler_admin.services.google import GoogleAccount, GoogleGroups, GoogleUsers


@click.command(context_settings={"ignore_unknown_options": True})
@click.option("-n", "--notify", help="An email address to send the new password notification.")
@click.argument("username")
@click.argument("gam_args", nargs=-1, type=click.UNPROCESSED)
def create(username: str, notify: str = "", gam_args: list = []):
    """Create a new user account.

    The user's password is randomly generated and requires reset on first login.

    Extra args are passed along to GAM as options.

    <https://github.com/GAM-team/GAM/wiki/Users#create-a-user>
    """
    account = GoogleAccount(username)

    if account.exists():
        click.echo(f"User already exists: {account}")
        raise SystemExit(Result.FAILURE)

    click.echo(f"User does not exist, continuing: {account}")

    GoogleUsers().create(account, notify, *gam_args)
    GoogleGroups(GoogleGroups.GROUP_TEAM).add_user(account)

    click.echo(f"User created successfully: {account}")
