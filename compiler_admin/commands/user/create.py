import click

from compiler_admin import RESULT_FAILURE
from compiler_admin.services.google import (
    GROUP_TEAM,
    USER_HELLO,
    add_user_to_group,
    CallGAMCommand,
    user_account_name,
    user_exists,
)


@click.command(context_settings={"ignore_unknown_options": True})
@click.option("-n", "--notify", help="An email address to send the new password notification.")
@click.argument("username")
@click.argument("gam_args", nargs=-1, type=click.UNPROCESSED)
def create(username: str, notify: str = "", gam_args: list = []):
    """Create a new user account.

    The user's password is randomly generated and requires reset on first login.

    Extra args are passed along to GAM as options.

    https://github.com/taers232c/GAMADV-XTD3/wiki/Users#create-a-user
    """
    account = user_account_name(username)

    if user_exists(account):
        click.echo(f"User already exists: {account}")
        raise SystemExit(RESULT_FAILURE)

    click.echo(f"User does not exist, continuing: {account}")

    command = ("create", "user", account, "password", "random", "changepassword")

    if notify:
        command += ("notify", notify, "from", USER_HELLO)

    command += (*gam_args,)

    CallGAMCommand(command)

    add_user_to_group(account, GROUP_TEAM)

    click.echo(f"User created successfully: {account}")
