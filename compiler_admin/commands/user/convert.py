import click

from compiler_admin import Result
from compiler_admin.services.google import (
    GROUP_PARTNERS,
    GROUP_STAFF,
    ORG_UNITS,
    OU_CONTRACTORS,
    OU_PARTNERS,
    OU_STAFF,
    add_user_to_group,
    move_user_ou,
    remove_user_from_group,
    user_account_name,
    user_exists,
    user_is_partner,
    user_is_staff,
)


@click.command()
@click.option("-f", "--force", is_flag=True, help="Don't ask for confirmation.")
@click.argument("username")
@click.argument("account_type", type=click.Choice(ORG_UNITS.keys(), case_sensitive=False))
@click.pass_context
def convert(ctx: click.Context, username: str, account_type: str, **kwargs):
    """Convert a user of one type to another."""
    account = user_account_name(username)

    if not user_exists(account):
        click.echo(f"User does not exist: {account}")
        raise SystemExit(Result.FAILURE)

    ou = ORG_UNITS[account_type]
    click.echo(f"User exists, converting to: {ou} for {account}")

    if ou == OU_CONTRACTORS:
        if user_is_partner(account):
            remove_user_from_group(account, GROUP_PARTNERS)
            remove_user_from_group(account, GROUP_STAFF)
        elif user_is_staff(account):
            remove_user_from_group(account, GROUP_STAFF)

    elif ou == OU_STAFF:
        if user_is_partner(account):
            remove_user_from_group(account, GROUP_PARTNERS)
        elif user_is_staff(account):
            click.echo(f"User is already staff: {account}")
            raise SystemExit(Result.FAILURE)
        add_user_to_group(account, GROUP_STAFF)

    elif ou == OU_PARTNERS:
        if user_is_partner(account):
            click.echo(f"User is already partner: {account}")
            raise SystemExit(Result.FAILURE)
        if not user_is_staff(account):
            add_user_to_group(account, GROUP_STAFF)
        add_user_to_group(account, GROUP_PARTNERS)

    move_user_ou(account, ou)

    click.echo(f"Account conversion complete for: {account}")
